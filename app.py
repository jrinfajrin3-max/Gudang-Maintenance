import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="TPM Control System - TMMIN", layout="wide")

# ==========================================
# 2. STYLE CSS
# ==========================================
def set_style():
    style = '''
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; padding-top: 0.5rem !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h3 { color: #000000 !important; }
    div.stButton > button { background-color: #ff0000; color: white; border: none; font-weight: bold; border-radius: 8px; width: 100%; }
    .block-container { padding-top: 1.5rem !important; }
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
            return buat_template()
    else:
        return buat_template()

def buat_template():
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
# 4. SIDEBAR (Logo Lokal, Jam WIB, Navigasi)
# ==========================================
with st.sidebar:
    # Menggunakan logo lokal dari folder sendiri
    if os.path.exists("logo_toyota.png"):
        st.image("logo_toyota.png", use_container_width=True)
    else:
        st.error("File logo_toyota.png tidak ditemukan di folder!")

    # --- TEMPAT JAM BERDETAK (WIB) ---
    container_jam = st.empty()
    
    st.markdown("---")
    
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
        
    st.markdown("### 🧭 Menu Utama")
    if st.button("📊 Dashboard Monitoring"):
        st.session_state.page = "Dashboard"
    if st.button("🛠️ Update Penggantian Part"):
        st.session_state.page = "Update"
    if st.button("➕ Master Data Part"):
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
    # Penyesuaian waktu Indonesia untuk perbandingan jatuh tempo
    today = (datetime.utcnow() + timedelta(hours=7)).date()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", len(df))
    c2.metric("Perlu Ganti (Delay)", len(df[df['Jadwal Jatuh Tempo'] <= today]))
    c3.metric("Selesai TPM", len(df[df['Status TPM'] == 'Finish']))
    
    st.markdown("---")
    st.subheader("🚧 Progress TPM per Line Produksi")
    cols = st.columns(2)
    for i, line in enumerate(list_line):
        with cols[i % 2]:
            df_l = df[df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_l.empty:
                st.progress(len(df_l[df_l['Status TPM'] == 'Finish']) / len(df_l))
            else:
                st.caption("Belum ada data.")

elif st.session_state.page == "Update":
    st.title("🛠️ Update Penggantian")
    # Bagian update (tetap sama)
    st.info("Pilih part pada menu Master Data untuk melakukan perubahan detail.")

elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    # Tabel editor interaktif sesuai kebutuhan Anda
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("Simpan Perubahan Master"):
        edited_df.to_csv(FILE_DATA, index=False)
        st.success("Data berhasil disimpan!")
        st.rerun()

# ==========================================
# 6. LOGIKA JAM REAL-TIME WIB (Update Detik)
# ==========================================
while True:
    # Menambahkan 7 jam agar jam 15 (UTC) berubah jadi jam 22 (WIB)
    wib_now = datetime.utcnow() + timedelta(hours=7)
    
    container_jam.markdown(f"""
        <div style="text-align: center; border: 1.5px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f8f9fa;">
            <p style="font-size: 1rem; font-weight: bold; color: #333; margin-bottom: 0;">{wib_now.strftime("%A, %d %B %Y")}</p>
            <h1 style="font-size: 2.5rem; margin-top: -8px; color: #000; font-family: monospace;">{wib_now.strftime("%H:%M:%S")}</h1>
            <p style="font-size: 0.8rem; color: #ff0000; font-weight: bold;">Waktu Indonesia Barat (WIB)</p>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1)
