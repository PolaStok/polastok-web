import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import load_sample_data

# 1. Konfigurasi Halaman (Ikon tab pakai logo PolaStok)
st.set_page_config(page_title="Daftar Barang | PolaStok", page_icon="assets/logo.png", layout="wide")
st.logo("assets/logo.png", size="large")

if not st.session_state.get('logged_in', False): 
    st.switch_page("PolaStok.py")
if 'nama_toko' not in st.session_state: 
    st.session_state.nama_toko = 'Toko Anda'

# 2. CSS Khusus "Figma Look"
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebarNav"] > div:first-child > span { font-size: 32px !important; font-weight: 900 !important; color: #1E293B !important; letter-spacing: -0.5px !important; margin-left: 10px; }
    .main div[data-testid="stButton"] > button {
        background-color: white !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; padding: 20px 24px !important;
        color: #1E293B !important; font-weight: 600 !important; display: flex !important; justify-content: flex-start !important;
        width: 100% !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important; margin-bottom: 25px !important;
    }
    .main div[data-testid="stButton"] > button:hover { border-color: #CBD5E1 !important; background-color: #F8FAFC !important; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; padding: 12px 16px !important; background-color: white !important; }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar 
with st.sidebar:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("---")
    with st.popover("⚙️ Pengaturan Toko", use_container_width=True):
        st.write("Edit Profil UMKM")
        with st.form("form_pengaturan_1"):
            new_name = st.text_input("Nama Toko", value=st.session_state.nama_toko)
            if st.form_submit_button("Simpan Perubahan", type="primary"):
                st.session_state.nama_toko = new_name
                st.rerun()
    if st.button("🚪 Keluar Akun", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.switch_page("PolaStok.py")

# 4. Konten Utama
st.markdown("<h2 style='color: #1E293B; font-weight: 800; margin-bottom: 20px; margin-top: -10px;'> 📦 Daftar Seluruh Barang</h2>", unsafe_allow_html=True)
if st.button("Tambah Barang Baru", use_container_width=True): 
    st.toast("Fitur tambah barang akan segera hadir!", icon="🚧")

col_search, col_kosong = st.columns([1.5, 2])
with col_search: 
    search_query = st.text_input("Pencarian", placeholder="🔍 Cari nama barang...", label_visibility="collapsed")

# 5. Persiapan Data
df = load_sample_data()
df_display = df.copy()
if 'kategori' not in df_display.columns: 
    df_display['kategori'] = 'Sembako'
if 'harga' not in df_display.columns:
    np.random.seed(42)
    df_display['harga'] = np.random.randint(10, 50, size=len(df_display)) * 1000

df_display['status'] = df_display['status'].str.capitalize()
if search_query: 
    df_display = df_display[df_display['nama_produk'].str.contains(search_query, case=False, na=False)]

df_display = df_display.rename(columns={'nama_produk': 'Nama Produk', 'kategori': 'Kategori', 'harga': 'Harga Satuan (Rp)', 'stok': 'Sisa Stok', 'status': 'Status'})
cols_to_show = ['Nama Produk', 'Kategori', 'Harga Satuan (Rp)', 'Sisa Stok', 'Status']

# 6. Menampilkan Tabel Interaktif (BISA EDIT & HAPUS)
with st.container(border=True):
    # Menggunakan st.data_editor agar bisa seperti Excel
    edited_df = st.data_editor(
        df_display[cols_to_show],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic", # Ini yang bikin bisa nambah/hapus baris
        column_config={
            "Nama Produk": st.column_config.TextColumn("Nama Produk", width="medium"),
            # Kategori dibuat jadi dropdown agar pengguna UMKM tinggal pilih
            "Kategori": st.column_config.SelectboxColumn("Kategori", width="small", options=["Sembako", "Minuman", "Snack", "Lainnya"]),
            "Harga Satuan (Rp)": st.column_config.NumberColumn("Harga Satuan (Rp)", width="small", format="%d"),
            "Sisa Stok": st.column_config.NumberColumn("Sisa Stok", width="small", min_value=0),
            # Status dikunci (disabled) karena ini indikator, bukan inputan
            "Status": st.column_config.TextColumn("Status", width="small", disabled=True)
        }
    )

# Catatan panduan penggunaan yang ramah untuk pemilik warung
st.caption("💡 **Tips:** Klik dua kali pada sel tabel untuk **mengubah data**. Untuk **menghapus barang**, centang kotak kecil di ujung kiri baris, lalu tekan tombol `Delete` atau `Backspace` di keyboard Anda.")