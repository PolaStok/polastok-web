# PolaStok: Smart Inventory System untuk UMKM
> **Repository polastok-web** ini adalah bagian frontend (Streamlit) dari proyek PolaStok.

![PolaStok Beranda](assets/ui%20beranda.png)

PolaStok adalah aplikasi dashboard prediktif khusus untuk UMKM yang dapat memprediksi kapan barang akan habis terjual berdasarkan pola masa lalu. Ini adalah produk Minimum Viable Product (MVP) yang dikembangkan oleh Tim Pijak (Dicoding Capstone).

## 🚀 Fitur Utama
1. **Rekomendasi AI**: Menggunakan model *Machine Learning* (Random Forest & LSTM) untuk memprediksi angka penjualan harian hingga 30 hari ke depan.
2. **Status Inventaris Realtime**: Kategorisasi "Aman", "Kritis", dan "Overstock".
3. **Simulasi Budget Kulakan**: Secara pintar memprioritaskan barang mana yang harus dibeli sesuai sisa budget Anda.
4. **Embedded Inference Pipeline**: Model ML berjalan secara langsung di atas *memory* Streamlit menggunakan `joblib` tanpa memerlukan server API / Docker tambahan, membuatnya sangat cepat & murah.

---

## 🛠️ Tech Stack
- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Data & Feature Engineering**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn (Random Forest), TensorFlow-CPU (LSTM)
- **Visualisasi Grafik**: Plotly Express, Plotly Graph Objects

---

## 📂 Struktur Folder
```text
polastok-web/
├── PolaStok.py               # Halaman utama (Login)
├── pages/                    # Halaman dashboard (Beranda, Inventaris, Rekomendasi)
├── utils/
│   ├── helpers.py            # Fungsi bantu umum (load data dummy/inventaris)
│   ├── predictor.py          # Pipeline ML inference (RF & LSTM) embedded
│   └── download_models.py    # Auto-downloader dari Google Drive untuk server Cloud
├── models/                   # Tempat menaruh file model AI (.pkl, .keras, .csv)
├── data/                     # Dataset inventaris.csv
├── assets/                   # Gambar, icon, UI preview
└── requirements.txt          # Library Python yang dibutuhkan
```

---

## 💻 Cara Install & Run di Lokal (Local Development)

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/PolaStok/polastok-web.git
cd polastok-web

# Buat virtual environment (opsional tapi disarankan)
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Library
```bash
pip install -r requirements.txt
```

### 3. Siapkan File Model
Karena ukuran file model AI terlalu besar untuk disimpan di GitHub, Anda harus mendownloadnya secara manual atau via script:
- Jalankan script auto-downloader:
  ```bash
  python utils/download_models.py
  ```
- *Atau*, minta akses folder Google Drive kepada Tim Pijak dan masukkan file-file ini ke folder `models/`:
  - `polastok_rf_model.pkl` (7 MB)
  - `historical_data.csv` (18 MB)
  - `polastok_lstm_model.keras`
  - (beserta semua file scaler dan json)

### 4. Jalankan Aplikasi
```bash
streamlit run PolaStok.py
```
Aplikasi akan terbuka secara otomatis di browser pada `http://localhost:8501`.
- Username: `admin`
- Password: `admin123`

---

## ☁️ Cara Deploy ke Streamlit Community Cloud (Production)

Untuk *deployment*, kita menggunakan **Streamlit Community Cloud** (Gratis). 
Karena keterbatasan limit memori dan GitHub file size (maks 100MB per file), kita telah memodifikasi sistem ini agar melakukan **Auto-Download dari Google Drive** ketika server berjalan.

1. Buka [share.streamlit.io](https://share.streamlit.io/).
2. Hubungkan akun GitHub Anda.
3. Klik **New App**.
4. Pilih repository `PolaStok/polastok-web` dan branch `main`.
5. Di kolom `Main file path`, isikan `PolaStok.py`.
6. Klik **Deploy!**

> **PENTING UNTUK DEPLOYMENT:**
> Sebelum mendeploy, pastikan ID Google Drive di `utils/download_models.py` sudah diisi dengan link ID file GDrive yang asli. Jika model belum terdownload, `utils/predictor.py` akan otomatis memanggil *downloader script* tersebut.

---

## 👥 Tim Pengembang (Pijak)
- **Rizky Maulana Harahap** – AI/ML (Data Preparation & Modeling)
- **Muhamad Fadli Sirojudin** – AI/ML (Training & Tuning)
- **Fauzi Noorsyabani** – Data Pipeline, System Integration, GitOps
- **Septian Samdani** – QA Tester, Cloud Deployment
- **Agni Fatya Kholila** – UI/UX & Web Frontend
