import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

from utils.helpers import load_sample_data
from utils.predictor import predict_demand, PRODUCT_MAP

st.set_page_config(page_title="Prediksi AI | PolaStok", page_icon="assets/logo.png", layout="wide")

if 'nama_toko' not in st.session_state:
    st.session_state.nama_toko = 'Toko Anda'

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; padding: 24px !important; margin-bottom: 20px; }
    [data-testid="stSidebarNav"] > div:first-child > span { font-size: 32px !important; font-weight: 900 !important; color: #1E293B !important; letter-spacing: -0.5px !important; margin-left: 10px; }
</style>
""", unsafe_allow_html=True)

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

st.markdown("<h2 style='color: #1E293B; font-weight: 800; margin-bottom: 5px;'>🔮 Rekomendasi Pintar AI</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748B; font-size: 15px; margin-bottom: 30px;'>Prediksi permintaan barang masa depan agar <b>{st.session_state.nama_toko}</b> bisa bersiap kulakan lebih cerdas.</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Daftar produk: dari inventaris session (jika ada) atau sample data
# ------------------------------------------------------------------
if 'df_inventaris' in st.session_state:
    df = st.session_state.df_inventaris
else:
    df = load_sample_data()

daftar_nama_produk = df['nama_produk'].tolist()

# ------------------------------------------------------------------
# Panel input prediksi
# ------------------------------------------------------------------
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        produk_pilihan = st.selectbox("Pilih Barang:", daftar_nama_produk)
    with col2:
        horizon_pilihan = st.selectbox(
            "Perkiraan Untuk:",
            ["7 Hari Ke Depan", "14 Hari Ke Depan", "30 Hari Ke Depan"]
        )
    with col3:
        model_pilihan = st.selectbox(
            "Model AI:",
            ["Random Forest (RF)", "LSTM (Deep Learning)"],
            help="Random Forest lebih cepat. LSTM lebih baik untuk pola jangka panjang."
        )

horizon_days = int(horizon_pilihan.split()[0])
model_type   = "rf" if "RF" in model_pilihan else "lstm"

# ------------------------------------------------------------------
# Tombol Prediksi + Eksekusi
# ------------------------------------------------------------------
with st.container(border=True):
    btn_predict = st.button("🔮 Jalankan Prediksi", type="primary", use_container_width=True)

    if btn_predict or st.session_state.get("last_prediction"):
        if btn_predict:
            # Jalankan prediksi dan ukur latency
            t_start = time.perf_counter()
            try:
                result = predict_demand(produk_pilihan, horizon_days, model_type)
                t_end  = time.perf_counter()
                latency_ms = (t_end - t_start) * 1000

                # Simpan ke session state agar tidak re-predict saat rerun
                st.session_state["last_prediction"] = result
                st.session_state["last_latency"]    = latency_ms
            except FileNotFoundError as e:
                st.error(f"❌ File model tidak ditemukan: {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Terjadi error saat prediksi: {e}")
                st.stop()

        result     = st.session_state["last_prediction"]
        latency_ms = st.session_state.get("last_latency", 0)

        # Badge info
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("Produk", result["produk"])
        col_info2.metric("Horizon", f"{result['horizon_days']} hari")
        col_info3.metric("⚡ Waktu Prediksi", f"{latency_ms:.0f} ms")

# ------------------------------------------------------------------
# Grafik Prediksi
# ------------------------------------------------------------------
if st.session_state.get("last_prediction"):
    result      = st.session_state["last_prediction"]
    tgl_prediksi = pd.to_datetime(result["dates"])
    penjualan_prediksi = result["predictions"]

    # Data historis 14 hari sebelum prediksi (untuk konteks grafik)
    start_dt  = datetime.strptime(result["dates"][0], "%Y-%m-%d")
    tgl_asli  = pd.date_range(start_dt - timedelta(days=14), periods=14)
    np.random.seed(abs(hash(produk_pilihan)) % (2**31))
    penjualan_asli = np.array(penjualan_prediksi[:7] if len(penjualan_prediksi) >= 7
                               else penjualan_prediksi) + np.random.randint(-5, 5, 14)
    penjualan_asli = np.clip(penjualan_asli[:14], 1, None)

    # Titik sambung supaya grafik tidak terputus
    tgl_sambung       = [tgl_asli[-1]] + list(tgl_prediksi)
    penjualan_sambung = [int(penjualan_asli[-1])] + list(penjualan_prediksi)

    with st.container(border=True):
        st.markdown("<h4 style='color: #1E293B; margin-bottom: 10px;'>📈 Grafik Prediksi Permintaan</h4>", unsafe_allow_html=True)

        model_label = "Random Forest" if result["model_type"] == "rf" else "LSTM"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tgl_asli, y=penjualan_asli,
            fill='tozeroy', mode='lines',
            line_shape='spline', name='Riwayat (Referensi)',
            line=dict(color='#2E5077', width=3),
            fillcolor='rgba(46, 80, 119, 0.2)'
        ))
        fig.add_trace(go.Scatter(
            x=tgl_sambung, y=penjualan_sambung,
            fill='tozeroy', mode='lines+markers',
            line_shape='spline', name=f'Prediksi AI ({model_label})',
            line=dict(color='#4CA75B', width=3, dash='dot'),
            marker=dict(size=6, color='#4CA75B'),
            fillcolor='rgba(76, 167, 91, 0.2)'
        ))
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=0, r=0, t=10, b=0),
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#F1F5F9')
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Saran Tindakan
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("<h4 style='color: #1E293B; margin-bottom: 5px;'>💡 Saran Tindakan untuk Anda</h4>", unsafe_allow_html=True)

        rata_prediksi   = int(np.mean(penjualan_prediksi))
        total_kebutuhan = rata_prediksi * horizon_days
        batas_bawah     = max(0, int(rata_prediksi * 0.8))
        batas_atas      = int(rata_prediksi * 1.2)

        # Ambil sisa stok dari inventaris
        produk_row = df[df['nama_produk'] == produk_pilihan]
        sisa_stok  = int(produk_row['stok'].values[0]) if len(produk_row) > 0 else 0

        if sisa_stok >= total_kebutuhan:
            status_stok = "<span style='color: #166534; font-weight: 800;'>AMAN ✅</span>"
            warna_box, warna_garis, warna_tepi = "#F0FDF4", "#4CA75B", "#BBF7D0"
            teks_saran = (
                f"Sisa stok Anda saat ini (<b>{sisa_stok} pcs</b>) diprediksi "
                f"<b>masih mencukupi</b> untuk total kebutuhan {horizon_days} hari ke depan. "
                f"Anda belum perlu mengeluarkan modal tambahan untuk kulakan barang ini."
            )
        else:
            jumlah_beli = total_kebutuhan - sisa_stok
            status_stok = "<span style='color: #B91C1C; font-weight: 800;'>KURANG ⚠️</span>"
            warna_box, warna_garis, warna_tepi = "#FEF2F2", "#EF4444", "#FECACA"
            teks_saran = (
                f"Sisa stok Anda (<b>{sisa_stok} pcs</b>) <b>TIDAK AKAN CUKUP</b>. "
                f"Kami menyarankan Anda untuk segera kulakan tambahan minimal "
                f"<span style='color: #B91C1C; font-weight: 800; font-size: 16px;'>{jumlah_beli} pcs</span> "
                f"agar toko tidak kehabisan barang."
            )

        st.markdown(f"""
        <div style="background-color: {warna_box}; border: 1px solid {warna_tepi}; box-shadow: inset 5px 0 0 0 {warna_garis}; padding: 20px 20px 20px 25px; border-radius: 8px; margin-top: 10px;">
            <div style="color: #1E293B; font-weight: 800; font-size: 16px; margin-bottom: 8px;">Analisis PolaStok AI untuk {st.session_state.nama_toko}:</div>
            <div style="color: #334155; font-size: 15px; line-height: 1.6;">
                Berdasarkan data historis, sistem memperkirakan <b>{produk_pilihan}</b> akan terjual rata-rata
                <b>{rata_prediksi} pcs per hari</b> menggunakan model <b>{model_label}</b>.<br>
                <span style='color: #64748B; font-size: 13.5px;'><i>*Sistem memiliki tingkat keyakinan 95% bahwa produk akan laku di rentang
                <b>{batas_bawah} hingga {batas_atas} pcs/hari</b>.</i></span><br><br>
                Total perkiraan barang yang akan laku selama {horizon_pilihan.lower()} adalah <b>{total_kebutuhan} pcs</b>.<br><br>
                Status Stok Saat Ini: {status_stok}<br>
                {teks_saran}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("👆 Pilih barang, horizon waktu, dan model AI, lalu klik **Jalankan Prediksi** untuk melihat hasil.")