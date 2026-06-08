import streamlit as st
import pandas as pd
from utils.predictor import build_inventory

st.set_page_config(page_title="Inventaris | PolaStok", page_icon="assets/logo.png", layout="wide")

if "nama_toko" not in st.session_state:
    st.session_state.nama_toko = "Toko Anda"

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px !important; margin-bottom: 20px; }
    .section-title { color: #0F172A; font-size: 15px; font-weight: 700; margin-bottom: 4px; }
    .section-sub   { color: #94A3B8; font-size: 13px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/logo.png", width=200)
    st.markdown("---")
    with st.popover("Pengaturan Toko", use_container_width=True):
        with st.form("form_pengaturan"):
            new_name = st.text_input("Nama Toko", value=st.session_state.nama_toko)
            if st.form_submit_button("Simpan", type="primary"):
                st.session_state.nama_toko = new_name
                st.rerun()

# Paksa rebuild jika struktur kolom lama
REQUIRED_COLS = {"demand_7d", "demand_30d", "avg_daily", "kategori", "harga"}
if "df_inventaris" not in st.session_state or \
   not REQUIRED_COLS.issubset(st.session_state.df_inventaris.columns):
    st.session_state.df_inventaris = build_inventory()

# Header
st.markdown("<h2 style='color:#0F172A; font-weight:700; margin-bottom:4px;'>Inventaris Produk</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94A3B8; font-size:14px; margin-bottom:24px;'>Data permintaan produk berdasarkan histori penjualan · {st.session_state.nama_toko}</p>", unsafe_allow_html=True)

# Filter
col_search, col_status, _ = st.columns([2, 1, 3])
with col_search:
    search_query = st.text_input("Cari produk", placeholder="Cari nama produk...", label_visibility="collapsed")
with col_status:
    status_filter = st.selectbox("Status", ["Semua Status", "Aman", "Kritis", "Overstock"], label_visibility="collapsed")

df_display = st.session_state.df_inventaris.copy()
if search_query:
    df_display = df_display[df_display["nama_produk"].str.contains(search_query, case=False, na=False)]
if status_filter != "Semua Status":
    df_display = df_display[df_display["status"] == status_filter]

# Tabel
with st.container(border=True):
    st.markdown("<div class='section-title'>Daftar Produk</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Kolom Kategori dan Harga Satuan dapat diedit langsung.</div>", unsafe_allow_html=True)

    cols_show = ["nama_produk", "item", "avg_daily", "demand_7d", "demand_30d", "status", "kategori", "harga"]

    edited_df = st.data_editor(
        df_display[cols_show],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "nama_produk": st.column_config.TextColumn("Nama Produk",        width="large",  disabled=True),
            "item":        st.column_config.NumberColumn("ID Produk",         width="small",  disabled=True),
            "avg_daily":   st.column_config.NumberColumn("Rata-rata/Hari",    width="small",  disabled=True, format="%.1f"),
            "demand_7d":   st.column_config.NumberColumn("Permintaan 7 Hari", width="small",  disabled=True),
            "demand_30d":  st.column_config.NumberColumn("Permintaan 30 Hari",width="medium", disabled=True),
            "status":      st.column_config.TextColumn("Status",              width="small",  disabled=True),
            "kategori":    st.column_config.SelectboxColumn(
                               "Kategori", width="small",
                               options=["Umum", "Sembako", "Minuman", "Snack", "Kebersihan", "Rokok", "Lainnya"]
                           ),
            "harga":       st.column_config.NumberColumn("Harga Satuan (Rp)", width="medium", format="%d", min_value=0),
        }
    )

    # Simpan perubahan kategori & harga
    if not edited_df.equals(df_display[cols_show]):
        for _, row in edited_df.iterrows():
            mask = st.session_state.df_inventaris["item"] == row["item"]
            st.session_state.df_inventaris.loc[mask, "kategori"] = row["kategori"]
            st.session_state.df_inventaris.loc[mask, "harga"]    = row["harga"]

# Ringkasan
with st.container(border=True):
    st.markdown("<div class='section-title'>Ringkasan</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Produk", len(df_display))
    c2.metric("Aman",         len(df_display[df_display["status"] == "Aman"]))
    c3.metric("Kritis",       len(df_display[df_display["status"] == "Kritis"]),
              delta=f"{len(df_display[df_display['status']=='Kritis'])} perlu perhatian" if len(df_display[df_display["status"]=="Kritis"]) > 0 else None,
              delta_color="inverse")
    c4.metric("Overstock",    len(df_display[df_display["status"] == "Overstock"]),
              delta=f"{len(df_display[df_display['status']=='Overstock'])} kelebihan" if len(df_display[df_display["status"]=="Overstock"]) > 0 else None,
              delta_color="inverse")