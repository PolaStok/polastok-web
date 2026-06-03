"""
utils/predictor.py
==================
Pipeline inferensi model ML PolaStok — embedded langsung di Streamlit.

Berisi:
  - PRODUCT_MAP     : Pemetaan nama produk UMKM → item_id Kaggle
  - load_rf_model() : Load model RF + scaler (@st.cache_resource)
  - load_history()  : Load historical_data.csv (@st.cache_data)
  - predict_rf()    : Inference loop Random Forest (N hari ke depan)
  - predict_lstm()  : Inference loop LSTM (N hari ke depan)

Catatan:
  - Feature engineering harus IDENTIK dengan saat training (src/features.py polastok-ml).
  - Tidak ada API terpisah — model dipanggil langsung via joblib.
"""

import json
import os
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
import streamlit as st

# ===========================================================
# PATH KONFIGURASI
# ===========================================================
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

RF_MODEL_PATH      = os.path.join(MODELS_DIR, "polastok_rf_model.pkl")
RF_SCALER_PATH     = os.path.join(MODELS_DIR, "minmax_scaler.pkl")
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "feature_names.json")
HISTORY_PATH       = os.path.join(MODELS_DIR, "historical_data.csv")
LSTM_MODEL_PATH    = os.path.join(MODELS_DIR, "polastok_lstm_model.keras")
LSTM_SCALER_PATH   = os.path.join(MODELS_DIR, "lstm_scaler.pkl")
LSTM_CONFIG_PATH   = os.path.join(MODELS_DIR, "lstm_config.json")

# ===========================================================
# PEMETAAN PRODUK UMKM → item_id & store_id (dataset Kaggle)
# Sesuaikan dengan produk nyata inventaris UMKM.
# ===========================================================
PRODUCT_MAP: dict[str, dict] = {
    "Produk A": {"item": 1,  "store": 1},
    "Produk B": {"item": 2,  "store": 1},
    "Produk C": {"item": 3,  "store": 1},
    "Produk D": {"item": 8,  "store": 1},
    "Produk E": {"item": 9,  "store": 1},
    "Produk F": {"item": 11, "store": 1},
}
DEFAULT_MAPPING = {"item": 1, "store": 1}

# LSTM config fallback
LSTM_WINDOW_SIZE = 30
LSTM_FEATURES    = ["sales", "day_of_week", "month"]


# ===========================================================
# FEATURE ENGINEERING (identik dengan polastok-ml/src/features.py)
# ===========================================================
ROLLING_WINDOWS = [7, 14, 30]
LAG_DAYS        = [7, 14, 30]
EWM_ALPHAS      = [0.95, 0.7, 0.5]
EWM_LAGS        = [7, 14, 30]


def _create_date_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"]          = df["date"].dt.month
    df["day_of_month"]   = df["date"].dt.day
    df["day_of_week"]    = df["date"].dt.dayofweek + 1   # 1=Senin, 7=Minggu
    df["week_of_year"]   = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"]        = df["date"].dt.quarter
    df["is_wknd"]        = (df["date"].dt.weekday >= 5).astype(int)
    df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
    df["is_month_end"]   = df["date"].dt.is_month_end.astype(int)
    df["season"]         = np.where(df["month"].isin([12, 1, 2]), 0,
                           np.where(df["month"].isin([3, 4, 5]),  1,
                           np.where(df["month"].isin([6, 7, 8]),  2, 3)))
    return df


def _add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for w in ROLLING_WINDOWS:
        df[f"sales_roll_mean_{w}"] = (
            df.groupby(["store", "item"])["sales"]
            .transform(lambda x: x.rolling(w, min_periods=1).mean().shift(1))
        )
    return df


def _add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for lag in LAG_DAYS:
        df[f"sales_lag_{lag}"] = (
            df.groupby(["store", "item"])["sales"]
            .transform(lambda x: x.shift(lag))
        )
    return df


def _add_ewm_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for alpha in EWM_ALPHAS:
        alpha_str = str(alpha).replace(".", "")
        for lag in EWM_LAGS:
            col = f"sales_ewm_alpha_{alpha_str}_lag_{lag}"
            df[col] = (
                df.groupby(["store", "item"])["sales"]
                .transform(
                    lambda x, a=alpha, l=lag: x.shift(l).ewm(
                        alpha=a, adjust=False
                    ).mean()
                )
            )
    return df


# ===========================================================
# LOAD ARTIFACTS — @st.cache_resource agar dimuat sekali saja
# ===========================================================
@st.cache_resource(show_spinner="Memuat model AI...")
def load_rf_model():
    """
    Load Random Forest model + scaler + feature names.
    Di-cache oleh Streamlit → hanya dimuat sekali per session.
    """
    model        = joblib.load(RF_MODEL_PATH)
    scaler       = joblib.load(RF_SCALER_PATH)
    with open(FEATURE_NAMES_PATH) as f:
        feature_names = json.load(f)
    return model, scaler, feature_names


@st.cache_data(show_spinner="Memuat data historis...")
def load_history() -> pd.DataFrame:
    """
    Load historical_data.csv (data penjualan 2013-2017).
    Di-cache oleh Streamlit → hanya dimuat sekali.
    """
    df = pd.read_csv(HISTORY_PATH, parse_dates=["date"])
    return df


@st.cache_resource(show_spinner="Memuat model LSTM...")
def load_lstm_model():
    """
    Load LSTM model + scaler + config.
    Import TensorFlow di sini agar tidak memperlambat startup
    jika LSTM tidak dipakai.
    """
    import tensorflow as tf  # noqa: F401

    model  = tf.keras.models.load_model(LSTM_MODEL_PATH)
    scaler = joblib.load(LSTM_SCALER_PATH)
    with open(LSTM_CONFIG_PATH) as f:
        config = json.load(f)
    return model, scaler, config


# ===========================================================
# INFERENCE — RANDOM FOREST
# ===========================================================
def predict_rf(
    nama_produk: str,
    horizon_days: int,
    start_date: datetime | None = None,
) -> list[int]:
    """
    Prediksi penjualan N hari ke depan menggunakan Random Forest.

    Strategi:
    - Ambil histori store-item dari historical_data.csv
    - Untuk setiap hari horizon: hitung fitur → scale → predict
    - Hasil prediksi dimasukkan ke histori untuk hari berikutnya

    Args:
        nama_produk  : Nama produk (dari PRODUCT_MAP atau nama bebas).
        horizon_days : Jumlah hari prediksi (7, 14, atau 30).
        start_date   : Tanggal awal prediksi. Default: 2018-04-01.

    Returns:
        List integer prediksi sales per hari.
    """
    rf_model, rf_scaler, feature_names = load_rf_model()
    history_df = load_history()

    mapping  = PRODUCT_MAP.get(nama_produk, DEFAULT_MAPPING)
    store_id = mapping["store"]
    item_id  = mapping["item"]

    if start_date is None:
        start_date = datetime(2018, 4, 1)

    # Filter histori untuk store-item yang dipilih
    hist = history_df[
        (history_df["store"] == store_id) &
        (history_df["item"]  == item_id)
    ].copy().sort_values("date").reset_index(drop=True)

    results = []

    for i in range(horizon_days):
        target_date = pd.Timestamp(start_date + timedelta(days=i))

        # Buat baris baru untuk hari yang diprediksi
        new_row = pd.DataFrame([{
            "date"  : target_date,
            "store" : store_id,
            "item"  : item_id,
            "sales" : np.nan,
        }])

        # Gabungkan ke histori lalu hitung semua fitur
        combined = pd.concat([hist, new_row], ignore_index=True)
        combined["date"] = pd.to_datetime(combined["date"])
        combined = combined.sort_values(["store", "item", "date"]).reset_index(drop=True)

        combined = _create_date_features(combined)
        combined = _add_rolling_features(combined)
        combined = _add_lag_features(combined)
        combined = _add_ewm_features(combined)

        # Ambil baris terakhir (hari yang diprediksi)
        last_row = combined.iloc[[-1]][feature_names].copy()
        last_row = last_row.fillna(0)

        # Scale → predict (pertahankan nama kolom agar tidak muncul warning)
        last_scaled_arr = rf_scaler.transform(last_row)
        last_scaled_df  = pd.DataFrame(last_scaled_arr, columns=feature_names)
        pred        = rf_model.predict(last_scaled_df)[0]
        pred_int    = max(0, round(float(pred)))
        results.append(pred_int)

        # Masukkan hasil ke histori untuk iterasi berikutnya
        new_hist_row = pd.DataFrame([{
            "date"  : target_date,
            "store" : store_id,
            "item"  : item_id,
            "sales" : float(pred_int),
        }])
        hist = pd.concat([hist, new_hist_row], ignore_index=True)

    return results


# ===========================================================
# INFERENCE — LSTM
# ===========================================================
def predict_lstm(
    nama_produk: str,
    horizon_days: int,
    start_date: datetime | None = None,
) -> list[int]:
    """
    Prediksi penjualan N hari ke depan menggunakan LSTM.

    Strategi:
    - Ambil 30 hari terakhir dari histori sebagai seed window
    - Predict satu hari → geser window → ulangi

    Args:
        nama_produk  : Nama produk.
        horizon_days : Jumlah hari prediksi.
        start_date   : Tanggal awal. Default: 2018-04-01.

    Returns:
        List integer prediksi sales per hari.
    """
    lstm_model, lstm_scaler, lstm_config = load_lstm_model()
    history_df = load_history()

    window_size   = lstm_config.get("window_size", LSTM_WINDOW_SIZE)
    lstm_features = lstm_config.get("features", LSTM_FEATURES)

    mapping  = PRODUCT_MAP.get(nama_produk, DEFAULT_MAPPING)
    store_id = mapping["store"]
    item_id  = mapping["item"]

    if start_date is None:
        start_date = datetime(2018, 4, 1)

    # Ambil histori dan tambahkan date features
    hist = history_df[
        (history_df["store"] == store_id) &
        (history_df["item"]  == item_id)
    ].copy().sort_values("date").reset_index(drop=True)
    hist = _create_date_features(hist)

    # Ambil window_size baris terakhir sebagai seed
    window_df = hist[lstm_features].tail(window_size).copy()
    window_df = pd.DataFrame(
        lstm_scaler.transform(window_df),
        columns=lstm_features
    )
    window = window_df.values.tolist()

    results = []

    for i in range(horizon_days):
        target_date = pd.Timestamp(start_date + timedelta(days=i))

        # Format input LSTM: (1, window_size, n_features)
        X = np.array([window], dtype=np.float32)

        # Predict (output dalam skala normalized)
        pred_scaled = lstm_model.predict(X, verbose=0)[0][0]

        # Inverse transform
        dummy       = np.zeros((1, len(lstm_features)))
        dummy[0, 0] = pred_scaled
        pred_real   = lstm_scaler.inverse_transform(dummy)[0][0]
        pred_int    = max(0, round(float(pred_real)))
        results.append(pred_int)

        # Buat baris baru dan geser window
        new_row_raw  = pd.DataFrame([{
            "date"  : target_date,
            "store" : store_id,
            "item"  : item_id,
            "sales" : float(pred_int),
        }])
        new_row_raw  = _create_date_features(new_row_raw)
        new_row_feat = new_row_raw[lstm_features].values
        new_row_scaled = lstm_scaler.transform(new_row_feat).tolist()[0]

        window.pop(0)
        window.append(new_row_scaled)

    return results


# ===========================================================
# WRAPPER UTAMA — dipanggil dari pages/3_Rekomendasi.py
# ===========================================================
def predict_demand(
    nama_produk: str,
    horizon_days: int,
    model_type: str = "rf",
) -> dict:
    """
    Entry point utama untuk prediksi demand.
    Dipanggil langsung dari halaman Rekomendasi Streamlit.

    Args:
        nama_produk  : Nama produk dari inventaris.
        horizon_days : 7, 14, atau 30 hari.
        model_type   : 'rf' atau 'lstm'.

    Returns:
        Dict berisi tanggal dan prediksi harian.
    """
    start_date = datetime(2018, 4, 1)
    dates = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(horizon_days)
    ]

    if model_type == "lstm":
        preds = predict_lstm(nama_produk, horizon_days, start_date)
    else:
        preds = predict_rf(nama_produk, horizon_days, start_date)

    return {
        "dates"       : dates,
        "predictions" : preds,
        "model_type"  : model_type,
        "produk"      : nama_produk,
        "horizon_days": horizon_days,
    }
