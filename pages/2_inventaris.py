"""
pages/2_inventaris.py
Halaman Inventaris - tabel daftar barang dan manajemen stok.
"""

import streamlit as st
import pandas as pd
from utils.helpers import load_sample_data

st.set_page_config(page_title="Inventaris | PolaStok", page_icon="📦", layout="wide")

st.title("📦 Inventaris Barang")
st.caption("Daftar semua produk beserta status stok.")

# ─── Load Data ────────────────────────────────────────────────────────────────
df = load_sample_data()

# ─── Filter ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])
search = col1.text_input("🔍 Cari produk", placeholder="Nama produk...")
status_filter = col2.selectbox("Filter Status", ["Semua", "aman", "kritis", "overstock"])

if search:
    df = df[df["nama_produk"].str.contains(search, case=False)]
if status_filter != "Semua":
    df = df[df["status"] == status_filter]

# ─── Tabel dengan Color Coding ────────────────────────────────────────────────
def color_status(val):
    colors = {"aman": "background-color: #d4edda", "kritis": "background-color: #f8d7da", "overstock": "background-color: #fff3cd"}
    return colors.get(val, "")

st.dataframe(
    df.style.applymap(color_status, subset=["status"]),
    use_container_width=True,
    height=400,
)

st.caption(f"Menampilkan {len(df)} produk")
