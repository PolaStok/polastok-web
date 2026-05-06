"""
utils/preprocessing.py
Transformasi input dari UI sebelum dikirim ke model ML.
"""

import pandas as pd
import numpy as np


HORIZON_MAP = {
    "1 Bulan": 1,
    "2 Bulan": 2,
    "3 Bulan": 3,
}


def prepare_input(product_name: str, horizon: str) -> pd.DataFrame:
    """
    Siapkan input dalam format yang sesuai dengan model.
    
    TODO: Sesuaikan fitur dengan kolom yang dipakai saat training di polastok-ml.
    
    Args:
        product_name: Nama produk yang dipilih user
        horizon: String horizon prediksi ("1 Bulan", "2 Bulan", "3 Bulan")
    
    Returns:
        DataFrame 1 baris siap di-predict
    """
    horizon_val = HORIZON_MAP.get(horizon, 1)

    # TODO: Ganti dengan fitur yang sesuai dari training
    input_df = pd.DataFrame([{
        "horizon": horizon_val,
        "product_encoded": hash(product_name) % 100,  # placeholder encoding
        # Tambahkan fitur lain sesuai model
    }])

    return input_df
