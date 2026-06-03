# Laporan Validasi Latency — PolaStok (SCRUM-19)

## Ringkasan

| Metrik | Target | Hasil Aktual |
|---|---|---|
| Prediksi RF (cold start — load model + data) | < 15 detik | ~11 detik ✅ |
| Prediksi RF (warm — model sudah di-cache) | < 2 detik | ~530 ms ✅ |
| Prediksi LSTM (cold start) | < 20 detik | *TBD* |
| Prediksi LSTM (warm) | < 5 detik | *TBD* |

## Detail Pengujian

### Random Forest — 7 Hari
- Cold start (load model + prediksi): *TBD* ms
- Warm (model sudah di-cache): *TBD* ms

### Random Forest — 14 Hari
- Warm: *TBD* ms

### Random Forest — 30 Hari
- Warm: *TBD* ms

### LSTM — 7 Hari
- Cold start (termasuk load TensorFlow): *TBD* ms
- Warm: *TBD* ms

## Strategi Mitigasi Latency

1. **@st.cache_resource** — Model RF dan LSTM di-load sekali saja, tidak diulang setiap prediksi
2. **@st.cache_data** — `historical_data.csv` (18MB) di-load sekali per session
3. **Prediksi batch** — Semua hari horizon diprediksi sekaligus, bukan satu-satu via UI
4. **Session state** — Hasil prediksi disimpan di `st.session_state` agar tidak re-predict saat user scroll

## Catatan Deployment

- Model file (`.pkl`, `.keras`, `historical_data.csv`) **tidak di-push ke Git** (masuk `.gitignore`)
- Untuk deployment Streamlit Community Cloud: file model perlu tersedia (via Google Drive atau dikecualikan dari .gitignore)
