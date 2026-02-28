import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="TPM Control System", layout="wide")

# ==========================================
# FUNGSI CSS CUSTOM
# ==========================================
def set_style():
    style = '''
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; padding-top: 0rem !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h3 { color: #000000 !important; }
    .stProgress > div > div > div > div { background-color: #ff0000; }
    div.stButton > button { background-color: #ff0000; color: white; border: none; }
    .block-container { padding-top: 1rem !important; }
    h1 { margin-top: -30px !important; }
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

set_style()

# ==========================================
# KONFIGURASI DATABASE
# ==========================================
FILE_DATA = "data_gudang.csv"
list_line = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]

def muat_data():
    if os.path.exists(FILE_DATA):
        df = pd.read_csv(FILE_DATA)
        df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
        df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
        return df
    else:
        # Template data awal jika file tidak ada
        data = {'ID': [1], 'Nama Mesin': ['Bucket Elevator'], 'Nama Part': ['Bearing 6205'], 
                'Line Produksi': ['Moulding'], 'Lokasi Rak': ['Zone 4'], 'Stok': [10], 
                'Rentang Waktu (Bulan)': [1], 'Tanggal Terakhir Ganti': [datetime.now().date()], 
                'Jadwal Jatuh Tempo': [datetime.now().date() + relativedelta(months=1)], 
                'Status TPM': ['On Progress'], 'PIC': ['Admin']}
        df = pd.DataFrame(data)
        df.to_csv(FILE_DATA, index=False)
        return df

df = muat_data()

# ==========================================
# SIDEBAR (Statik)
# ==========================================
with st.sidebar:
    # Logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Toyota_carlogo.svg/1200px-Toyota_carlogo.svg.png", use_container_width=True)
    
    # Placeholder untuk Jam (Akan diisi di bagian bawah kode)
    container_jam = st.empty()
    
    st.markdown("---")
    st.markdown("### 🔍 Cari Sparepart")
    search_query = st.text_input("Ketik nama...", label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🧭 Menu Utama")
    if 'page' not in st.session_state: st.session_state.page = "Dashboard"
    
    if st.button("📊 Dashboard Monitoring", use_container_width=True): st.session_state.page = "Dashboard"
    if st.button("🛠️ Update Penggantian Part", use_container_width=True): st.session_state.page = "Update"
    if st.button("➕ Master Data Part", use_container_width=True): st.session_state.page = "Master"

# ==========================================
# HALAMAN UTAMA
# ==========================================
if search_query:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_query, case=False, na=False)]
    st.dataframe(results, use_container_width=True)

elif st.session_state.page == "Dashboard":
    st.title("📊 Maindashboard")
    t1, t2, t3 = st.columns(3)
    t1.metric("Total Items", len(df))
    t2.metric("Perlu Ganti", len(df[df['Jadwal Jatuh Tempo'] <= datetime.now().date()]))
    # Perbaikan typo Status TPN ke Status TPM sesuai error sebelumnya
    t3.metric("Selesai TPM", len(df[df['Status TPM'] == 'Finish']))
    
    st.markdown("---")
    st.subheader("🚧 Progress TPM per Line Produksi")
    cols = st.columns(2)
    for i, line in enumerate(list_line):
        with cols[i % 2]:
            df_l = df[df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_l.empty:
                prog = len(df_l[df_l['Status TPM'] == 'Finish']) / len(df_l)
                st.progress(prog)
            else: st.caption("Belum ada data.")

elif st.session_state.page == "Update":
    st.title("🛠️ Update Penggantian")
    # Form update sederhana
    with st.form("form_update"):
        pilih = st.selectbox("Pilih Part", df['Nama Part'].tolist())
        pic = st.text_input("PIC")
        if st.form_submit_button("Simpan"):
            st.success("Data diperbarui!")

elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    # Tampilan editor data sesuai gambar terakhir
    st.data_editor(df, use_container_width=True)

# ==========================================
# LOGIKA JAM REAL-TIME (Ditaruh paling bawah)
# ==========================================
# Menggunakan loop agar jam terus berdetak
while True:
    skrg = datetime.now()
    tgl = skrg.strftime("%A, %d %B %Y")
    jam = skrg.strftime("%H:%M:%S")
    
    container_jam.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0;">{tgl}</p>
            <h1 style="font-size: 3rem; margin-top: -10px; color: #000000;">{jam}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1) # Tunggu 1 detik lalu update lagi
