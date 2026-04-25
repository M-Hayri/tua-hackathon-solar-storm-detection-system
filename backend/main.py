import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from ai_engine import SpaceWeatherInferenceEngine

# Uygulama başlatıldığında AI Motorunu başlatıyoruz
engine = SpaceWeatherInferenceEngine()

# Statik klasör oluştur (İmages, grad-cam vb.)
os.makedirs("static", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 TUA Uzay Havası YZ Komuta Sistemi Başlatıldı.")
    yield
    print("🛑 TUA Uzay Havası YZ Komuta Sistemi Durduruldu.")

app = FastAPI(title="TUA Space Weather Command Center API", lifespan=lifespan)

# CORS İzinleri (Frontend'den Fetch yapabilmek için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resim dosyalarını (current_heatmap.png) servis etmek için Statik Dosya modülü
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"message": "Space Weather API Runtime is active."}


@app.get("/api/status")
def get_system_status():
    """
    Called by the frontend every 2 seconds.
    Sözleşme API Formatı: {target_region, probability, alert_level, eta, impact_areas, active_protocols}
    """
    return engine.infer()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
