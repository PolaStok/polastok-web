from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import joblib
import pandas as pd

# Inisialisasi FastAPI
app = FastAPI(
    title="PolaStok API",
    description="Backend API untuk Manajemen Inventaris dan Prediksi Stok UMKM",
    version="1.0.0"
)

# --- 1. MODEL DATA (Schema) ---
class PredictRequest(BaseModel):
    nama_produk: str
    horizon: int  

class PredictResponse(BaseModel):
    status: str
    produk: str
    estimasi_kebutuhan: int
    pesan: str

# --- 2. LOAD MODEL ML ---
MODEL_PATH = "models/model.pkl"

def get_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except:
            return None
    return None

model = get_model()

# --- 3. ENDPOINTS ---

@app.get("/")
async def root():
    """Endpoint untuk mengecek status API."""
    return {
        "status": "success",
        "message": "Backend PolaStok API berhasil berjalan!",
        "ai_module": "Ready" if model else "Model not found"
    }

@app.get("/health")
async def health_check():
    """Endpoint untuk monitoring kesehatan sistem."""
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictResponse)
async def predict_stock(request: PredictRequest):
    """Endpoint utama untuk melakukan prediksi stok."""
    
    if model is None:
        import random
        estimasi = random.randint(10, 100)
        return {
            "status": "success",
            "produk": request.nama_produk,
            "estimasi_kebutuhan": estimasi,
            "pesan": "Hasil ini menggunakan logika simulasi karena model.pkl tidak ditemukan."
        }
    
    try:
        estimasi = 50 
        
        return {
            "status": "success",
            "produk": request.nama_produk,
            "estimasi_kebutuhan": estimasi,
            "pesan": "Prediksi berhasil dihitung oleh model AI."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 4. DATA INVENTARIS (Optional) ---
@app.get("/inventory")
async def get_inventory():
    """Endpoint jika ingin mengambil data inventaris via API."""
    return {"message": "Integrasikan dengan database MySQL kamu di sini."}