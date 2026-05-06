"""
utils/helpers.py
Fungsi bantu umum yang digunakan di seluruh aplikasi.
"""

import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """
    Load data inventaris.
    Prioritas: data/inventaris.csv → data/sample_data.csv (fallback dummy).
    """
    for path in ["data/inventaris.csv", "data/sample_data.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)

    # Fallback: data dummy agar aplikasi tetap bisa dijalankan
    return pd.DataFrame({
        "nama_produk": ["Produk A", "Produk B", "Produk C", "Produk D"],
        "stok": [150, 8, 300, 45],
        "stok_minimum": [50, 10, 50, 30],
        "stok_maksimum": [200, 100, 250, 150],
        "status": ["aman", "kritis", "overstock", "aman"],
        "satuan": ["pcs", "pcs", "pcs", "pcs"],
    })


def classify_status(stok: int, minimum: int, maksimum: int) -> str:
    """Klasifikasi status stok berdasarkan threshold."""
    if stok < minimum:
        return "kritis"
    elif stok > maksimum:
        return "overstock"
    return "aman"
