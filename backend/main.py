from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from backend.core.face_detector import initFaceRecognition
from backend.core.liveness import loadLivenessModel
from backend.api.routes import router

# COSTANTI
load_dotenv()
INSIGHTFACE_MODEL = os.getenv("INSIGHTFACE_MODEL") or "buffalo_l"
LIVENESS_MODEL_PATH = os.getenv("LIVENESS_MODEL_PATH") or ""
MONGODB_URI = os.getenv("MONGODB_URI") or ""
FRONTEND_URL = os.getenv("FRONTEND_URL") or "http://localhost:5173"
BACKEND_URL = "http://0.0.0.0:3000"

# LIVENESS SERVER
@asynccontextmanager
async def lifespan(app: FastAPI):
    if(not INSIGHTFACE_MODEL or not LIVENESS_MODEL_PATH or not MONGODB_URI):
        raise ValueError("INSIGHTFACE_MODEL, LIVENESS_MODEL_PATH e MONGODB_URI devono essere impostati nel .env")

    
    print(f"Using InsightFace model: {INSIGHTFACE_MODEL}")
    print(f"Using Liveness model: {LIVENESS_MODEL_PATH}")

    app.state.recognizer = initFaceRecognition(INSIGHTFACE_MODEL, (320, 320))
    app.state.livenessSession = loadLivenessModel(LIVENESS_MODEL_PATH)

    print(f"🔫 Live on {BACKEND_URL}")

    yield
    
    print("Shutting down...")


app = FastAPI(
    lifespan=lifespan, 
    title="ID Card Face Recognition API", 
    description="API per il riconoscimento facciale da carte di identità", 
    version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(router, prefix="/api")

# STARTING
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=BACKEND_URL.split(":")[1][2:], port=int(BACKEND_URL.split(":")[2]), reload=True)
