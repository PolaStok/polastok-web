import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# 1. Konfigurasi
st.set_page_config(page_title="Prediksi AI | PolaStok", page_icon="assets/logo.png", layout="wide")
st.logo("assets/logo.png", size="large")

if not st.session_state.get('logged_in', False): st.switch_page("PolaStok.py")
if 'nama_toko' not in st.session_state: st.session_state.nama_toko = 'Toko Anda'

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; padding: 24px !important; margin-bottom: 20px; }
    [data-testid="stSidebarNav"] > div:first-child > span { font-size: 32px !important; font-weight: 900 !important; color: #1E293B !important; letter-spacing: -0.5px !important; margin-left: 10px; }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar
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

# 3. Konten Utama
st.markdown("<h2 style='color: #1E293B; font-weight: 800; margin-bottom: 5px;'>🔮 Rekomendasi Pintar AI</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748B; font-size: 15px; margin-bottom: 30px;'>Cari tahu perkiraan barang yang akan laku di masa depan agar <b>{st.session_state.nama_toko}</b> bisa bersiap kulakan.</p>", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1: produk_pilihan = st.selectbox("Pilih Barang:", ["Minyak Goreng 2L", "Beras Putih 5Kg", "Tepung Terigu 1Kg", "Gula Pasir 1Kg"])
    with col2: horizon_pilihan = st.selectbox("Perkiraan Untuk:", ["7 Hari Ke Depan", "14 Hari Ke Depan", "30 Hari Ke Depan"])

hari_lalu = 14
hari_depan = int(horizon_pilihan.split()[0])
tgl_asli = pd.date_range(datetime.now() - timedelta(days=hari_lalu), periods=hari_lalu)
tgl_prediksi = pd.date_range(datetime.now(), periods=hari_depan)

np.random.seed(len(produk_pilihan))
penjualan_asli = np.random.randint(20, 60, size=hari_lalu)
titik_terakhir = penjualan_asli[-1]
penjualan_prediksi = np.linspace(titik_terakhir, np.random.randint(40, 90), hari_depan) + np.random.randint(-8, 8, hari_depan)
penjualan_prediksi = np.clip(penjualan_prediksi, 5, None)

tgl_sambung = [tgl_asli[-1]] + list(tgl_prediksi)
penjualan_sambung = [titik_terakhir] + list(penjualan_prediksi)

with st.container(border=True):
    st.markdown("<h4 style='color: #1E293B; margin-bottom: 10px;'>Grafik Perkiraan Permintaan Pasar</h4>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tgl_asli, y=penjualan_asli, fill='tozeroy', mode='lines', line_shape='spline', name='Riwayat Penjualan', line=dict(color='#2E5077', width=3), fillcolor='rgba(46, 80, 119, 0.2)'))
    fig.add_trace(go.Scatter(x=tgl_sambung, y=penjualan_sambung, fill='tozeroy', mode='lines', line_shape='spline', name='Prediksi AI', line=dict(color='#4CA75B', width=3, dash='dot'), fillcolor='rgba(76, 167, 91, 0.2)'))
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=10, b=0), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#F1F5F9')
    st.plotly_chart(fig, use_container_width=True)
    
with st.container(border=True):
    st.markdown("<h4 style='color: #1E293B; margin-bottom: 5px;'>💡 Saran Tindakan untuk Anda</h4>", unsafe_allow_html=True)
    
    rata_prediksi = int(np.mean(penjualan_prediksi))
    total_kebutuhan = rata_prediksi * hari_depan
    sisa_stok_saat_ini = np.random.randint(10, 300) 
    
    if sisa_stok_saat_ini >= total_kebutuhan:
        status_stok, warna_box, warna_garis, warna_tepi = "<span style='color: #166534; font-weight: 800;'>AMAN ✅</span>", "#F0FDF4", "#4CA75B", "#BBF7D0"
        teks_saran = f"Sisa stok Anda di toko saat ini (<b>{sisa_stok_saat_ini} pcs</b>) diprediksi <b>masih mencukupi</b> untuk memenuhi total kebutuhan. Anda belum perlu mengeluarkan modal tambahan untuk kulakan barang ini."
    else:
        jumlah_beli = total_kebutuhan - sisa_stok_saat_ini
        status_stok, warna_box, warna_garis, warna_tepi = "<span style='color: #B91C1C; font-weight: 800;'>KURANG ⚠️</span>", "#FEF2F2", "#EF4444", "#FECACA"
        teks_saran = f"Sisa stok Anda di toko (<b>{sisa_stok_saat_ini} pcs</b>) <b>TIDAK AKAN CUKUP</b>. Kami menyarankan Anda untuk segera menyiapkan modal dan kulakan tambahan minimal <span style='color: #B91C1C; font-weight: 800; font-size: 16px;'>{jumlah_beli} pcs</span> agar toko tidak kehabisan barang."

    # Trik inset box shadow agar sudut membulat sempurna dan rapi
    st.markdown(f"""
    <div style="background-color: {warna_box}; border: 1px solid {warna_tepi}; box-shadow: inset 5px 0 0 0 {warna_garis}; padding: 20px 20px 20px 25px; border-radius: 8px; margin-top: 10px;">
        <div style="color: #1E293B; font-weight: 800; font-size: 16px; margin-bottom: 8px;">Analisis PolaStok AI untuk {st.session_state.nama_toko}:</div>
        <div style="color: #334155; font-size: 15px; line-height: 1.6;">
            Berdasarkan tren riwayat penjualan, sistem memperkirakan <b>{produk_pilihan}</b> akan terjual rata-rata <b>{rata_prediksi} pcs per hari</b>.<br>
            Total perkiraan barang yang akan laku selama {horizon_pilihan.lower()} adalah <b>{total_kebutuhan} pcs</b>.<br><br>
            Status Stok Saat Ini: {status_stok}<br>
            {teks_saran}
        </div>
    </div>
    """, unsafe_allow_html=True)