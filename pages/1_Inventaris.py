import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import load_sample_data

st.set_page_config(page_title="Daftar Barang | PolaStok", page_icon="assets/logo.png", layout="wide")

if 'nama_toko' not in st.session_state: 
    st.session_state.nama_toko = 'Toko Anda'

# ------- dummy database ----------
if 'df_inventaris' not in st.session_state:
    df_awal = load_sample_data()
    if 'kategori' not in df_awal.columns: 
        df_awal['kategori'] = 'Sembako'
    if 'harga' not in df_awal.columns:
        np.random.seed(42)
        df_awal['harga'] = np.random.randint(10, 50, size=len(df_awal)) * 1000
    if 'safety_stock' not in df_awal.columns:
        df_awal['safety_stock'] = 15
    df_awal['status'] = df_awal['status'].str.capitalize()
    st.session_state.df_inventaris = df_awal

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

with st.sidebar:
    st.image("assets/logo.png", use_column_width=True)
    st.markdown("---")
    with st.popover("⚙️ Pengaturan Toko", use_container_width=True):
        st.write("Edit Profil UMKM")
        with st.form("form_pengaturan_1"):
            new_name = st.text_input("Nama Toko", value=st.session_state.nama_toko)
            if st.form_submit_button("Simpan Perubahan", type="primary"):
                st.session_state.nama_toko = new_name
                st.rerun()

with st.expander("➕ Tambah Barang Baru", expanded=False):
    st.write("Isi detail barang dagangan baru, lalu klik Simpan.")
    
    with st.form("form_tambah_barang", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            nama_baru = st.text_input("Nama Produk*")
            kategori_baru = st.selectbox("Kategori", ["Sembako", "Minuman", "Snack", "Lainnya"])
        with col_form2:
            harga_baru = st.number_input("Harga Satuan (Rp)", min_value=0, step=1000)
            stok_baru = st.number_input("Stok Awal", min_value=0, step=1)
        
        submit_btn = st.form_submit_button("Simpan Barang", type="primary")
        
        if submit_btn:
            if nama_baru.strip() == "":
                st.error("Nama produk tidak boleh kosong!")
            else:
                status_baru = "Aman" if stok_baru > 10 else "Kritis"
                data_baru = pd.DataFrame([{
                    "nama_produk": nama_baru,
                    "stok": stok_baru,
                    "satuan": "pcs",
                    "status": status_baru,
                    "kategori": kategori_baru,
                    "harga": harga_baru,
                    "safety_stock": 15
                }])
                st.session_state.df_inventaris = pd.concat([data_baru, st.session_state.df_inventaris], ignore_index=True)
                st.success(f"Barang {nama_baru} berhasil ditambahkan!")
                st.rerun() 

col_search, col_kosong = st.columns([1.5, 2])
with col_search: 
    search_query = st.text_input("Pencarian", placeholder="🔍 Cari nama barang...", label_visibility="collapsed")

df_display = st.session_state.df_inventaris.copy()

if search_query: 
    df_display = df_display[df_display['nama_produk'].str.contains(search_query, case=False, na=False)]

df_display['kekurangan'] = (df_display['safety_stock'] - df_display['stok']).clip(lower=0)
df_display['potensi_kerugian'] = df_display['kekurangan'] * df_display['harga']

df_display = df_display.rename(columns={
    'nama_produk': 'Nama Produk', 
    'kategori': 'Kategori', 
    'harga': 'Harga Satuan (Rp)', 
    'stok': 'Sisa Stok', 
    'status': 'Status',
    'potensi_kerugian': 'Potensi Kerugian (Rp)'
})

cols_to_show = ['Nama Produk', 'Kategori', 'Harga Satuan (Rp)', 'Sisa Stok', 'Status', 'Potensi Kerugian (Rp)']

with st.container(border=True):
    edited_df = st.data_editor(
        df_display[cols_to_show],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Nama Produk": st.column_config.TextColumn("Nama Produk", width="medium"),
            "Kategori": st.column_config.SelectboxColumn("Kategori", width="small", options=["Sembako", "Minuman", "Snack", "Lainnya"]),
            "Harga Satuan (Rp)": st.column_config.NumberColumn("Harga Satuan (Rp)", width="small", format="%d"),
            "Sisa Stok": st.column_config.NumberColumn("Sisa Stok", width="small", min_value=0),
            "Status": st.column_config.TextColumn("Status", width="small", disabled=True),
            "Potensi Kerugian (Rp)": st.column_config.NumberColumn("Potensi Kerugian (Rp)", width="medium", format="%d", disabled=True)
        }
    )
    
    if not edited_df.equals(df_display[cols_to_show]):
        reversed_cols = {
            'Nama Produk': 'nama_produk', 
            'Kategori': 'kategori', 
            'Harga Satuan (Rp)': 'harga', 
            'Sisa Stok': 'stok', 
            'Status': 'status',
            'Potensi Kerugian (Rp)': 'potensi_kerugian'
        }
        df_to_save = edited_df.rename(columns=reversed_cols)
        df_to_save['satuan'] = "pcs" 
        
        if 'safety_stock' not in df_to_save.columns:
            df_to_save['safety_stock'] = 15
        
        if 'potensi_kerugian' in df_to_save.columns:
            df_to_save = df_to_save.drop(columns=['potensi_kerugian'])
        
        st.session_state.df_inventaris = df_to_save

st.caption("💡 **Tips:** Klik dua kali pada sel tabel untuk **mengubah data**. Untuk **menghapus barang**, centang kotak kecil di ujung kiri baris, lalu tekan tombol `Delete` atau `Backspace` di keyboard Anda.")