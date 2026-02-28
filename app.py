import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(
    page_title="TPM Control System - TMMIN", 
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS agar tampilan persis seperti permintaan Anda
def local_css():
    st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        padding-top: 1rem !important;
        border-right: 1px solid #ddd;
    }
    
    /* Teks Sidebar menjadi Hitam agar Kontras */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    
    /* Tombol Navigasi Merah Toyota */
    div.stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 5px;
        width: 100%;
        height: 45px;
        margin-bottom: -10px;
    }
    
    div.stButton > button:hover {
        background-color: #cc0000;
        border: none;
        color: white;
    }

    /* Input Search Styling */
    .stTextInput input {
        background-color: #f1f1f1 !important;
        color: black !important;
    }
    
    /* Metrik Card */
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: bold; }
    
    /* Status Box */
    .status-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==========================================
# 2. MANAJEMEN DATA (DATABASE CSV)
# ==========================================
DB_FILE = "data_gudang.csv"
LINE_LIST = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Konversi kolom tanggal agar tidak error saat olah data
            df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
            df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
            return df
        except Exception:
            return create_initial_data()
    else:
        return create_initial_data()

def create_initial_data():
    # Menggunakan Nama Kolom yang Konsisten 'Status TPM' (Bukan TPN)
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
    df.to_csv(DB_FILE, index=False)
    return df

# Muat data global
df = load_data()

# ==========================================
# 3. SIDEBAR (LOGO, JAM WIB, NAVIGASI)
# ==========================================
with st.sidebar:
    # Logo Lokal
    if os.path.exists("logo_toyota.png"):
        st.image("logo_toyota.png", use_container_width=True)
    else:
        st.markdown("<h2 style='color:red; text-align:center;'>TOYOTA</h2>", unsafe_allow_html=True)
    
    # --- REAL-TIME CLOCK PLACEHOLDER ---
    clock_placeholder = st.empty()
    
    st.markdown("---")
    
    # Navigasi Menu
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
    search_term = st.text_input("Ketik nama part/mesin", placeholder="Search...", label_visibility="collapsed")

# ==========================================
# 4. HALAMAN DASHBOARD MONITORING
# ==========================================
def show_dashboard(data_df):
    st.title("📊 Maindashboard Monitoring")
    
    # Zona Waktu WIB (UTC+7) untuk perbandingan jatuh tempo
    current_date_wib = (datetime.utcnow() + timedelta(hours=7)).date()
    
    # Metrik Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(data_df))
    
    # Filter Perlu Ganti (Delay)
    delay_count = len(data_df[data_df['Jadwal Jatuh Tempo'] <= current_date_wib])
    col2.metric("Perlu Ganti (Delay)", delay_count)
    
    # Filter Selesai
