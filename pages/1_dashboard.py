"""
pages/1_dashboard.py
Halaman Dashboard - ringkasan KPI dan status inventaris.
"""

import streamlit as st
import pandas as pd
from components.charts import plot_stock_trend
from components.alerts import show_stock_alerts
from utils.helpers import load_sample_data

st.set_page_config(page_title="Dashboard | PolaStok", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.caption("Ringkasan kondisi inventaris saat ini.")

# ─── Load Data ────────────────────────────────────────────────────────────────
df = load_sample_data()

# ─── KPI Cards ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Produk", len(df))
col2.metric("Stok Aman 🟢", len(df[df["status"] == "aman"]))
col3.metric("Stok Kritis 🔴", len(df[df["status"] == "kritis"]))
col4.metric("Stok Berlebih 🟡", len(df[df["status"] == "overstock"]))

st.divider()

# ─── Peringatan ───────────────────────────────────────────────────────────────
show_stock_alerts(df)

st.divider()

# ─── Grafik Tren ──────────────────────────────────────────────────────────────
st.subheader("📈 Tren Stok (7 Hari Terakhir)")
plot_stock_trend(df)
