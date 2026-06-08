"""
utils/predictor.py
==================
Pipeline inferensi model ML PolaStok — embedded langsung di Streamlit.

Catatan arsitektur:
- Dataset asli: 10 store × 50 item (Kaggle Store Item Demand Forecasting)
- Di layer UI, 10 store diagregasi menjadi 1 toko tunggal (konteks UMKM)
- Model inference tetap menggunakan store=1 dari dataset asli
- Nama produk di-mapping via data/product_names.csv
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
NAME_MAP_PATH      = os.path.join(BASE_DIR, "data", "data_produk.csv")

# Store yang dipakai untuk inference (store 1 dari dataset asli)
INFERENCE_STORE = 1

# LSTM config fallback
LSTM_WINDOW_SIZE = 30
LSTM_FEATURES    = ["sales", "day_of_week", "month"]

# ===========================================================
# FEATURE ENGINEERING
# ===========================================================
ROLLING_WINDOWS = [7, 14, 30]
LAG_DAYS        = [7, 14, 30]
EWM_ALPHAS      = [0.95, 0.7, 0.5]
EWM_LAGS        = [7, 14, 30]


def _create_date_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"]          = df["date"].dt.month
    df["day_of_month"]   = df["date"].dt.day
    df["day_of_week"]    = df["date"].dt.dayofweek + 1
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
# LOAD ARTIFACTS
# ===========================================================

def _ensure_models_exist():
    if not os.path.exists(RF_MODEL_PATH) or not os.path.exists(HISTORY_PATH):
        try:
            from utils.download_models import download_if_missing
            download_if_missing()
        except Exception as e:
            st.error(f"Gagal memanggil auto-downloader: {str(e)}")


@st.cache_data(show_spinner=False)
def load_product_list() -> pd.DataFrame:
    _ensure_models_exist()
    df    = pd.read_csv(HISTORY_PATH, usecols=["item"])
    items = sorted(df["item"].unique())
    result = pd.DataFrame({
        "item":        items,
        "store":       INFERENCE_STORE,
        "nama_produk": [f"Produk {i}" for i in items],
        "harga":       0,
    })

    if os.path.exists(NAME_MAP_PATH):
        name_map = pd.read_csv(NAME_MAP_PATH)
        if "store" in name_map.columns:
            name_map = name_map.drop(columns=["store"])
        name_map = name_map.rename(columns={
            "nama_produk": "nama_mapped",
            "harga":       "harga_mapped"
        })
        result = result.merge(name_map, on="item", how="left")
        result["nama_produk"] = result["nama_mapped"].fillna(result["nama_produk"])
        result["harga"]       = result["harga_mapped"].fillna(0).astype(int)
        result = result[["nama_produk", "store", "item", "harga"]]

    return result


def get_mapping(nama_produk: str) -> dict:
    """Ambil store & item dari nama_produk."""
    product_list = load_product_list()
    row = product_list[product_list["nama_produk"] == nama_produk]
    if row.empty:
        row = product_list.iloc[[0]]
    return {
        "store": int(row["store"].values[0]),
        "item":  int(row["item"].values[0]),
    }
    
def load_rf_model():
    _ensure_models_exist()
    model  = joblib.load(RF_MODEL_PATH)
    scaler = joblib.load(RF_SCALER_PATH)
    with open(FEATURE_NAMES_PATH) as f:
        feature_names = json.load(f)
    return model, scaler, feature_names


@st.cache_data(show_spinner="Memuat data historis...")
def load_history() -> pd.DataFrame:
    _ensure_models_exist()
    return pd.read_csv(HISTORY_PATH, parse_dates=["date"])


@st.cache_resource(show_spinner="Memuat model LSTM...")
def load_lstm_model():
    _ensure_models_exist()
    import tensorflow as tf

    original_dense_from_config = tf.keras.layers.Dense.from_config

    def custom_dense_from_config(cls, config):
        if "quantization_config" in config:
            del config["quantization_config"]
        return original_dense_from_config(config)

    tf.keras.layers.Dense.from_config = classmethod(custom_dense_from_config)

    model  = tf.keras.models.load_model(LSTM_MODEL_PATH)
    scaler = joblib.load(LSTM_SCALER_PATH)
    with open(LSTM_CONFIG_PATH) as f:
        config = json.load(f)
    return model, scaler, config


# ===========================================================
# INFERENCE — RANDOM FOREST
# ===========================================================
def predict_rf(nama_produk: str, horizon_days: int, start_date: datetime) -> list[int]:
    rf_model, rf_scaler, feature_names = load_rf_model()
    history_df = load_history()

    mapping  = get_mapping(nama_produk)
    store_id = mapping["store"]
    item_id  = mapping["item"]

    hist = history_df[
        (history_df["store"] == store_id) &
        (history_df["item"]  == item_id)
    ].copy().sort_values("date").reset_index(drop=True)

    results = []
    for i in range(horizon_days):
        target_date = pd.Timestamp(start_date + timedelta(days=i))

        new_row  = pd.DataFrame([{"date": target_date, "store": store_id, "item": item_id, "sales": np.nan}])
        combined = pd.concat([hist, new_row], ignore_index=True)
        combined["date"] = pd.to_datetime(combined["date"])
        combined = combined.sort_values(["store", "item", "date"]).reset_index(drop=True)
        combined = _create_date_features(combined)
        combined = _add_rolling_features(combined)
        combined = _add_lag_features(combined)
        combined = _add_ewm_features(combined)

        last_row        = combined.iloc[[-1]][feature_names].copy().fillna(0)
        last_scaled_arr = rf_scaler.transform(last_row)
        last_scaled_df  = pd.DataFrame(last_scaled_arr, columns=feature_names)
        pred_int        = max(0, round(float(rf_model.predict(last_scaled_df)[0])))
        results.append(pred_int)

        hist = pd.concat([hist, pd.DataFrame([{
            "date": target_date, "store": store_id, "item": item_id, "sales": float(pred_int),
        }])], ignore_index=True)

    return results


# ===========================================================
# INFERENCE — LSTM
# ===========================================================
def predict_lstm(nama_produk: str, horizon_days: int, start_date: datetime) -> list[int]:
    lstm_model, lstm_scaler, lstm_config = load_lstm_model()
    history_df = load_history()

    window_size   = lstm_config.get("window_size", LSTM_WINDOW_SIZE)
    lstm_features = lstm_config.get("features", LSTM_FEATURES)

    mapping  = get_mapping(nama_produk)
    store_id = mapping["store"]
    item_id  = mapping["item"]

    hist = history_df[
        (history_df["store"] == store_id) &
        (history_df["item"]  == item_id)
    ].copy().sort_values("date").reset_index(drop=True)
    hist = _create_date_features(hist)

    window_df = hist[lstm_features].tail(window_size).copy()
    window    = pd.DataFrame(
        lstm_scaler.transform(window_df), columns=lstm_features
    ).values.tolist()

    results = []
    for i in range(horizon_days):
        target_date = pd.Timestamp(start_date + timedelta(days=i))
        X           = np.array([window], dtype=np.float32)
        pred_scaled = lstm_model.predict(X, verbose=0)[0][0]

        dummy       = np.zeros((1, len(lstm_features)))
        dummy[0, 0] = pred_scaled
        pred_real   = lstm_scaler.inverse_transform(
            pd.DataFrame(dummy, columns=lstm_features)
        )[0][0]
        pred_int = max(0, round(float(pred_real)))
        results.append(pred_int)

        new_row_raw    = _create_date_features(pd.DataFrame([{
            "date": target_date, "store": store_id, "item": item_id, "sales": float(pred_int),
        }]))
        new_row_scaled = lstm_scaler.transform(new_row_raw[lstm_features]).tolist()[0]
        window.pop(0)
        window.append(new_row_scaled)

    return results


# ===========================================================
# BUILD INVENTORY — agregasi semua store → 1 toko
# ===========================================================
@st.cache_data(show_spinner="Memuat data inventaris...")
def build_inventory() -> pd.DataFrame:
    history    = load_history()
    product_df = load_product_list()  # sudah include kolom harga jika ada

    last_date = history["date"].max()

    agg_30 = (
        history[history["date"] > last_date - pd.Timedelta(days=30)]
        .groupby("item")["sales"]
        .agg(demand_30d="sum", avg_daily="mean")
        .reset_index()
    )
    agg_7 = (
        history[history["date"] > last_date - pd.Timedelta(days=7)]
        .groupby("item")["sales"]
        .agg(demand_7d="sum")
        .reset_index()
    )

    df = agg_30.merge(agg_7, on="item", how="left")
    df = df.merge(product_df[["item", "nama_produk", "harga"]], on="item", how="left")

    q25 = df["avg_daily"].quantile(0.25)
    q75 = df["avg_daily"].quantile(0.75)

    df["status"]     = df["avg_daily"].apply(
        lambda v: "Kritis" if v <= q25 else ("Overstock" if v >= q75 else "Aman")
    )
    df["avg_daily"]  = df["avg_daily"].round(1)
    df["demand_30d"] = df["demand_30d"].astype(int)
    df["demand_7d"]  = df["demand_7d"].astype(int)
    df["harga"]      = df["harga"].fillna(0).astype(int)
    df["kategori"]   = "Umum"

    return df[["nama_produk", "item", "avg_daily", "demand_7d",
               "demand_30d", "status", "kategori", "harga"]]


# ===========================================================
# ENTRY POINT
# ===========================================================
def predict_demand(nama_produk: str, horizon_days: int, model_type: str = "rf") -> dict:
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(horizon_days)
    ]
    preds = predict_lstm(nama_produk, horizon_days, start_date) if model_type == "lstm" \
            else predict_rf(nama_produk, horizon_days, start_date)

    return {
        "dates":        dates,
        "predictions":  preds,
        "model_type":   model_type,
        "produk":       nama_produk,
        "horizon_days": horizon_days,
    }