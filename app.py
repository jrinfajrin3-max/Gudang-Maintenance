import streamlit as st
import pandas as pd
import os
from datetime import date
import base64
import time # Tambahkan library time untuk jeda

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Control Parts Maintenance", layout="wide")

# ==========================================
# FUNGSI CSS & GAMBAR
# ==========================================
def set_futuristic_style():
    """Mengatur tema CSS: Dark mode, neon accents, white sidebar"""
    
    style = f'''
    <style>
    /* Mengatur Background Halaman Utama */
    .stApp {{
        background-color: #0e1117; /* Dark background */
        color: #ffffff;
    }}
    
    /* SIDEBAR TETAP PUTIH */
    [data-testid="stSidebar"] {{
        background-image: none;
        background-color: #ffffff; 
    }}
    [data-testid="stSidebar"]::before {{
        display: none;
    }}
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h3 {{
        color: #000000 !important;
    }}
    
    .block-container {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: 30px;
        color: #00f2fe; /* Neon Cyan */
        font-weight: bold;
    }}
    
    h1, h2, h3, h4, p, label {{
        color: #ffffff !important;
    }}
    
    [data-testid="stDataFrame"] {{
        border: 1px solid #333333;
    }}
    
    /* CSS UNTUK TULISAN KONFIRMASI BESAR */
    .big-font {{
        font-size:30px !important;
        font-weight: bold;
        text-align: center;
        color: #00ff00; /* Hijau neon */
        padding: 20px;
        border: 2px solid #00ff00;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

set_futuristic_style()

# ==========================================
# KONFIGURASI DATABASE
# ==========================================
FILE_DATA = "data_gudang.csv"

def muat_data():
    if os.path.exists(FILE_DATA):
        df = pd.read_csv(FILE_DATA)
        df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
        return df
    else:
        return pd.DataFrame(columns=['ID', 'Nama Barang', 'Kategori', 'Status', 'Stok', 
                                   'Min_Stok', 'Line Produksi', 'PIC', 'Jadwal Jatuh Tempo', 'Lokasi Rak'])

df = muat_data()
list_line = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]
list_status = ["New", "Repairable", "Refurbished", "Scrap"]

# ==========================================
# SIDEBAR - PENCARIAN & MENU
# ==========================================
with st.sidebar:
    # --- LOGO TOYOTA ---
    if os.path.exists("logo_toyota.png"):
        with open("logo_toyota.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(
                f'<div style="text-align: center; margin-top: -20px;"><img src="data:image/png;base64,{encoded_string}" width="200"></div>',
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # --- FITUR PENCARIAN ---
    st.subheader("🔍 Cari Sparepart")
    search_term = st.text_input("Nama barang...", placeholder="Contoh: Bearing")
    st.markdown("---")
    
    # --- MENU NAVIGATION ---
    app_mode = st.radio(
        "Mode Tampilan Utama:",
        ["Dashboard Utama", "Update Gudang"]
    )
    st.info("Sistem Manajemen Sparepart Maintenance")

# ==========================================
# TAMPILAN UTAMA
# ==========================================

# --- LOGIKA PENCARIAN (Filtering Data) ---
df_filtered = df.copy()
if search_term:
    df_filtered = df_filtered[df_filtered['Nama Barang'].str.contains(search_term, case=False, na=False)]

# --- MODE: DASHBOARD ---
if app_mode == "Dashboard Utama":
    
    # KONDISI: JIKA ADA PENCARIAN, TAMPILKAN HANYA HASIL PENCARIAN
    if search_term:
        st.title("🔎 Hasil Pencarian")
        
        if not df_filtered.empty:
            # Kolom untuk Data Inventaris
            st.write("📦 **Data Inventaris**")
            st.dataframe(df_filtered[['Nama Barang', 'Stok', 'Lokasi Rak']], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Kolom untuk Pengambilan Barang
            st.write("🛠️ **Pengambilan Barang**")
            with st.form("take_form_search"):
                item_list = df_filtered['Nama Barang'].unique().tolist()
                selected_item = st.selectbox("Pilih Barang", item_list)
                qty_out = st.number_input("Jumlah Diambil", min_value=1)
                status_bekas = st.selectbox("Status Barang yang Dilepas", ["New", "Repairable", "Scrap"])
                
                take_btn = st.form_submit_button("Ambil & Proses")
                
                if take_btn:
                    current_stock = df.loc[df['Nama Barang'] == selected_item, 'Stok'].values[0]
                    if qty_out <= current_stock:
                        df.loc[df['Nama Barang'] == selected_item, 'Stok'] -= qty_out
                        df.to_csv(FILE_DATA, index=False)
                        
                        # --- KONFIRMASI PENGAMBILAN (Besar di Tengah) ---
                        st.markdown(f'<p class="big-font">✅ BERHASIL MENGAMBIL {qty_out} PCS {selected_item.upper()}!</p>', unsafe_allow_html=True)
                        time.sleep(2) # Beri jeda 2 detik agar terbaca
                        
                        if status_bekas == "Repairable":
                            st.warning(f"Barang {selected_item} dikirim ke workshop untuk repair.")
                        st.rerun()
                    else:
                        st.error("❌ Stok tidak cukup!")
        else:
            st.warning("Barang tidak ditemukan.")

    # KONDISI: JIKA TIDAK ADA PENCARIAN, TAMPILKAN DASHBOARD NORMAL
    else:
        st.title("📊 Control Parts Maintenance Dashboard")
        
        if not df.empty:
            today = date.today()
            current_month = today.month
            current_year = today.year
            
            due_items = df[
                (pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.month == current_month) &
                (pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.year == current_year) &
                (df['Status'] != 'Scrap')
            ]
            
            # KPI Cards
            st.subheader("Ringkasan")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            total_items = len(df[df['Status'] != 'Scrap'])
            low_stock = len(df[(df['Stok'] <= df['Min_Stok']) & (df['Status'] != 'Scrap')])
            
            kpi1.metric("Total Item Aktif", total_items)
            kpi2.metric("⚠️ Perlu Restock", low_stock)
            kpi3.metric("📅 Jatuh Tempo", len(due_items))
            kpi4.metric("Line Terpantau", len(list_line))

            st.markdown("---")
            
            # 1. INDIKATOR LINE PRODUKSI
            st.subheader("Acuan Jadwal & Pengolahan Produksi")
            num_lines = len(list_line)
            cols = st.columns(num_lines)
            for i, line in enumerate(list_line):
                items_due_line = len(due_items[due_items['Line Produksi'] == line])
                with cols[i]:
                    if items_due_line > 0:
                        st.error(f"**{line}**\n\n⚠️ **{items_due_line}** Jatuh Tempo")
                    else:
                        st.success(f"**{line}**\n\n✅ Aman")

            st.markdown("---")
            
            # 2. TABEL BARANG (Semua)
            st.subheader("Daftar Inventaris Lengkap")
            st.dataframe(df[['Nama Barang', 'Status', 'Stok', 'Line Produksi', 'Jadwal Jatuh Tempo', 'Lokasi Rak']], use_container_width=True)
                
        else:
            st.warning("Data kosong. Silakan input data di menu Update Gudang.")

# --- MODE: UPDATE ---
elif app_mode == "Update Gudang":
    st.title("📥 Update Gudang / Workshop")
    
    with st.form("input_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            nama = st.text_input("Nama Sparepart")
            line = st.selectbox("Line Produksi", list_line)
            qty = st.number_input("Jumlah", min_value=1)
            jadwal_tgl = st.date_input("Jadwal Jatuh Tempo", date.today())
            
        with col_b:
            status = st.selectbox("Status", list_status)
            pic = st.text_input("PIC Mesin")
            lokasi = st.text_input("Lokasi Rak/Workshop")
            min_stok = st.number_input("Min Stok", min_value=0, value=5)
            
        submitted = st.form_submit_button("Update Inventaris")
        
        if submitted:
            if nama in df['Nama Barang'].values:
                df.loc[df['Nama Barang'] == nama, 'Stok'] += qty
                df.loc[df['Nama Barang'] == nama, 'Status'] = status
                df.loc[df['Nama Barang'] == nama, 'Line Produksi'] = line
                df.loc[df['Nama Barang'] == nama, 'Jadwal Jatuh Tempo'] = jadwal_tgl
                df.loc[df['Nama Barang'] == nama, 'PIC'] = pic
                df.loc[df['Nama Barang'] == nama, 'Lokasi Rak'] = lokasi
            else:
                new_data = pd.DataFrame([[len(df)+1, nama, "Mechanical", status, qty, min_stok, line, pic, jadwal_tgl, lokasi]], columns=df.columns)
                df = pd.concat([df, new_data], ignore_index=True)
            
            df.to_csv(FILE_DATA, index=False)
            
            # --- KONFIRMASI UPDATE (Besar di Tengah) ---
            st.markdown(f'<p class="big-font">✅ DATA {nama.upper()} BERHASIL DIPERBARUI!</p>', unsafe_allow_html=True)
            time.sleep(2) # Beri jeda 2 detik
            
            # Tunggu sebentar lalu refresh
            st.rerun()
