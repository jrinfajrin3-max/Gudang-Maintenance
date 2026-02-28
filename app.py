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
        padding-top: 0.5rem !important;
    }
    
    /* Warna Teks Sidebar Jadi Hitam agar Terbaca */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    
    /* Tombol Navigasi Merah Toyota */
    div.stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
    }
    
    /* Mengatur Jarak Konten Utama agar Rapi */
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
            # Konversi kolom tanggal agar bisa diolah
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

# Muat data ke dalam variabel df
df = muat_data()

# ==========================================
# 4. SIDEBAR (Logo, Navigasi, Jam)
# ==========================================
with st.sidebar:
    # Logo Toyota Indonesia
    st.markdown("<h1 style='text-align: center; color: #ff0000; margin-bottom: 0;'>TOYOTA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: black; margin-top: -10px; font-weight: bold;'>INDONESIA</p>", unsafe_allow_html=True)
    
    # --- TEMPAT JAM OTOMATIS (Placeholder) ---
    container_jam = st.empty()
    
    st.markdown("---")
    
    # Inisialisasi halaman di session state
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
    
    # Pencarian Cepat
    st.markdown("### 🔍 Cari Sparepart")
    search_query = st.text_input("Cari...", placeholder="Ketik nama part/mesin", label_visibility="collapsed")

# ==========================================
# 5. LOGIKA HALAMAN UTAMA
# ==========================================

# 5A. JIKA USER SEDANG MENCARI SESUATU
if search_query:
    st.title("🔍 Hasil Pencarian")
    results = df[
        df['Nama Part'].str.contains(search_query, case=False, na=False) |
        df['Nama Mesin'].str.contains(search_query, case=False, na=False)
    ]
    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("Data tidak ditemukan.")

# 5B. HALAMAN DASHBOARD MONITORING
elif st.session_state.page == "Dashboard":
    st.title("📊 Maindashboard Monitoring")
    
    today = datetime.now().date()
    
    # Metrik Atas (FIXED: Menggunakan Status TPM, bukan Status TPN)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", len(df))
    c2.metric("Perlu Ganti (Delay)", len(df[df['Jadwal Jatuh Tempo'] <= today]))
    c3.metric("Selesai TPM", len(df[df['Status TPM'] == 'Finish']))
    
    st.markdown("---")
    
    # Tabel Progress per Line
    st.subheader("🚧 Progress TPM per Line Produksi")
    col_l = st.columns(2)
    for i, line in enumerate(list_line):
        with col_l[i % 2]:
            df_line = df[df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_line.empty:
                done = len(df_line[df_line['Status TPM'] == 'Finish'])
                total = len(df_line)
                st.progress(done / total)
                st.caption(f"{done} dari {total} part selesai.")
            else:
                st.caption("Belum ada data di line ini.")

# 5C. HALAMAN UPDATE PENGGANTIAN
elif st.session_state.page == "Update":
    st.title("🛠️ Update Penggantian Part")
    with st.form("form_update"):
        pilih_part = st.selectbox("Pilih Mesin | Part", (df['Nama Mesin'] + " | " + df['Nama Part']).tolist())
        tgl_baru = st.date_input("Tanggal Penggantian", datetime.now())
        pic_update = st.text_input("PIC Eksekutor")
        
        if st.form_submit_button("Konfirmasi Update"):
            # Cari baris data berdasarkan pilihan
            idx = df[df['Nama Mesin'] + " | " + df['Nama Part'] == pilih_part].index[0]
            rentang = df.at[idx, 'Rentang Waktu (Bulan)']
            
            # Update data
            df.at[idx, 'Tanggal Terakhir Ganti'] = tgl_baru
            df.at[idx, 'Jadwal Jatuh Tempo'] = tgl_baru + relativedelta(months=int(rentang))
            df.at[idx, 'Status TPM'] = 'Finish'
            df.at[idx, 'PIC'] = pic_update
            
            df.to_csv(FILE_DATA, index=False)
            st.success("Data Berhasil Diupdate!")
            st.rerun()

# 5D. HALAMAN MASTER DATA (TAMPILAN EDITOR)
elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    st.markdown("Edit data langsung pada tabel di bawah ini untuk menambah atau menghapus part.")
    
    # Editor Data Interaktif
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if st.button("Simpan Semua Perubahan Master"):
        edited_df.to_csv(FILE_DATA, index=False)
        st.success("Master data berhasil diperbarui!")
        st.rerun()

# ==========================================
# 6. LOGIKA JAM REAL-TIME (UPDATE OTOMATIS)
# ==========================================
# Bagian ini akan terus berjalan untuk mengupdate jam setiap detik
while True:
    skrg = datetime.now()
    tgl_display = skrg.strftime("%A, %d %B %Y")
    jam_display = skrg.strftime("%H:%M:%S")
    
    # Update Jam di Sidebar secara rapi
    container_jam.markdown(f"""
        <div style="text-align: center; border: 2px solid #f0f2f6; border-radius: 10px; padding: 10px; background-color: #f8f9fa;">
            <p style="font-size: 1rem; font-weight: bold; color: #555; margin-bottom: 0;">{tgl_display}</p>
            <h1 style="font-size: 2.8rem; margin-top: -5px; color: #000000; font-family: 'Courier New', Courier, monospace;">{jam_display}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1) # Tunggu 1 detik sebelum update berikutnya
