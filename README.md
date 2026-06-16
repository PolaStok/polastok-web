# PolaStok — Smart Inventory & Demand Forecasting untuk UMKM

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

PolaStok adalah dashboard prediktif berbasis Machine Learning yang dirancang untuk membantu pemilik UMKM memahami pola permintaan produk dan mengambil keputusan kulakan yang lebih cerdas.

> Dikembangkan oleh **Tim PJK-GM041** sebagai proyek capstone program pelatihan AI Engineer Pijak Dicoding.

![PolaStok Beranda](assets/ui%20beranda.png)

---

## Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Catatan Dataset](#catatan-dataset)
- [Tech Stack](#tech-stack)
- [Struktur Folder](#struktur-folder)
- [Cara Menjalankan Lokal](#cara-menjalankan-lokal)
- [Cara Deploy ke Streamlit Community Cloud](#cara-deploy-ke-streamlit-community-cloud)
- [Konfigurasi API Key](#konfigurasi-api-key)
- [Tim Pengembang](#tim-pengembang)

---

## Fitur Utama

- **Dashboard Inventaris** — Ringkasan kondisi permintaan 50 produk berdasarkan data historis penjualan
- **Prediksi Demand** — Proyeksi penjualan harian 7, 14, atau 30 hari ke depan menggunakan Random Forest dan LSTM
- **Rekomendasi AI** — Analisis dan saran kulakan yang dihasilkan oleh Google Gemini AI berdasarkan hasil prediksi model
- **Embedded Inference** — Model ML berjalan langsung di memory Streamlit tanpa server API terpisah

---

## Arsitektur Sistem
polastok-web/

│

├── PolaStok.py                  # Halaman Beranda (entry point)

├── pages/

│   ├── 1_Inventaris.py          # Halaman daftar & status produk

│   └── 2_Rekomendasi.py         # Halaman prediksi demand + Gemini AI

│

├── utils/

│   ├── predictor.py             # Pipeline ML inference (RF & LSTM)

│   ├── helpers.py               # Fungsi bantu umum

│   └── download_models.py       # Auto-downloader model dari Google Drive

│

├── notebooks/

│   ├── PolaStok_ML.ipynb             # Notebook Pembangunan Model

├── models/                      # File model AI (tidak di-push ke GitHub)

│   ├── polastok_rf_model.pkl

│   ├── minmax_scaler.pkl

│   ├── feature_names.json

│   ├── historical_data.csv

│   ├── polastok_lstm_model.keras

│   ├── lstm_scaler.pkl

│   └── lstm_config.json

│

├── data/

│   └── product_names.csv        # Mapping item ID → nama produk UMKM

│

├── assets/                      # Logo dan gambar UI

├── .streamlit/

│   ├── config.toml              # Konfigurasi tema Streamlit

│   └── secrets.toml             # API key (TIDAK di-push ke GitHub)

├── requirements.txt

└── Dockerfile

---

## Catatan Dataset

Model ML dilatih menggunakan dataset publik [**Store Item Demand Forecasting Challenge**](https://www.kaggle.com/competitions/demand-forecasting-kernels-only) dari Kaggle — berisi 5 tahun data penjualan harian dari 10 toko dan 50 produk (2013–2017).

**Mengapa dataset ini?**
Dataset ini dipilih karena memiliki karakteristik pola demand yang bersifat universal: tren mingguan, pola musiman, dan variasi antar produk — karakteristik yang juga ditemukan di toko UMKM Indonesia.

**Penyesuaian untuk konteks UMKM:**
- 10 store dalam dataset diagregasi menjadi **1 representasi toko tunggal** di layer UI
- 50 item di-mapping ke nama produk FMCG/sembako yang relevan untuk warung Indonesia via `data/product_names.csv`
- Model inference tetap menggunakan `store=1` dari dataset asli untuk menjaga kualitas prediksi

**Skenario produksi:**
Dalam implementasi nyata, model akan di-*retrain* menggunakan data transaksi toko UMKM yang bersangkutan (minimal 6 bulan ke belakang) untuk menghasilkan prediksi yang benar-benar personal.

---

## Tech Stack

| Komponen | Library / Tool |
|---|---|
| App Framework | Streamlit 1.35.0 |
| Data Processing | Pandas 2.2.2, NumPy 1.26.4 |
| Machine Learning | Scikit-Learn 1.6.1 (Random Forest) |
| Deep Learning | TensorFlow-CPU, tf-keras (LSTM) |
| Visualisasi | Plotly 5.22.0 |
| Generative AI | Google Gemini API (google-genai) |
| Model Serialization | Joblib 1.4.2 |
| Cloud Download | gdown 5.2.0 |

---

## Cara Menjalankan Lokal

### Prasyarat

- Python 3.11
- Git
- Akses ke file model (lihat langkah 3)

### 1. Clone Repository

```bash
git clone https://github.com/PolaStok/polastok-web.git
cd polastok-web
```

### 2. Buat Virtual Environment

```bash
# Buat venv
python -m venv venv

# Aktifkan — Windows:
venv\Scripts\activate

# Aktifkan — Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Catatan:** Jika muncul warning konflik `scikit-learn`, jalankan:
> ```bash
> pip install scikit-learn==1.6.1
> ```

### 4. Siapkan File Model

File model tidak disimpan di GitHub karena ukurannya besar. Ada dua cara:

**Opsi A — Auto-download via script:**
```bash
python utils/download_models.py
```
> Pastikan ID Google Drive di `utils/download_models.py` sudah diisi dengan benar oleh tim.

**Opsi B — Download manual:**
Minta akses folder Google Drive kepada Tim Pijak, lalu letakkan file berikut di folder `models/`:
models/

├── polastok_rf_model.pkl

├── minmax_scaler.pkl

├── feature_names.json

├── historical_data.csv

├── polastok_lstm_model.keras

├── lstm_scaler.pkl

└── lstm_config.json

### 5. Konfigurasi API Key Gemini

Buat file `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "isi_api_key_kamu_di_sini"
```

> Dapatkan API key gratis di: https://aistudio.google.com/app/apikey
> 
> **Jangan pernah push file ini ke GitHub.**

### 6. Jalankan Aplikasi

```bash
streamlit run PolaStok.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

---

## Cara Deploy ke Streamlit Community Cloud

1. Fork atau push repository ini ke GitHub kamu
2. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan akun GitHub
3. Klik **New App**
4. Pilih repository dan branch `main`, set **Main file path** ke `PolaStok.py`
5. Klik **Advanced settings** → tab **Secrets**, isi:

```toml
GEMINI_API_KEY = "isi_api_key_kamu_di_sini"
```

6. Klik **Deploy**

> **Penting:** Pastikan ID Google Drive di `utils/download_models.py` sudah diisi sebelum deploy agar model ter-download otomatis saat server pertama kali berjalan.

---

## Konfigurasi API Key

File `.streamlit/secrets.toml.example` tersedia sebagai template:

```toml
# Salin file ini menjadi secrets.toml dan isi dengan nilai asli
GEMINI_API_KEY = "your_gemini_api_key_here"
```

Untuk deployment di Streamlit Community Cloud, secrets diatur melalui dashboard — tidak memerlukan file apapun di repo.

---

## Evaluasi Model

| Model | Metrik | Nilai |
|---|---|---|
| Random Forest | SMAPE | ~18% |
| LSTM | SMAPE | — |

> Nilai SMAPE RF dihitung pada test set periode 2017. Untuk detail lengkap proses training, lihat repository [polastok-ml](https://github.com/PolaStok/polastok-ml).

---

## Tim Pengembang (Pijak)

| Nama | Peran |
|---|---|
| Rizky Maulana Harahap | AI/ML — Data Preparation & Modeling |
| Muhamad Fadli Sirojudin | AI/ML — Training & Tuning |
| Fauzi Noorsyabani | Data Pipeline, System Integration, GitOps |
| Septian Samdani | QA Tester, Cloud Deployment |
| Agni Fatya Kholila | UI/UX & Web Frontend |

---

## Lisensi

Proyek ini dikembangkan untuk keperluan akademik sebagai syarat kelulusan program Pijak Dicoding 2026
