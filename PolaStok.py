import streamlit as st

st.set_page_config(
    page_title="PolaStok | Solusi Inventaris UMKM", 
    page_icon="assets/logo.png", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Hapus elemen default Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], header { display: none !important; }
    
    .stApp { background-color: #F8FAFC; }

    /* Paksa jarak biar rapat */
    .block-container { padding-top: 3rem !important; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* Styling card putih */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        padding: 40px !important;
        border-radius: 24px;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        border: 1px solid #E2E8F0;
        max-width: 420px; 
        margin: auto;
    }

    /* Styling Teks Input */
    .stTextInput label { color: #2E5077 !important; font-weight: 600; font-size: 14px !important; }
    .stTextInput input { border-radius: 10px !important; border: 1px solid #CBD5E1 !important; padding: 12px !important; }

    /* TOMBOL UTAMA (Tabel Ijo Solid - Pakai tipe Primary) */
    button[kind="primary"] {
        background-color: #4CA75B !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        height: 3.2em !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: 0.2s;
        box-shadow: 0 4px 6px -1px rgba(76, 167, 91, 0.3);
    }
    button[kind="primary"]:hover {
        background-color: #3d8649 !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

_, center, _ = st.columns([0.1, 1, 0.1])

with center:
    with st.container(border=True):
        
        logo_kiri, logo_tengah, logo_kanan = st.columns([0.15, 0.7, 0.15])
        with logo_tengah:
            st.image("assets/logo.png", use_column_width=True)
        
        st.markdown("<h3 style='text-align: center; color: #1E293B; margin-top: -10px; margin-bottom: 5px; font-weight: 700;'>Selamat Datang! 👋</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px; margin-bottom: 25px;'>Silakan masuk untuk memantau inventaris otomatis.</p>", unsafe_allow_html=True)
        
        user = st.text_input("Nama Pengguna", placeholder="Masukkan nama pengguna")
        pw = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
        
        st.write("") 
        
        if st.button("Masuk", type="primary", use_container_width=True):
            if user == "admin" and pw == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Nama pengguna atau kata sandi salah!")

if st.session_state.get('logged_in', False):
    st.switch_page("pages/1_Beranda.py")