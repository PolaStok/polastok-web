import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import load_sample_data

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Beranda | PolaStok", page_icon="assets/logo.png", layout="wide")
st.logo("assets/logo.png", size="large") # Kembalikan logo resmi

# Proteksi Login
if not st.session_state.get('logged_in', False):
    st.switch_page("PolaStok.py")

if 'nama_toko' not in st.session_state:
    st.session_state.nama_toko = 'Toko Anda'

# 2. CSS Figma-Look
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    .figma-card {
        background-color: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-bottom: 15px;
    }
    .card-label { color: #64748B; font-size: 14px; font-weight: 600; margin-bottom: 5px; }
    .card-value { color: #1E293B; font-size: 28px; font-weight: 800; margin: 0; }
    .card-footer { display: flex; align-items: center; font-size: 13px; font-weight: 600; margin-top: 12px; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0; padding: 20px !important; margin-bottom: 20px;
    }
    .custom-table-header { background-color: #F1F5F9; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 700; color: #1E293B; display: flex; justify-content: space-between; margin-bottom: 5px; }
    .custom-table-row { display: flex; justify-content: space-between; padding: 15px 16px; border-bottom: 1px solid #E2E8F0; }
    .custom-table-row:last-child { border-bottom: none; }
    [data-testid="stSidebarNav"] > div:first-child > span { font-size: 28px !important; font-weight: 900 !important; color: #1E293B !important; letter-spacing: -0.5px !important; margin-left: 10px; }
    @media (max-width: 768px) {
        .card-value { font-size: 22px !important; } .card-label { font-size: 12px !important; }
        [data-testid="stVerticalBlockBorderWrapper"] { padding: 15px 10px !important; } h2 { font-size: 24px !important; }
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar
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

# 4. Konten Utama
st.markdown(f"<h2 style='color: #1E293B; font-weight: 800; margin-bottom: 5px;'>👋 Halo, Selamat Datang di {st.session_state.nama_toko}!</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; font-size: 15px; margin-bottom: 25px;'>Ringkasan performa dan kondisi stok barang Anda hari ini.</p>", unsafe_allow_html=True)

df = load_sample_data()

def draw_card(label, value, footer_text, footer_color="#10B981", icon="📈"):
    st.markdown(f'<div class="figma-card"><p class="card-label">{label}</p><p class="card-value">{value}</p><div class="card-footer" style="color: {footer_color};"><span style="margin-right: 6px; font-size: 16px;">{icon}</span> {footer_text}</div></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: draw_card("Total Produk", f"{len(df)} Barang", "Semua Kategori", "#10B981", "📦")
with col2: draw_card("Stok Aman", f"{len(df[df['status']=='aman'])} Barang", "Kondisi Stabil", "#10B981", "✅")
with col3: draw_card("Stok Menipis", f"{len(df[df['status']=='kritis'])} Barang", "Segera Beli", "#EF4444", "⚠️")
with col4: draw_card("Prediksi AI", "92% Tepat", "Sangat Akurat", "#10B981", "🤖")

with st.container(border=True):
    st.markdown("<h4 style='color: #1E293B; margin-bottom: 5px;'>📊 Status Ketersediaan Barang</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 20px; margin-top: -5px;'>Perbandingan jumlah sisa stok untuk masing-masing produk.</p>", unsafe_allow_html=True)
    fig = px.bar(df.head(5), x="nama_produk", y="stok", color="status", color_discrete_map={"aman": "#2E5077", "kritis": "#EF4444", "overstock": "#F59E0B"}, template="plotly_white", text_auto=True)
    fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("<h4 style='color: #1E293B; display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>⚠️ Daftar Barang Harus Dibeli</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 15px; margin-top: -5px;'>Prioritaskan untuk menyetok ulang barang-barang di bawah ini:</p>", unsafe_allow_html=True)
    kritis_list = df[df['status'] == 'kritis']
    if not kritis_list.empty:
        html_table = '<div style="border-radius: 8px; border: 1px solid #E2E8F0; overflow: hidden;"><div class="custom-table-header"><span style="flex: 2; text-align: left; padding-left: 10px;">Nama Barang</span><span style="flex: 1; text-align: right; padding-right: 10px;">Sisa Stok</span></div>'
        for _, row in kritis_list.iterrows(): html_table += f'<div class="custom-table-row"><span style="flex: 2; color: #334155; text-align: left; font-size: 14px; font-weight: 600; padding-left: 10px;">{row["nama_produk"]}</span><span style="flex: 1; color: #EF4444; text-align: right; font-size: 15px; font-weight: 800; padding-right: 10px;">{row["stok"]}</span></div>'
        st.markdown(html_table + '</div>', unsafe_allow_html=True)
    else: st.info("Mantap! Tidak ada barang yang stoknya menipis saat ini. Kondisi toko aman. ✅")