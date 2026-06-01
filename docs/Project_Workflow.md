# PolaStok (SEDIAin) - Tactical Project Workflow 🚀

Workflow ini dirancang untuk memandu pengerjaan MVP (Minimum Viable Product) SEDIAin selama 6 minggu. Ini merupakan penjabaran dari dokumen *Project Plan* menjadi tugas-tugas taktis yang dapat diserahkan ke *Learning Path* masing-masing (Frontend, Backend, ML, dan Project Management).

## 📌 Minggu 1: Setup & Data Exploration (Fondasi)
**Fokus:** Mempersiapkan environment pengembangan, pembagian tugas eksplisit, dan analisis dataset dasar.

*   **Penyelesaian Setup Repositori** (Semua / PM)
    *   [x] Strukturisasi folder (`docs`, `src`, `data`, `tests`).
    *   [ ] Inisialisasi GitHub & Setup Git Flow (Main, Dev, Feature branches).
*   **Pemilihan Dataset** (Machine Learning)
    *   [ ] Mengunduh dataset public dari Kaggle ke `data/raw/`.
    *   [ ] Melakukan Exploratory Data Analysis (EDA) di `src/ml/notebooks/`.
    *   [ ] Membersihkan data (handling missing values, outliers) dan simpan ke `data/processed/`.
*   **Arsitektur & UI Mockup** (PM / Frontend / Backend)
    *   [ ] Membuat *Wireframe* / Mockup tampilan dashboard MVP.
    *   [ ] Merancang Contract API (dokumentasi endpoint yang dibutuhkan antara Backend & Frontend).

## 📌 Minggu 2: Baseline Model & Backend Initialization
**Fokus:** Membuat model ML dasar dan routing backend awal.

*   **Pengembangan Model AI Baseline** (Machine Learning)
    *   [ ] Membangun model *Time-Series Forecasting* dasar (Misal: ARIMA atau Prophet).
    *   [ ] Evaluasi akurasi model pertama (MAE/RMSE).
    *   [ ] Mengekspor model baseline dalam bentuk `model.pkl` atau format sejenis.
*   **Setup Rest API** (Backend)
    *   [ ] Setup kerangka framework Backend (misalnya FastAPI / Express).
    *   [ ] Melakukan integrasi CORS dan koneksi database dasar.
    *   [ ] Membuat Endpoint *Dummy* untuk testing Frontend (berdasarkan Contract API).
*   **Inisialisasi Antarmuka** (Frontend)
    *   [ ] Inisialisasi project Web Framework (Vue / React / Vanilla HTML+CSS).
    *   [ ] Konfigurasi komponen *Routing* (Halaman Login, Dashboard Dasar).

## 📌 Minggu 3: Integrasi Model ke API & Pengembangan Komponen UI
**Fokus:** Menghubungkan Backend dengan model ML dan mempercantik antarmuka.

*   **Deploy Model by API** (Backend & Machine Learning)
    *   [ ] Membuat endpoint API yang menerima input JSON (parameter demand) dan merespons hasil Prediksi ML (`/predict`).
    *   [ ] Menambahkan endpoint CRUD untuk *Inventaris Barang* (Tambah barang, Catat keluar masuk).
*   **Membangun Dashboard Inventaris** (Frontend)
    *   [ ] Membuat Tabel Daftar Inventaris.
    *   [ ] Mengkonsumsi Rest API backend menggunakan Fetch/Axios.
    *   [ ] Menambahkan fungsionalitas Status Stok (Color-coding: Merah = kritis, Hijau = aman).

## 📌 Minggu 4: Visualisasi Data & Model Tuning
**Fokus:** Membuat grafik tren di antarmuka dan meningkatkan akurasi dari model machine learning.

*   **Optimasi Model Time-Series** (Machine Learning)
    *   [ ] Melakukan hyperparameter tuning pada model (atau bereksperimen dengan model deep learning bertipe LSTM jika perlu).
    *   [ ] Menganalisis hasil prediksi untuk horizon 1-3 bulan ke depan secara lebih komprehensif.
*   **Implementasi Visualisasi Charts** (Frontend)
    *   [ ] Mengintegrasikan library Charting (Chart.js / ApexCharts).
    *   [ ] Membuat *Early Warning System* di UI (Peringatan alert untuk barang *understock* / *overstock*).
*   **Pengujian Integrasi** (Semua / PM)
    *   [ ] Memastikan request-response antara Frontend ➔ Backend ➔ ML Module berjalan lancar.

## 📌 Minggu 5: Testing, Bug Fixing, & Security
**Fokus:** Quality assurance dari MVP sebelum rilis final.

*   **System Testing** (QA / PM)
    *   [ ] Menulis Unit Tests dasar di Backend dan ML.
    *   [ ] Menguji coba User Flow dari layar Login hingga melihat rekomendasi stok (Manual testing / End-to-end testing).
    *   [ ] Evaluasi bug dan memperbaikinya.
*   **Finalisasi Dokumen Pendukung** (PM)
    *   [ ] Menyelesaikan laporan hasil uji.
    *   [ ] Menyelesaikan dokumen *Risk Management* & *Project Wrap-up*.

## 📌 Minggu 6: Rilis & Presentasi Final (Deployment)
**Fokus:** Merilis MVP ke Cloud agar dapat diakses secara publik dan siap dipresentasikan.

*   **Production Deployment** (Backend / Frontend)
    *   [ ] *Deploy* Backend & ML Model ke platform Cloud (misal: Railway, Render, atau Heroku).
    *   [ ] *Deploy* Frontend ke Vercel atau Netlify.
*   **Penulisan Slides & Simulasi Pitching** (Semua Tim)
    *   [ ] Berlatih demonstrasi live *SEDIAin*.
    *   [ ] Mematangkan Executive Summary & Slide Deck presentasi Final.

---
> **Catatan:** Jangan lupa adakan **Daily / Weekly Standup** (selama 15-30 menit) agar kemajuan tim tetap sejalan dengan timeline ini. 
