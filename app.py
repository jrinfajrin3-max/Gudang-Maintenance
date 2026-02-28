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

# Custom CSS untuk merapikan tampilan
def local_css():
    st.markdown("""
    <style>
    /* Main Background Gelap */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Putih */
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
    
    /* Styling Jam */
    .clock-box {
        text-align: center;
        border: 1.5px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background-color: #f8f9fa;
        margin-top: 10px;
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
            # Konversi kolom tanggal
            df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
            df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
            return df
        except Exception:
            return create_initial_data()
    else:
        return create_initial_data()

def create_initial_data():
    # Menggunakan 'Status TPM' (BUKAN TPN)
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
    # Logo dari folder lokal
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
# 4. FUNGSI HALAMAN (DIPISAH AGAR TIDAK BAYANGAN)
# ==========================================
def show_dashboard(data_df):
    st.title("📊 Maindashboard Monitoring") #
    
    # Zona Waktu WIB (UTC+7)
    current_date_wib = (datetime.utcnow() + timedelta(hours=7)).date()
    
    # Metrik Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(data_df))
    
    # Filter Perlu Ganti (Delay)
    delay_count = len(data_df[data_df['Jadwal Jatuh Tempo'] <= current_date_wib])
    col2.metric("Perlu Ganti (Delay)", delay_count)
    
    # Filter Selesai TPM (Gunakan 'Status TPM' agar tidak KeyError)
    finish_count = len(data_df[data_df['Status TPM'] == 'Finish'])
    col3.metric("Selesai TPM", finish_count)
    
    st.markdown("---")
    
    # Progress per Line
    st.subheader("🚧 Progress TPM per Line Produksi")
    p_col1, p_col2 = st.columns(2)
    
    for i, line in enumerate(LINE_LIST):
        target_col = p_col1 if i % 2 == 0 else p_col2
        with target_col:
            df_line = data_df[data_df['Line Produksi'] == line]
            st.write(f"**{line}**")
            if not df_line.empty:
                done = len(df_line[df_line['Status TPM'] == 'Finish'])
                total = len(df_line)
                progress = done / total
                st.progress(progress)
                st.caption(f"{done} dari {total} part selesai.")
            else:
                st.caption("Belum ada data part di line ini.")

    st.markdown("---")
    
    # List Part Delay
    st.subheader("⚠️ List Part Delay (Segera Ganti)")
    df_delay = data_df[data_df['Jadwal Jatuh Tempo'] <= current_date_wib]
    if not df_delay.empty:
        st.warning(f"Terdapat {len(df_delay)} part yang melewati batas waktu penggantian!")
        st.table(df_delay[['Nama Mesin', 'Nama Part', 'Jadwal Jatuh Tempo', 'PIC']])
    else:
        st.success("Semua part dalam kondisi On Schedule!")

def show_update(data_df):
    st.title("🛠️ Update Penggantian Part")
    with st.form("form_update"):
        st.write("Input data penggantian sparepart baru")
        # Dropdown kombinasi
        options = (data_df['Nama Mesin'] + " | " + data_df['Nama Part']).tolist()
        selected_part = st.selectbox("Pilih Part yang Diganti", options=options)
        
        tgl_ganti = st.date_input("Tanggal Penggantian", datetime.now())
        pic_input = st.text_input("PIC Eksekutor")
        
        if st.form_submit_button("Konfirmasi Update"):
            # Cari baris data
            idx = data_df[data_df['Nama Mesin'] + " | " + data_df['Nama Part'] == selected_part].index[0]
            rentang = data_df.at[idx, 'Rentang Waktu (Bulan)']
            
            # Update Nilai
            data_df.at[idx, 'Tanggal Terakhir Ganti'] = tgl_ganti
            data_df.at[idx, 'Jadwal Jatuh Tempo'] = tgl_ganti + relativedelta(months=int(rentang))
            data_df.at[idx, 'Status TPM'] = 'Finish'
            data_df.at[idx, 'PIC'] = pic_input
            
            # Simpan
            data_df.to_csv(DB_FILE, index=False)
            st.success(f"Update Berhasil untuk {selected_part}!")
            time.sleep(1)
            st.rerun()

def show_master(data_df):
    st.title("➕ Master Data Part") #
    
    # Form Tambah Data Baru
    with st.expander("➕ Tambah Part Baru"):
        with st.form("add_new"):
            c1, c2 = st.columns(2)
            line_new = c1.selectbox("Line Produksi", LINE_LIST)
            mesin_new = c1.text_input("Nama Mesin")
            part_new = c1.text_input("Nama Part Sparepart")
            lokasi_new = c1.text_input("Lokasi Rak (Zone/Rak)")
            
            siklus_new = c2.number_input("Siklus Ganti (Bulan)", min_value=1, value=1)
            stok_new = c2.number_input("Jumlah Stok Awal", min_value=0, value=1)
            tgl_awal = c2.date_input("Tanggal Terakhir Ganti Saat Ini")
            pic_new = c2.text_input("PIC Penanggung Jawab")
            
            if st.form_submit_button("Simpan Data Master"):
                new_id = data_df['ID'].max() + 1 if not data_df.empty else 1
                jatuh_tempo = tgl_awal + relativedelta(months=int(siklus_new))
                
                new_row = {
                    'ID': new_id, 'Nama Mesin': mesin_new, 'Nama Part': part_new,
                    'Line Produksi': line_new, 'Lokasi Rak': lokasi_new, 'Stok': stok_new,
                    'Rentang Waktu (Bulan)': siklus_new, 'Tanggal Terakhir Ganti': tgl_awal,
                    'Jadwal Jatuh Tempo': jatuh_tempo, 'Status TPM': 'On Progress', 'PIC': pic_new
                }
                data_df = pd.concat([data_df, pd.DataFrame([new_row])], ignore_index=True)
                data_df.to_csv(DB_FILE, index=False)
                st.success("Data Part Berhasil Ditambahkan!")
                st.rerun()

    st.markdown("---")
    st.subheader("📝 Edit / Hapus Master Data")
    # Editor data interaktif
    edited_df = st.data_editor(data_df, use_container_width=True, num_rows="dynamic")
    
    if st.button("Simpan Perubahan Master"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("Seluruh perubahan berhasil disimpan!")
        st.rerun()

# ==========================================
# 5. ROUTER (LOGIKA UTAMA)
# ==========================================

# Logika Pencarian Universal
if search_term:
    st.title("🔍 Hasil Pencarian")
    results = df[df['Nama Part'].str.contains(search_term, case=False, na=False) | 
                 df['Nama Mesin'].str.contains(search_term, case=False, na=False)]
    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.warning(f"Tidak ada data ditemukan untuk kata kunci: {search_term}")
else:
    # Router Halaman
    if st.session_state.current_page == "Dashboard":
        show_dashboard(df)
    elif st.session_state.current_page == "Update":
        show_update(df)
    elif st.session_state.current_page == "Master":
        show_master(df)

# ==========================================
# 6. LOGIKA JAM REAL-TIME WIB (Update per Detik)
# ==========================================
# Loop ini harus di paling akhir agar tidak menghentikan fungsi streamlit
while True:
    # GitHub Server (UTC) + 7 Jam = WIB
    now_wib = datetime.utcnow() + timedelta(hours=7)
    
    clock_placeholder.markdown(f"""
        <div class="clock-box">
            <p style="font-size: 1.1rem; font-weight: bold; color: #333; margin-bottom: 0;">{now_wib.strftime("%A, %d %B %Y")}</p>
            <h1 style="font-size: 2.8rem; margin-top: -10px; color: #000000; font-family: 'Courier New', Courier, monospace;">{now_wib.strftime("%H:%M:%S")}</h1>
            <p style="font-size: 0.8rem; color: #ff0000; font-weight: bold; margin-top: -5px;">Waktu Indonesia Barat (WIB)</p>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1) # Refresh setiap 1 detik
