import streamlit as st

# 1. Konfigurasi Halaman & Nama Tab
st.set_page_config(
    page_title="PolaStok | Masuk", 
    page_icon="assets/logo.png", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 
st.markdown("""
<style>
    /* Hilangkan Sidebar & Header Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"], header { display: none !important; }
    
    .stApp { background-color: #F8FAFC; }

    /* Paksa Jarak Rapat */
    .block-container { padding-top: 3rem !important; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* Card Container Putih */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        padding: 35px 40px !important;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        max-width: 420px; /* Ukuran pas biar gak terlalu lebar */
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
    
    /* TOMBOL LINK (Tipe Secondary - Sejajar di Samping) */
    button[kind="secondary"] {
        background-color: transparent !important;
        color: #4CA75B !important;
        border: none !important;
        box-shadow: none !important;
        text-decoration: underline;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0 !important;
        margin-top: 8px !important; /* Biar sejajar tengah sama tombol ijo */
        text-align: left !important;
    }
    button[kind="secondary"]:hover {
        color: #2E5077 !important; /* Berubah navy pas disentuh */
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Mode
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'masuk'

# Konten Tengah
_, center, _ = st.columns([0.1, 1, 0.1])

with center:
    with st.container(border=True):
        # Logo PolaStok (Konsisten ada di halaman Masuk & Daftar)
        st.image("assets/logo.png", use_container_width=True)
        
        if st.session_state.auth_mode == 'masuk':
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px; margin-top: -15px; margin-bottom: 20px;'>Silakan masuk ke akun toko Anda</p>", unsafe_allow_html=True)
            
            # Input Fields (Full Bahasa Indonesia)
            user = st.text_input("Nama Pengguna", placeholder="Masukkan nama pengguna")
            pw = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
            
            st.write("") # Spasi
            
            # Layout Sampingan (Tombol Masuk & Daftar)
            col_btn, col_txt = st.columns([1.2, 1])
            
            with col_btn:
                # Perhatikan penambahan type="primary"
                if st.button("Masuk", type="primary"):
                    if user == "admin" and pw == "admin123":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Nama pengguna atau kata sandi salah!")
            
            with col_txt:
                st.markdown("<p style='font-size: 12px; color: #94A3B8; margin-bottom: -15px;'>Belum punya akun?</p>", unsafe_allow_html=True)
                # Perhatikan penambahan type="secondary"
                if st.button("Buat Akun Baru", type="secondary"):
                    st.session_state.auth_mode = 'daftar'
                    st.rerun()

        else:
            # Mode Registrasi
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px; margin-top: -15px; margin-bottom: 20px;'>Daftarkan toko Anda sekarang</p>", unsafe_allow_html=True)
            
            st.text_input("Nama Toko", placeholder="Contoh: Warung Berkah")
            st.text_input("Buat Nama Pengguna", placeholder="Gunakan huruf kecil tanpa spasi")
            st.text_input("Buat Kata Sandi", type="password", placeholder="Minimal 8 karakter")
            
            st.write("") # Spasi
            
            col_reg, col_back = st.columns([1.2, 1])
            with col_reg:
                if st.button("Buat akun baru", type="primary"):
                    st.success("Akun berhasil dibuat!")
                    st.session_state.auth_mode = 'masuk'
                    st.rerun()
            with col_back:
                st.markdown("<p style='font-size: 12px; color: #94A3B8; margin-bottom: -15px;'>Sudah ada akun?</p>", unsafe_allow_html=True)
                if st.button("Masuk di sini", type="secondary"):
                    st.session_state.auth_mode = 'masuk'
                    st.rerun()

# Redirect ke Dashboard kalau sudah login
if st.session_state.get('logged_in', False):
    st.switch_page("pages/1_dashboard.py")