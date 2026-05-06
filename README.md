# 🌐 PolaStok Web

Aplikasi web PolaStok berbasis **Streamlit** untuk visualisasi inventaris, prediksi stok, dan sistem peringatan dini.

---

## 📁 Struktur Folder

```
polastok-web/
├── PolaStok.py                     # Entry point utama Streamlit
├── pages/
│   ├── 1_dashboard.py         # KPI & ringkasan inventaris
│   ├── 2_inventaris.py        # Tabel daftar & manajemen stok
│   └── 3_prediksi.py          # Prediksi demand dari model ML
├── components/
│   ├── charts.py              # Fungsi grafik (Plotly)
│   └── alerts.py              # Komponen peringatan stok
├── models/
│   └── model.pkl              # Model ML (copy dari polastok-ml)
├── utils/
│   ├── preprocessing.py       # Transformasi input sebelum prediksi
│   └── helpers.py             # Fungsi bantu umum
├── data/
│   └── sample_data.csv        # Data contoh untuk demo
├── assets/                    # Logo, gambar
├── .streamlit/
│   └── config.toml            # Konfigurasi tema Streamlit
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Environment

```bash
# 1. Clone repo
git clone https://github.com/PolaStok/polastok-web.git
cd polastok-web

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Aplikasi

```bash
streamlit run PolaStok.py
```

Buka browser: `http://localhost:8501`

---

## 🔮 Setup Model Prediksi

Salin file model dari repo `polastok-ml` setelah proses training selesai:

```bash
cp ../polastok-ml/models/model.pkl models/model.pkl
```

> ⚠️ Tanpa `model.pkl`, halaman Prediksi tidak akan berfungsi.

---

## 🖥️ Halaman Aplikasi

| Halaman    | File                    | Deskripsi                       |
| ---------- | ----------------------- | ------------------------------- |
| Dashboard  | `pages/1_dashboard.py`  | KPI stok, tren, peringatan dini |
| Inventaris | `pages/2_inventaris.py` | Tabel produk + filter status    |
| Prediksi   | `pages/3_prediksi.py`   | Forecast demand 1–3 bulan       |

---

## ☁️ Deployment (Streamlit Cloud)

1. Push ke branch `main`
2. Buka [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pilih repo `PolaStok/polastok-web`, branch `main`, file `PolaStok.py`
4. Klik **Deploy**

---

## 🌿 Git Flow

| Branch         | Kegunaan                    |
| -------------- | --------------------------- |
| `main`         | Production-ready            |
| `dev`          | Pengembangan aktif          |
| `feature/nama` | Fitur baru → merge ke `dev` |
