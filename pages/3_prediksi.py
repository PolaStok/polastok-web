"""
pages/3_prediksi.py
Halaman Prediksi - forecast demand menggunakan model ML.
"""

import streamlit as st
import pandas as pd
import joblib
import os
from utils.preprocessing import prepare_input
from utils.helpers import load_sample_data

st.set_page_config(page_title="Prediksi | PolaStok", page_icon="🔮", layout="wide")

st.title("🔮 Prediksi Kebutuhan Stok")
st.caption("Forecast demand produk untuk 1–3 bulan ke depan.")

# ─── Load Model ───────────────────────────────────────────────────────────────
MODEL_PATH = "models/model.pkl"

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

model = load_model()

if model is None:
    st.warning("⚠️ Model belum tersedia. Pastikan file `models/model.pkl` sudah ada.")
    st.stop()

# ─── Input Form ───────────────────────────────────────────────────────────────
df = load_sample_data()

with st.form("form_prediksi"):
    st.subheader("Parameter Prediksi")
    col1, col2 = st.columns(2)
    produk = col1.selectbox("Pilih Produk", df["nama_produk"].unique())
    horizon = col2.selectbox("Horizon Prediksi", ["1 Bulan", "2 Bulan", "3 Bulan"])
    submitted = st.form_submit_button("🚀 Prediksi Sekarang")

# ─── Hasil Prediksi ───────────────────────────────────────────────────────────
if submitted:
    with st.spinner("Menghitung prediksi..."):
        input_data = prepare_input(produk, horizon)
        prediction = model.predict(input_data)

    st.success("✅ Prediksi berhasil!")
    st.metric(f"Estimasi Demand — {horizon}", f"{int(prediction[0])} unit")

    st.info("💡 **Rekomendasi:** Segera lakukan reorder jika stok saat ini di bawah estimasi demand.")
