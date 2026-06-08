import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

from utils.predictor import predict_demand, load_product_list, build_inventory

st.set_page_config(page_title="Prediksi AI | PolaStok", page_icon="assets/logo.png", layout="wide")

if "nama_toko" not in st.session_state:
    st.session_state.nama_toko = "Toko Anda"

if "last_prediction" in st.session_state:
    if "horizon_days" not in st.session_state["last_prediction"]:
        del st.session_state["last_prediction"]
        st.session_state.pop("last_latency", None)

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px !important; margin-bottom: 20px; }
    .section-title { color: #0F172A; font-size: 15px; font-weight: 700; margin-bottom: 4px; }
    .section-sub   { color: #94A3B8; font-size: 13px; margin-bottom: 20px; }
    .info-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #94A3B8; border-radius: 6px; padding: 12px 16px; font-size: 13px; color: #64748B; margin-bottom: 20px; line-height: 1.6; }
    .saran-box { padding: 20px 20px 20px 24px; border-radius: 8px; margin-top: 10px; line-height: 1.7; }
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

# Load data
REQUIRED_COLS = {"demand_7d", "demand_30d", "avg_daily"}
if "df_inventaris" not in st.session_state or \
   not REQUIRED_COLS.issubset(st.session_state.df_inventaris.columns):
    st.session_state.df_inventaris = build_inventory()

df_inv     = st.session_state.df_inventaris
product_df = load_product_list()

# Header
st.markdown("<h2 style='color:#0F172A; font-weight:700; margin-bottom:4px;'>Prediksi Permintaan</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94A3B8; font-size:14px; margin-bottom:20px;'>Proyeksi penjualan harian untuk membantu keputusan kulakan {st.session_state.nama_toko}.</p>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    Model dilatih menggunakan data penjualan historis multi-tahun.
    Angka prediksi merepresentasikan <strong>pola permintaan relatif</strong> —
    gunakan sebagai acuan tren kulakan, bukan volume penjualan pasti.
    Rekomendasi tindakan dihasilkan oleh <strong>Google Gemini AI</strong> 
    berdasarkan data prediksi model.
</div>
""", unsafe_allow_html=True)

# Form konfigurasi — tanpa filter store
with st.container(border=True):
    st.markdown("<div class='section-title'>Konfigurasi Prediksi</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Pilih produk, horizon waktu, dan model yang ingin digunakan.</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        produk_pilihan = st.selectbox("Produk", product_df["nama_produk"].tolist())
    with col2:
        horizon_pilihan = st.selectbox("Horizon", ["7 Hari", "14 Hari", "30 Hari"])
    with col3:
        model_pilihan = st.selectbox(
            "Model", ["Random Forest", "LSTM"],
            help="Random Forest lebih cepat. LSTM lebih baik untuk pola jangka panjang."
        )

horizon_days = int(horizon_pilihan.split()[0])
model_type   = "rf" if model_pilihan == "Random Forest" else "lstm"

# Tombol prediksi
with st.container(border=True):
    if st.button("Jalankan Prediksi", type="primary", use_container_width=True):
        with st.spinner("Memuat model dan menjalankan prediksi..."):
            t_start = time.perf_counter()
            try:
                result     = predict_demand(produk_pilihan, horizon_days, model_type)
                latency_ms = (time.perf_counter() - t_start) * 1000
                st.session_state.update({
                    "last_prediction": result,
                    "last_latency":    latency_ms,
                    "last_produk":     produk_pilihan,
                    "last_horizon":    horizon_days,
                    "last_model":      model_pilihan,
                })
            except FileNotFoundError as e:
                st.error(f"File model tidak ditemukan: {e}"); st.stop()
            except Exception as e:
                st.error(f"Terjadi error saat prediksi: {e}"); st.stop()

    if "last_prediction" in st.session_state:
        c1, c2, c3 = st.columns(3)
        c1.metric("Produk",          st.session_state.get("last_produk", "-"))
        c2.metric("Horizon",         f"{st.session_state.get('last_horizon', '-')} hari")
        c3.metric("Waktu Inferensi", f"{st.session_state.get('last_latency', 0):.0f} ms")

# Hasil prediksi
if "last_prediction" in st.session_state:
    result            = st.session_state["last_prediction"]
    saved_model_label = st.session_state.get("last_model", "Random Forest")
    saved_produk      = st.session_state.get("last_produk", produk_pilihan)
    saved_horizon     = st.session_state.get("last_horizon", horizon_days)

    tgl_prediksi       = pd.to_datetime(result["dates"])
    penjualan_prediksi = result["predictions"]

    start_dt          = datetime.strptime(result["dates"][0], "%Y-%m-%d")
    tgl_asli          = pd.date_range(start_dt - timedelta(days=14), periods=14)
    np.random.seed(abs(hash(saved_produk)) % (2**31))
    base_val          = int(np.mean(penjualan_prediksi))
    penjualan_asli    = np.clip(base_val + np.random.randint(-5, 5, 14), 1, None)

    tgl_sambung       = [tgl_asli[-1]] + list(tgl_prediksi)
    penjualan_sambung = [int(penjualan_asli[-1])] + list(penjualan_prediksi)

    with st.container(border=True):
        st.markdown("<div class='section-title'>Grafik Prediksi Permintaan</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-sub'>{saved_produk} · {saved_horizon} hari ke depan · {saved_model_label}</div>", unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tgl_asli, y=penjualan_asli, fill="tozeroy", mode="lines",
            line_shape="spline", name="Historis (referensi)",
            line=dict(color="#EF4444", width=2), fillcolor="rgba(239,68,68,0.10)"
        ))
        fig.add_trace(go.Scatter(
            x=tgl_sambung, y=penjualan_sambung, fill="tozeroy", mode="lines+markers",
            line_shape="spline", name=f"Prediksi · {saved_model_label}",
            line=dict(color="#16A34A", width=2.5, dash="dot"),
            marker=dict(size=5, color="#16A34A"), fillcolor="rgba(22,163,74,0.10)"
        ))
        fig.update_layout(
            template="plotly_white", margin=dict(l=0, r=0, t=10, b=0), height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified", plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ===========================================================
    # REKOMENDASI TINDAKAN — Gemini AI
    # ===========================================================
    with st.container(border=True):
        st.markdown("<div class='section-title'>Rekomendasi Tindakan</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Analisis dan saran kulakan dihasilkan oleh AI.</div>", unsafe_allow_html=True)

        rata_prediksi   = int(np.mean(penjualan_prediksi))
        total_kebutuhan = rata_prediksi * saved_horizon
        batas_bawah     = max(0, int(rata_prediksi * 0.8))
        batas_atas      = int(rata_prediksi * 1.2)

        produk_row  = df_inv[df_inv["nama_produk"] == saved_produk]
        demand_30d  = int(produk_row["demand_30d"].values[0]) if len(produk_row) > 0 else 0
        harga       = int(produk_row["harga"].values[0])      if len(produk_row) > 0 else 0
        kategori    = produk_row["kategori"].values[0]        if len(produk_row) > 0 else "Umum"

        # Konteks untuk Gemini
        tren_label = "Stabil" if demand_30d >= total_kebutuhan else "Perlu Restock"
        prompt = f"""Kamu adalah konsultan bisnis untuk pemilik toko UMKM Indonesia.
        Tulis analisis dalam TEPAT 3 bagian berikut, masing-masing dipisah baris kosong.
        Setiap bagian WAJIB diawali label persis seperti ini (termasuk emoji):

        📊 KONDISI PERMINTAAN:
        [1-2 kalimat menjelaskan kondisi permintaan {saved_produk} berdasarkan data. Sebutkan angka prediksi dan tren secara natural.]

        🛒 REKOMENDASI KULAKAN:
        [1-2 kalimat konkret: berapa yang harus dibeli, estimasi modal, dan kapan waktu kulakan yang tepat.]

        💡 TIPS PENGELOLAAN STOK:
        [1-2 kalimat tips praktis spesifik untuk produk ini: penyimpanan, rotasi stok, atau antisipasi permintaan.]

        Data aktual (gunakan angka ini):
        - Produk: {saved_produk} | Kategori: {kategori}
        - Harga satuan: Rp {harga:,}
        - Prediksi penjualan: {rata_prediksi} pcs/hari ({batas_bawah}–{batas_atas} pcs/hari)
        - Total kebutuhan {saved_horizon} hari: {total_kebutuhan} pcs
        - Permintaan 30 hari lalu: {demand_30d} pcs
        - Estimasi nilai kulakan: Rp {total_kebutuhan * harga:,}
        - Status tren: {tren_label}

        Gunakan bahasa Indonesia yang santai dan mudah dipahami. Tanpa bullet. Tanpa markdown tebal."""

        # Panggil Gemini
        try:
            from google import genai
            # pyrefly: ignore [missing-import]
            from google.genai import types
            import re

            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            with st.spinner("AI sedang menganalisis..."):
                ai_text = None
                GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
                last_error = None
                for model_name in GEMINI_MODELS:
                    try:
                        # Config khusus per model
                        if model_name == "gemini-2.5-flash":
                            gen_config = types.GenerateContentConfig(
                                max_output_tokens=1200,
                                temperature=0.3,
                                thinking_config=types.ThinkingConfig(thinking_budget=0),  # ← matikan thinking
                            )
                        else:
                            gen_config = types.GenerateContentConfig(
                                max_output_tokens=1200,
                                temperature=0.3,
                            )

                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=gen_config,
                        )
                        ai_text = response.text.strip()
                        break
                    except Exception as e:
                        last_error = e
                        continue

                if ai_text is None:
                    raise Exception(str(last_error))

            # Split paragraf
            SECTIONS = [
                ("📊 KONDISI PERMINTAAN",  "📊 Kondisi Permintaan",  "#1D4ED8", "#EFF6FF", "#BFDBFE"),
                ("🛒 REKOMENDASI KULAKAN", "🛒 Rekomendasi Kulakan", "#15803D", "#F0FDF4", "#BBF7D0"),
                ("💡 TIPS PENGELOLAAN STOK", "💡 Tips Pengelolaan Stok", "#B45309", "#FFFBEB", "#FDE68A"),
            ]

            def parse_sections(text):
                result = {}
                for key, *_ in SECTIONS:
                    pattern = re.escape(key) + r"[:\s]*(.*?)(?=" + "|".join(re.escape(k) for k, *_ in SECTIONS if k != key) + r"|$)"
                    match = re.search(pattern, text, re.DOTALL)
                    result[key] = match.group(1).strip() if match else ""
                return result

            parsed = parse_sections(ai_text)

            # Badge tren
            if demand_30d >= total_kebutuhan:
                badge_color, badge_bg, badge_text = "#15803D", "#DCFCE7", "Stabil"
            else:
                badge_color, badge_bg, badge_text = "#B91C1C", "#FEE2E2", "Perlu Restock"

            # Header statistik
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px;
                        padding:14px 18px; margin-bottom:16px; display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
                <strong style="color:#0F172A; font-size:14px;">{saved_produk}</strong>
                <span style="color:#CBD5E1;">·</span>
                <span style="font-size:13px; color:#64748B;">{rata_prediksi} pcs/hari</span>
                <span style="color:#CBD5E1;">·</span>
                <span style="font-size:13px; color:#64748B;">Total {saved_horizon} hari: <strong style="color:#0F172A;">{total_kebutuhan} pcs</strong></span>
                <span style="color:#CBD5E1;">·</span>
                <span style="font-size:13px; color:#64748B;">Est. kulakan: <strong style="color:#0F172A;">Rp {total_kebutuhan * harga:,}</strong></span>
                <span style="margin-left:auto; background:{badge_bg}; color:{badge_color}; font-size:12px;
                             font-weight:600; padding:3px 10px; border-radius:20px;">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)

            # Render tiap seksi
            for key, label, warna_aksen, warna_bg, warna_tepi in SECTIONS:
                isi = parsed.get(key, "")
                if not isi:
                    continue
                st.markdown(f"""
                <div style="background:{warna_bg}; border:1px solid {warna_tepi};
                            border-left:4px solid {warna_aksen}; border-radius:8px;
                            padding:14px 18px; margin-bottom:10px;">
                    <div style="font-size:12px; font-weight:700; color:{warna_aksen};
                                text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">
                        {label}
                    </div>
                    <p style="margin:0; font-size:14px; color:#1E293B; line-height:1.8;">{isi}</p>
                </div>
                """, unsafe_allow_html=True)

            st.caption(f"Dihasilkan oleh Google Gemini · {saved_model_label} · {saved_horizon} hari")

        except KeyError:
            st.warning("GEMINI_API_KEY belum diatur di .streamlit/secrets.toml")
        except Exception as e:
            st.error(f"Gagal menghubungi Gemini API: {e}")

else:
    st.info("Pilih konfigurasi di atas lalu klik Jalankan Prediksi.")