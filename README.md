# PolaStok (Smart Enterprise Data & Inventory Analytics)

## Ringkasan Eksekutif
PolaStok adalah platform digital berbasis Machine Learning (time-series forecasting) yang secara efektif memprediksi permintaan barang di masa depan bagi UMKM, guna menurunkan angka stockout (kekurangan barang) sekaligus memotong biaya penyimpanan inventaris berlebih.

## Struktur Direktori
```
📦 PolaStok
 ┣ 📂 data           # Berisi raw data (Kaggle dataset) dan data hasil preprocessing
 ┃ ┣ 📂 raw
 ┃ ┗ 📂 processed 
 ┣ 📂 docs           # Dokumentasi proyek (C4 Model, Project Plan, UI/UX Design)
 ┣ 📂 src            # Source code aplikasi (Frontend, Backend, dan Modul ML)
 ┃ ┣ 📂 frontend     # Dashboard Vue/React/HTML 
 ┃ ┣ 📂 backend      # RESTful API (FastAPI / Express / Laravel)
 ┃ ┗ 📂 ml           # Jupyter notebooks, script training, pkl files (Time-Series)
 ┗ 📂 tests          # Automation test & Unit testing 
```

## Anggota Tim
- Fauzi Noorsyabani (APC313D6Y0155)
- Septian Samdani (APC313D6Y0078)
- Agni Fatya Kholila (APC154D6X0062)
- Rizky Maulana Harahap (APC313D6Y0022)
- Muhamad Fadli Sirojudin (APC313D6Y0319)

## Cara Memulai Proyek
1. Clone repositori ini.
2. Ikuti instruksi di dalam `.md` files di masing-masing direktori src (frontend/backend).
3. Setup dataset Anda di dalam direktori `data/raw`.
