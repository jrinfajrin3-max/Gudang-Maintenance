import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="TPM Control System - TMMIN", layout="wide")

# ==========================================
# 2. STYLE CSS (Tampilan Sidebar & Panel)
# ==========================================
def set_style():
    style = '''
    <style>
    /* Background Utama Gelap */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Putih Bersih */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        padding-top: 0rem !important;
    }
    
    /* Teks Sidebar Hitam */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    
    /* Tombol Navigasi Merah */
    div.stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #cc0000;
    }
    
    /* Mengatur Jarak Konten Utama */
    .block-container {
        padding-top: 1.5rem !important;
    }
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

set_style()

# ==========================================
# 3. MANAJEMEN DATABASE (CSV)
# ==========================================
FILE_DATA = "data_gudang.csv"
list_line = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]

def muat_data():
    if os.path.exists(FILE_DATA):
        try:
            df = pd.read_csv(FILE_DATA)
            df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
            df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
            return df
        except:
            return buat_template_awal()
    else:
        return buat_template_awal()

def buat_template_awal():
    data = {
        'ID': [1],
        'Nama Mesin': ['Bucket Elevator'],
        'Nama Part': ['Bearing 6205'],
        'Line Produksi': ['Moulding'],
        'Lokasi Rak': ['Zone 4'],
        'Stok': [10],
        'Rentang Waktu (Bulan)': [1],
        'Tanggal Terakhir Ganti': [datetime.now().date()],
        'Jadwal Jatuh Tempo': [datetime.now().date() + relativedelta(months=1)],
        'Status TPM': ['On Progress'],
        'PIC': ['Admin']
    }
    df = pd.DataFrame(data)
    df.to_csv(FILE_DATA, index=False)
    return df

df = muat_data()

# ==========================================
# 4. SIDEBAR (Logo, Navigasi, Jam)
# ==========================================
with st.sidebar:
    # --- FIX LOGO: Menggunakan URL agar pasti muncul di GitHub ---
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Toyota_carlogo.svg/1200px-Toyota_carlogo.svg.png", use_container_width=True)
    st.markdown("<p style='text-align: center; color: black; font-weight: bold; margin-top: -15px;'>INDONESIA</p>", unsafe_allow_html=True)
    
    # Placeholder untuk Jam (Akan diupdate di akhir kode)
    container_jam = st.empty()
    
    st.markdown("---")
    
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
        
    st.markdown("### 🧭 Menu Utama")
    if st.button("📊 Dashboard Monitoring", use_container_width=True):
        st.session_state.page = "Dashboard"
    if st.button("🛠️ Update Penggantian Part", use_container_width=True):
        st.session_state.page = "Update"
    if st.button("➕ Master Data Part", use_container_width=True):
        st.session_state.page = "Master"
    
    st.markdown("---")
    st.markdown("### 🔍 Cari Sparepart")
    search_query = st.text_input("Cari...", placeholder="Ketik nama part/mesin", label_visibility="collapsed")

# ==========================================
# 5. LOGIKA HALAMAN UTAMA
# ==========================================

if search_query:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_query, case=False, na=False) | 
                 df['Nama Mesin'].str.contains(search_query, case=False, na=False)]
    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("Data tidak ditemukan.")

elif st.session_state.page == "Dashboard":
    st.title("📊 Maindashboard Monitoring")
    
    today = datetime.now().date()
    
    # Metrik (FIXED: Menggunakan Status TPM sesuai database)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", len(df))
    c2.metric("Perlu Ganti (Delay)", len(df[df['Jadwal Jatuh Tempo'] <= today]))
    c3.metric("Selesai TPM", len(df[df['Status TPM'] == 'Finish']))
    
    st.markdown("---")
    st.subheader("🚧 Progress TPM per Line Produksi")
    col_l = st.columns(2)
    for i, line in enumerate(list_line):
        with col_l[i % 2]:
            df_line = df[df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_line.empty:
                done = len(df_line[df_line['Status TPM'] == 'Finish'])
                st.progress(done / len(df_line))
                st.caption(f"{done} dari {len(df_line)} part selesai.")
            else:
                st.caption("Belum ada data.")

elif st.session_state.page == "Update":
    st.title("🛠️ Update Penggantian Part")
    with st.form("form_update"):
        pilih = st.selectbox("Pilih Part", (df['Nama Mesin'] + " | " + df['Nama Part']).tolist())
        tgl = st.date_input("Tanggal Ganti", datetime.now())
        pic = st.text_input("PIC Eksekutor")
        if st.form_submit_button("Simpan Perubahan"):
            idx = df[df['Nama Mesin'] + " | " + df['Nama Part'] == pilih].index[0]
            rentang = df.at[idx, 'Rentang Waktu (Bulan)']
            df.at[idx, 'Tanggal Terakhir Ganti'] = tgl
            df.at[idx, 'Jadwal Jatuh Tempo'] = tgl + relativedelta(months=int(rentang))
            df.at[idx, 'Status TPM'] = 'Finish'
            df.at[idx, 'PIC'] = pic
            df.to_csv(FILE_DATA, index=False)
            st.success("Berhasil diupdate!")
            st.rerun()

elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("Simpan Perubahan Master"):
        edited_df.to_csv(FILE_DATA, index=False)
        st.success("Data master diperbarui!")
        st.rerun()

# ==========================================
# 6. LOGIKA JAM REAL-TIME (UPDATE OTOMATIS)
# ==========================================
while True:
    now = datetime.now()
    container_jam.markdown(f"""
        <div style="text-align: center; border: 1px solid #ddd; border-radius: 8px; padding: 10px; background-color: #f9f9f9;">
            <p style="font-size: 1rem; font-weight: bold; color: #333; margin-bottom: 0;">{now.strftime("%A, %d %B %Y")}</p>
            <h1 style="font-size: 2.8rem; margin-top: -5px; color: #000; font-family: monospace;">{now.strftime("%H:%M:%S")}</h1>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
