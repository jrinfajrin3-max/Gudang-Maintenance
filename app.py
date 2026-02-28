import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="TPM Control System", layout="wide")

def local_css():
    st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; color: #000000 !important; }
    [data-testid="stSidebar"] * { color: #000000 !important; }
    div.stButton > button { background-color: #ff0000; color: white; width: 100%; border-radius: 5px; }
    .clock-box { text-align: center; border: 1.5px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)
local_css()

# ==========================================
# 2. MANAJEMEN DATA (CSV)
# ==========================================
DB_FILE = "data_gudang.csv"
LINE_LIST = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
        df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
        return df
    else:
        # Template data jika CSV belum ada
        data = {'ID': [1], 'Nama Mesin': ['Contoh Mesin'], 'Nama Part': ['Contoh Part'], 
                'Line Produksi': ['Moulding'], 'Lokasi Rak': ['Zone 1'], 'Stok': [10], 
                'Rentang Waktu (Bulan)': [1], 'Tanggal Terakhir Ganti': [datetime.now().date()], 
                'Jadwal Jatuh Tempo': [datetime.now().date()], 'Status TPM': ['On Progress'], 'PIC': ['Admin']}
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
        return df

df = load_data()

# ==========================================
# 3. SIDEBAR & LOGIKA NAVIGASI
# ==========================================
with st.sidebar:
    if os.path.exists("logo_toyota.png"):
        st.image("logo_toyota.png", use_container_width=True)
    
    # --- TEMPAT JAM WIB ---
    clock_placeholder = st.empty()
    
    st.markdown("---")
    
    # Inisialisasi Session State Halaman agar tidak berubah-ubah
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    st.markdown("### 🧭 Menu Utama")
    if st.button("📊 Dashboard Monitoring"):
        st.session_state.current_page = "Dashboard"
    if st.button("🛠️ Update Penggantian Part"):
        st.session_state.current_page = "Update"
    if st.button("➕ Master Data Part"):
        st.session_state.current_page = "Master"
    
    st.markdown("---")
    st.markdown("### 🔍 Cari Sparepart")
    search_term = st.text_input("Ketik nama part...", label_visibility="collapsed")

# ==========================================
# 4. FUNGSI HALAMAN (DIPISAH)
# ==========================================

def show_dashboard(data_df):
    st.title("📊 Maindashboard Monitoring")
    # Tampilan Dashboard...
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(data_df))
    st.write("Progress Monitoring...")

def show_update(data_df):
    st.title("🛠️ Update Penggantian Part")
    # Form Update...
    st.write("Update Status Sparepart...")

def show_master(data_df):
    st.title("➕ Master Data Part")
    # Editor Master Data...
    edited_df = st.data_editor(data_df, use_container_width=True, num_rows="dynamic")
    if st.button("Simpan Master Data"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("Data tersimpan!")
        st.rerun()

# ==========================================
# 5. ROUTER (LOGIKA UTAMA - DIPERBAIKI)
# ==========================================

# LOGIKA UTAMA: Pastikan pencarian dan menu tidak bentrok
if search_term:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_term, case=False, na=False)]
    st.dataframe(results, use_container_width=True)
else:
    # --- PENGUNAAN ELIF YANG KETAT ---
    if st.session_state.current_page == "Dashboard":
        show_dashboard(df)
    elif st.session_state.current_page == "Update":
        show_update(df)
    elif st.session_state.current_page == "Master":
        show_master(df)
    else:
        # Default jika state error
        show_dashboard(df)

# ==========================================
# 6. LOGIKA JAM WIB (DI BAWAH)
# ==========================================
while True:
    now_wib = datetime.utcnow() + timedelta(hours=7)
    clock_placeholder.markdown(f"""
        <div class="clock-box">
            <p style="font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 0;">{now_wib.strftime("%A, %d %B %Y")}</p>
            <h1 style="font-size: 2.8rem; margin-top: -10px; color: #000000; font-family: monospace;">{now_wib.strftime("%H:%M:%S")}</h1>
            <p style="font-size: 0.8rem; color: #ff0000; font-weight: bold; margin-top: -5px;">Waktu Indonesia Barat (WIB)</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
