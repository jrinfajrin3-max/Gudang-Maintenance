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
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Putih */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        padding-top: 0.5rem !important;
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
    }
    
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
# 4. SIDEBAR (Navigasi & Pencarian)
# ==========================================
with st.sidebar:
    # Logo Cadangan jika file tidak ada
    st.markdown("<h1 style='text-align: center; color: #ff0000; margin-bottom: 0;'>TOYOTA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: black; margin-top: -10px;'>INDONESIA</p>", unsafe_allow_html=True)
    
    # PLACEHOLDER JAM (PENTING: Diupdate di akhir kode)
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
    search_query = st.text_input("Cari...", placeholder="Nama part/mesin", label_visibility="collapsed")

# ==========================================
# 5. HALAMAN UTAMA
# ==========================================

if search_query:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_query, case=False, na=False)]
    st.dataframe(results, use_container_width=True)

elif st.session_state.page == "Dashboard":
    st.title("📊 Maindashboard Monitoring")
    
    today = datetime.now().date()
    
    # Metrik (FIXED: Status TPM bukan Status TPN)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", len(df))
    c2.metric("Perlu Ganti (Delay)", len(df[df['Jadwal Jatuh Tempo'] <= today]))
    c3.metric("Selesai TPM", len(df[df['Status TPM'] == 'Finish']))
    
    st.markdown("---")
    st.subheader("🚧 Progress TPM per Line Produksi")
    cols = st.columns(2)
    for i, line in enumerate(list_line):
        with cols[i % 2]:
            df_line = df[df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_line.empty:
                done = len(df_line[df_line['Status TPM'] == 'Finish'])
                st.progress(done / len(df_line))
            else:
                st.caption("Data kosong.")

elif st.session_state.page == "Update":
    st.title("🛠️ Form Update Penggantian")
    with st.form("update_form"):
        pilih = st.selectbox("Pilih Part", df['Nama Part'].tolist())
        pic_input = st.text_input("PIC Eksekutor")
        if st.form_submit_button("Submit"):
            st.success("Data berhasil diupdate!")

elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

# ==========================================
# 6. LOGIKA JAM REAL-TIME (Detik Berjalan)
# ==========================================
while True:
    now = datetime.now()
    tgl_display = now.strftime("%A, %d %B %Y")
    jam_display = now.strftime("%H:%M:%S")
    
    # Update hanya bagian jam di sidebar
    container_jam.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0;">{tgl_display}</p>
            <h1 style="font-size: 3rem; margin-top: -10px; color: #000000;">{jam_display}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1)
