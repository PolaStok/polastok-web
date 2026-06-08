import streamlit as st
import pandas as pd
import plotly.express as px
from utils.predictor import build_inventory, load_history

st.set_page_config(page_title="Beranda | PolaStok", page_icon="assets/logo.png", layout="wide")

if "nama_toko" not in st.session_state:
    st.session_state.nama_toko = "Toko Anda"

st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    .metric-card { background-color: white; padding: 24px 28px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 16px; }
    .metric-label { color: #64748B; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .metric-value { color: #0F172A; font-size: 26px; font-weight: 700; margin: 0; line-height: 1; }
    .metric-sub   { color: #94A3B8; font-size: 12px; font-weight: 500; margin-top: 8px; }
    .metric-sub.green { color: #10B981; }
    .metric-sub.red   { color: #EF4444; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: white; border-radius: 12px; border: 1px solid #E2E8F0; padding: 24px !important; margin-bottom: 20px; }
    .section-title { color: #0F172A; font-size: 15px; font-weight: 700; margin-bottom: 4px; }
    .section-sub   { color: #94A3B8; font-size: 13px; margin-bottom: 20px; }
    .table-header  { background-color: #F8FAFC; padding: 10px 16px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 13px; color: #64748B; display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; }
    .table-row     { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #F1F5F9; }
    .table-row:last-child { border-bottom: none; }
    .badge-kritis  { background-color: #FEF2F2; color: #EF4444; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
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
REQUIRED_COLS = {"demand_7d", "demand_30d", "avg_daily", "kategori", "harga"}
if "df_inventaris" not in st.session_state or \
   not REQUIRED_COLS.issubset(st.session_state.df_inventaris.columns):
    st.session_state.df_inventaris = build_inventory()

df        = st.session_state.df_inventaris
last_date = load_history()["date"].max().strftime("%d %b %Y")

# Header
st.markdown(f"<h2 style='color:#0F172A; font-weight:700; margin-bottom:4px;'>{st.session_state.nama_toko}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#94A3B8; font-size:14px; margin-bottom:28px;'>Ringkasan kondisi permintaan produk · data s.d. {last_date}</p>", unsafe_allow_html=True)

# Metric cards
def draw_card(label, value, sub, sub_class=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub {sub_class}">{sub}</div>
    </div>""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: draw_card("Total Produk",  f"{len(df)}",                       "50 jenis barang")
with col2: draw_card("Demand Stabil", f"{len(df[df['status']=='Aman'])}",  "Penjualan normal",  "green")
with col3: draw_card("Demand Rendah", f"{len(df[df['status']=='Kritis'])}", "Perlu perhatian",   "red")
with col4: draw_card("Akurasi Model", "SMAPE ~18%",                        "Random Forest · Data Historis")

# Chart
with st.container(border=True):
    st.markdown("<div class='section-title'>Demand 30 Hari Terakhir</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>10 produk dengan total permintaan tertinggi.</div>", unsafe_allow_html=True)

    df_chart = df.sort_values("demand_30d", ascending=False).head(10)
    fig = px.bar(
        df_chart, x="nama_produk", y="demand_30d", color="status",
        color_discrete_map={"Aman": "#2E5077", "Kritis": "#EF4444", "Overstock": "#F59E0B"},
        template="plotly_white", text_auto=True,
        labels={"demand_30d": "Total Permintaan", "nama_produk": ""}
    )
    fig.update_traces(textfont_size=11, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0)
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        xaxis=dict(showgrid=False, tickangle=-30)
    )
    st.plotly_chart(fig, use_container_width=True)

# Tabel produk kritis
with st.container(border=True):
    st.markdown("<div class='section-title'>Produk dengan Demand Rendah</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Produk dengan rata-rata penjualan harian di bawah normal — perlu perhatian.</div>", unsafe_allow_html=True)

    kritis_df = df[df["status"] == "Kritis"].sort_values("avg_daily")

    if not kritis_df.empty:
        html  = '<div style="border:1px solid #E2E8F0; border-radius:8px; overflow:hidden;">'
        html += '<div class="table-header"><span style="flex:3">Produk</span><span style="flex:1;text-align:center">Avg/Hari</span><span style="flex:1;text-align:right">Total 30 Hari</span></div>'
        for _, row in kritis_df.iterrows():
            html += (
                f'<div class="table-row">'
                f'<span style="flex:3;font-size:14px;font-weight:600;color:#1E293B;">{row["nama_produk"]}</span>'
                f'<span style="flex:1;text-align:center;font-size:13px;color:#64748B;">{row["avg_daily"]} pcs</span>'
                f'<span style="flex:1;text-align:right;font-size:13px;color:#64748B;">{row["demand_30d"]} pcs&nbsp;&nbsp;<span class="badge-kritis">Rendah</span></span>'
                f'</div>'
            )
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.success("Semua produk memiliki demand yang stabil.")