"""
app.py
Entry point utama aplikasi PolaStok.
Jalankan: streamlit run app.py
"""

import streamlit as st

# ─── Konfigurasi Halaman ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="PolaStok",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.image("assets/logo.png", use_column_width=True) if __import__("os").path.exists("assets/logo.png") else None
st.sidebar.title("📦 PolaStok")
st.sidebar.caption("Sistem Prediksi & Manajemen Stok")

# ─── Halaman Utama ────────────────────────────────────────────────────────────
st.title("📦 Selamat Datang di PolaStok")
st.markdown(
    """
    **PolaStok** adalah sistem cerdas untuk membantu UMKM dalam:
    - 📊 Memantau kondisi stok secara real-time
    - 🔮 Memprediksi kebutuhan stok ke depan
    - 🚨 Mendapatkan peringatan dini *understock* / *overstock*

    ---
    Gunakan menu di **sidebar kiri** untuk navigasi.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Produk", "—", help="Jumlah produk terdaftar")
col2.metric("Stok Kritis", "—", help="Produk dengan stok di bawah threshold")
col3.metric("Akurasi Model", "—", help="Akurasi prediksi model ML terakhir")
