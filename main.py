from fastapi import FastAPI

app = FastAPI(
    title="PolaStok API",
    description=(
        "Backend API PolaStok. "
        "Catatan: Inference ML berjalan secara embedded di Streamlit (utils/predictor.py). "
        "Endpoint ini digunakan untuk health check dan monitoring deployment saja."
    ),
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "PolaStok API berjalan. ML inference berjalan di Streamlit (embedded).",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}