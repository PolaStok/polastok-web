import os
import gdown
import streamlit as st

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# ==============================================================================
# PENTING: Ganti ID Google Drive di bawah ini dengan ID file model yang asli!
# Pastikan file di Google Drive disetting "Anyone with the link can view"
# ==============================================================================
DRIVE_IDS = {
    "polastok_rf_model.pkl": "GANTI_DENGAN_ID_GDRIVE_RF_MODEL",
    "minmax_scaler.pkl": "GANTI_DENGAN_ID_GDRIVE_RF_SCALER",
    "feature_names.json": "GANTI_DENGAN_ID_GDRIVE_FEATURE_NAMES",
    "historical_data.csv": "GANTI_DENGAN_ID_GDRIVE_HISTORY_DATA",
    "polastok_lstm_model.keras": "GANTI_DENGAN_ID_GDRIVE_LSTM_MODEL",
    "lstm_scaler.pkl": "GANTI_DENGAN_ID_GDRIVE_LSTM_SCALER",
    "lstm_config.json": "GANTI_DENGAN_ID_GDRIVE_LSTM_CONFIG"
}

def download_if_missing():
    """
    Mengecek apakah file model tersedia. Jika tidak ada (misal di Cloud),
    akan mendownload otomatis dari Google Drive.
    """
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR, exist_ok=True)

    missing_files = []
    for filename in DRIVE_IDS.keys():
        file_path = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(file_path):
            missing_files.append(filename)

    if missing_files:
        st.info("🔄 Sistem mendeteksi file AI tidak tersedia di server. Mengunduh data dari Cloud (Google Drive)... Ini mungkin memakan waktu 1-2 menit.")
        
        progress_bar = st.progress(0)
        for i, filename in enumerate(missing_files):
            file_id = DRIVE_IDS[filename]
            output_path = os.path.join(MODELS_DIR, filename)
            
            if file_id.startswith("GANTI"):
                # Menghindari error gdown jika user lupa ganti ID dummy
                st.warning(f"⚠️ ID Google Drive untuk {filename} belum diatur. Silakan update di utils/download_models.py")
                continue
                
            try:
                st.text(f"Mendownload {filename}...")
                gdown.download(id=file_id, output=output_path, quiet=False)
            except Exception as e:
                st.error(f"Gagal mengunduh {filename}: {str(e)}")
                
            progress_bar.progress((i + 1) / len(missing_files))
            
        st.success("✅ Semua file berhasil diunduh. Aplikasi siap digunakan!")
        
if __name__ == "__main__":
    download_if_missing()
