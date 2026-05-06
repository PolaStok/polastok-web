"""
components/alerts.py
Komponen Early Warning System untuk stok kritis dan overstock.
"""

import streamlit as st
import pandas as pd


def show_stock_alerts(df: pd.DataFrame):
    """Tampilkan peringatan untuk produk kritis dan overstock."""
    kritis = df[df["status"] == "kritis"]
    overstock = df[df["status"] == "overstock"]

    if kritis.empty and overstock.empty:
        st.success("✅ Semua stok dalam kondisi aman.")
        return

    if not kritis.empty:
        with st.expander(f"🔴 Stok Kritis ({len(kritis)} produk)", expanded=True):
            for _, row in kritis.iterrows():
                st.error(f"**{row['nama_produk']}** — Sisa stok: {row['stok']} unit")

    if not overstock.empty:
        with st.expander(f"🟡 Overstock ({len(overstock)} produk)", expanded=False):
            for _, row in overstock.iterrows():
                st.warning(f"**{row['nama_produk']}** — Stok: {row['stok']} unit (melebihi batas)")
