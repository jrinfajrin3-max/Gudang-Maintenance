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
# FUNGSI CSS CUSTOM (MENAIKKAN KONTEN & CSS)
# ==========================================
def set_style():
    style = '''
    <style>
    .stApp { background-color: #1e2530; color: #ffffff; }
    
    /* Sidebar Putih Clean & Mentok Atas */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        padding-top: 0rem !important; /* Mengurangi padding atas */
    }
    
    /* Teks Sidebar Hitam */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #000000 !important;
    }
    
    /* Progress Bar Merah */
    .stProgress > div > div > div > div {
        background-color: #ff0000;
    }
    
    /* Tombol Aksi */
    div.stButton > button {
        background-color: #ff0000;
        color: white;
        border: none;
        margin-top: -10px; /* Menarik tombol lebih ke atas */
    }

    /* Mengatur jarak elemen di sidebar */
    [data-testid="stSidebar"] .block-container {
        padding-top: 0rem !important;
    }

    /* --- PERBAIKAN: MENAIKKAN KONTEN KANAN --- */
    .block-container {
        padding-top: 1rem !important; /* Mengurangi jarak atas */
        margin-top: -20px; /* Menarik konten lebih ke atas */
    }
    
    /* Memastikan judul naik */
    h1 {
        margin-top: -30px !important;
    }
    </style>
    '''
    # CARA PERBAIKAN: Gunakan markdown untuk menyisipkan gaya
    st.markdown(style, unsafe_allow_html=True)

set_style()

# ==========================================
# KONFIGURASI DATABASE
# ==========================================
FILE_DATA = "data_gudang.csv"
list_line = ["Sand Preparation", "Moulding", "Core Making", "Finishing", "RCS Pretreatment", "Melting"]

# Mapping lokasi otomatis
mapping_lokasi = {
    "Sand Preparation": "Zone 3",
    "Moulding": "Zone 4",
    "Core Making": "Zone 2",
    "RCS Pretreatment": "Zone 2",
    "Finishing": "Zone 1",
    "Melting": "Zone 5"
}

def buat_data_baru():
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

def muat_data():
    if os.path.exists(FILE_DATA):
        try:
            df = pd.read_csv(FILE_DATA)
            required_columns = ['Tanggal Terakhir Ganti', 'Jadwal Jatuh Tempo']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = datetime.now().date()
            
            df['Tanggal Terakhir Ganti'] = pd.to_datetime(df['Tanggal Terakhir Ganti']).dt.date
            df['Jadwal Jatuh Tempo'] = pd.to_datetime(df['Jadwal Jatuh Tempo']).dt.date
            return df
        except Exception as e:
            st.error(f"Error membaca database: {e}")
            return buat_data_baru()
    else:
        return buat_data_baru()

df = muat_data()

# ==========================================
# SIDEBAR (Logo, Jam, Menu, Pencarian)
# ==========================================
with st.sidebar:
    # 1. Logo Toyota Besar di Tengah (Mentok Atas)
    if os.path.exists("logo_toyota.png"):
        st.image("logo_toyota.png", use_container_width=True) # Menggunakan lebar penuh sidebar
    else:
        st.markdown("<h2 style='text-align: center; color: black; margin-top: -20px;'>TOYOTA</h2>", unsafe_allow_html=True)
    
    # 2. Tanggal dan Jam (Ukuran Besar & Bold)
    sekarang = datetime.now()
    tgl_str = sekarang.strftime("%A, %d %B %Y")
    jam_str = sekarang.strftime("%H:%M:%S")
    
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; font-weight: bold; margin-bottom: 0; margin-top: -10px;'>{tgl_str}</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; margin-top: -10px;'>{jam_str}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. Kotak Pencarian Sparepart
    st.markdown("### 🔍 Cari Sparepart / Mesin")
    search_query = st.text_input("Ketik nama...", key="search_bar", label_visibility="collapsed")
    
    st.markdown("---")
    
    # 4. Menu Navigasi
    st.markdown("### 🧭 Menu Utama")
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    if st.button("📊 Dashboard Monitoring", use_container_width=True):
        st.session_state.page = "Dashboard"
    if st.button("🛠️ Update Penggantian Part", use_container_width=True):
        st.session_state.page = "Update"
    if st.button("➕ Master Data Part", use_container_width=True):
        st.session_state.page = "Master"

# ==========================================
# LOGIKA PENCARIAN (TAMPIL DI HALAMAN UTAMA)
# ==========================================
if search_query:
    st.title("🔍 Hasil Pencarian")
    
    results = df[
        df['Nama Part'].str.contains(search_query, case=False, na=False) |
        df['Nama Mesin'].str.contains(search_query, case=False, na=False)
    ].copy() 
    
    if not results.empty:
        st.dataframe(
            results[['ID', 'Nama Mesin', 'Nama Part', 'Line Produksi', 'Lokasi Rak', 'Stok', 'Status TPM']], 
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("🛠️ Aksi Pengambilan Barang")
        
        for index, row in results.iterrows():
            col_part, col_btn = st.columns([3, 1])
            with col_part:
                st.write(f"**{row['Nama Part']}** - Mesin: {row['Nama Mesin']}")
                st.caption(f"Lokasi Rak: {row['Lokasi Rak']} | Stok: {row['Stok']}")
            with col_btn:
                if st.button(f"Ambil", key=f"btn_{row['ID']}"):
                    if row['Stok'] > 0:
                        df.at[index, 'Stok'] = row['Stok'] - 1
                        df.to_csv(FILE_DATA, index=False)
                        st.success(f"1 {row['Nama Part']} diambil dari {row['Lokasi Rak']}.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Stok habis!")
                    
    else:
        st.warning("Data tidak ditemukan.")
    st.markdown("---")

# ==========================================
# HALAMAN 1: DASHBOARD MONITORING
# ==========================================
elif st.session_state.page == "Dashboard":
    # --- PERBAIKAN: JUDUL DASHBOARD DISAMBUNG ---
    st.title("📊 Maindashboard") # Disambung
    
    today = datetime.now().date()
    
    c1, c2, c3 = st.columns(3)
    total_part = len(df)
    total_delay = len(df[df['Jadwal Jatuh Tempo'] <= today])
    total_finish = len(df[df['Status TPM'] == 'Finish'])
    
    c1.metric("Total Items", total_part)
    c2.metric("Perlu Ganti (Delay)", total_delay, delta_color="inverse")
    c3.metric("Selesai TPM", total_finish)
    
    st.markdown("---")
    st.subheader("🚧 Progress TPM per Line Produksi")
    
    col_line = st.columns(2)
    for idx, line in enumerate(list_line):
        with col_line[idx % 2]:
            df_line = df[df['Line Produksi'] == line]
            if not df_line.empty:
                count_total = len(df_line)
                count_done = len(df_line[df_line['Status TPM'] == 'Finish'])
                prog = count_done / count_total
                
                st.write(f"**{line}** ({count_done}/{count_total} Part Selesai)")
                st.progress(prog)
            else:
                st.write(f"**{line}**")
                st.caption("Belum ada data part di line ini.")
    
    st.markdown("---")
    st.subheader("⚠️ List Part Delay (Segera Ganti)")
    df_warn = df[df['Jadwal Jatuh Tempo'] <= today]
    if not df_warn.empty:
        st.table(df_warn[['Line Produksi', 'Nama Mesin', 'Nama Part', 'Jadwal Jatuh Tempo', 'PIC']])
    else:
        st.success("Semua part dalam kondisi On Schedule!")

# ==========================================
# HALAMAN 2: UPDATE PENGGANTIAN
# ==========================================
elif st.session_state.page == "Update":
    st.title("🛠️ Form Penggantian Sparepart")
    
    with st.form("update_form"):
        part_pilihan = df['Nama Mesin'] + " | " + df['Nama Part']
        pilih = st.selectbox("Pilih Mesin & Part", part_pilihan)
        tgl_ganti = st.date_input("Tanggal Penggantian", datetime.now())
        pic_update = st.text_input("PIC Eksekutor")
        
        submit = st.form_submit_button("Konfirmasi Selesai Ganti")
        
        if submit:
            idx = df[df['Nama Mesin'] + " | " + df['Nama Part'] == pilih].index[0]
            rentang = df.at[idx, 'Rentang Waktu (Bulan)']
            
            df.at[idx, 'Tanggal Terakhir Ganti'] = tgl_ganti
            df.at[idx, 'Jadwal Jatuh Tempo'] = tgl_ganti + relativedelta(months=int(rentang))
            df.at[idx, 'Status TPM'] = 'Finish'
            df.at[idx, 'PIC'] = pic_update
            
            df.to_csv(FILE_DATA, index=False)
            st.success("Data Berhasil Diperbarui! Jadwal otomatis diperpanjang.")
            time.sleep(1)
            st.rerun()

# ==========================================
# HALAMAN 3: MASTER DATA (TAMBAH & EDIT)
# ==========================================
elif st.session_state.page == "Master":
    st.title("➕ Manajemen Master Part")
    
    with st.expander("➕ Tambah Part Baru", expanded=True):
        with st.form("master_form"):
            c1, c2 = st.columns(2)
            with c1:
                m_line = st.selectbox("Line Produksi", list_line)
                m_mesin = st.text_input("Nama Mesin")
                m_part = st.text_input("Nama Part Sparepart")
                
                # Lokasi Otomatis
                lokasi_default = mapping_lokasi.get(m_line, "")
                m_lokasi = st.text_input("Lokasi Rak (Zone/Rak)", value=lokasi_default)
                
            with c2:
                m_rentang = st.number_input("Siklus Ganti (Bulan)", min_value=1, value=1)
                m_stok = st.number_input("Jumlah Stok Awal", min_value=0, value=1)
                m_tgl = st.date_input("Tanggal Terakhir Ganti Saat Ini", datetime.now())
                m_pic = st.text_input("PIC Penanggung Jawab")
                
            if st.form_submit_button("Simpan Data Master"):
                jadwal_next = m_tgl + relativedelta(months=int(m_rentang))
                new_row = {
                    'ID': df['ID'].max() + 1 if not df.empty else 1,
                    'Nama Mesin': m_mesin,
                    'Nama Part': m_part,
                    'Line Produksi': m_line,
                    'Lokasi Rak': m_lokasi, 
                    'Stok': m_stok,
                    'Rentang Waktu (Bulan)': m_rentang,
                    'Tanggal Terakhir Ganti': m_tgl,
                    'Jadwal Jatuh Tempo': jadwal_next,
                    'Status TPM': 'On Progress',
                    'PIC': m_pic
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(FILE_DATA, index=False)
                st.success("Data Master Berhasil Ditambahkan!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Edit / Hapus Master Data")
    
    st.write("Edit data langsung pada tabel di bawah ini:")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if st.button("Simpan Perubahan Tabel"):
        edited_df.to_csv(FILE_DATA, index=False)
        st.success("Data Master Berhasil Diperbarui!")
        st.rerun()
