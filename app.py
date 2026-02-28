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
# 2. STYLE CSS (Merapikan Sidebar & Dashboard)
# ==========================================
def set_style():
    style = '''
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Putih */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        padding-top: 1rem !important;
    }
    
    /* Teks Sidebar Hitam */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    
    /* Tombol Merah Toyota */
    div.stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        font-weight: bold;
        border-radius: 8px;
        height: 42px;
        width: 100%;
        margin-bottom: -10px;
    }
    
    /* Menghilangkan header default Streamlit agar bersih */
    header {visibility: hidden;}
    .block-container { padding-top: 2rem !important; }
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
            # Standarisasi kolom tanggal
            df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
            df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
            return df
        except:
            return buat_data_baru()
    else:
        return buat_data_baru()

def buat_data_baru():
    data = {
        'ID': [1], 'Nama Mesin': ['Bucket Elevator'], 'Nama Part': ['Bearing 6205'], 
        'Line Produksi': ['Moulding'], 'Lokasi Rak': ['Zone 4'], 'Stok': [10], 
        'Rentang Waktu (Bulan)': [1], 'Tanggal Terakhir Ganti': [datetime.now().date()], 
        'Jadwal Jatuh Tempo': [datetime.now().date() + relativedelta(months=1)], 
        'Status TPM': ['On Progress'], 'PIC': ['Admin']
    }
    df = pd.DataFrame(data)
    df.to_csv(FILE_DATA, index=False)
    return df

df = muat_data()

# ==========================================
# 4. SIDEBAR (Logo, Jam, Navigasi)
# ==========================================
with st.sidebar:
    # Logo Toyota Indonesia (Gunakan URL agar pasti muncul di Cloud)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Toyota_carlogo.svg/1200px-Toyota_carlogo.svg.png", use_container_width=True)
    st.markdown("<p style='text-align: center; color: black; font-weight: bold; margin-top: -15px;'>INDONESIA</p>", unsafe_allow_html=True)
    
    # Placeholder Jam Real-time (Detik menghitung)
    container_jam = st.empty()
    
    st.markdown("---")
    
    # Inisialisasi Session State Halaman
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
    search_query = st.text_input("Nama part/mesin...", placeholder="Ketik di sini", label_visibility="collapsed")

# ==========================================
# 5. HALAMAN UTAMA
# ==========================================

# A. Logika Pencarian
if search_query:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_query, case=False, na=False) | 
                 df['Nama Mesin'].str.contains(search_query, case=False, na=False)]
    st.dataframe(results, use_container_width=True)

# B. Halaman Dashboard
elif st.session_state.page == "Dashboard":
    st.title("📊 Maindashboard Monitoring")
    
    today = datetime.now().date()
    
    # METRIK (FIXED: Status TPM bukan TPN)
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
                selesai = len(df_l[df_l['Status TPM'] == 'Finish'])
                st.progress(selesai / len(df_l))
                st.caption(f"{selesai} dari {len(df_l)} part selesai.")
            else:
                st.caption("Belum ada data.")

# C. Halaman Update
elif st.session_state.page == "Update":
    st.title("🛠️ Update Status Penggantian")
    with st.form("form_update"):
        pilihan = st.selectbox("Pilih Part", (df['Nama Mesin'] + " - " + df['Nama Part']).tolist())
        pic_baru = st.text_input("PIC Eksekutor")
        tgl_ganti = st.date_input("Tanggal Ganti Baru", today)
        
        if st.form_submit_button("Simpan Data"):
            # Update logika CSV
            idx = df[df['Nama Mesin'] + " - " + df['Nama Part'] == pilihan].index[0]
            bln = df.at[idx, 'Rentang Waktu (Bulan)']
            df.at[idx, 'Tanggal Terakhir Ganti'] = tgl_ganti
            df.at[idx, 'Jadwal Jatuh Tempo'] = tgl_ganti + relativedelta(months=int(bln))
            df.at[idx, 'Status TPM'] = 'Finish'
            df.at[idx, 'PIC'] = pic_baru
            df.to_csv(FILE_DATA, index=False)
            st.success("Data berhasil diupdate!")
            st.rerun()

# D. Halaman Master Data
elif st.session_state.page == "Master":
    st.title("➕ Master Data Part")
    # Editor data interaktif sesuai gambar Anda
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("Simpan Seluruh Perubahan Master"):
        edited.to_csv(FILE_DATA, index=False)
        st.success("Master data diperbarui!")
        st.rerun()

# ==========================================
# 6. LOGIKA JAM REAL-TIME (Wajib di Paling Bawah)
# ==========================================
while True:
    skrg = datetime.now()
    container_jam.markdown(f"""
        <div style="text-align: center; border: 1.5px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f8f9fa;">
            <p style="font-size: 1rem; font-weight: bold; color: #333; margin-bottom: 0;">{skrg.strftime("%A, %d %B %Y")}</p>
            <h1 style="font-size: 2.6rem; margin-top: -8px; color: #000; font-family: 'Courier New', monospace;">{skrg.strftime("%H:%M:%S")}</h1>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
