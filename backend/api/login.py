from fastapi import WebSocket, WebSocketException
from PIL import Image
from dotenv import load_dotenv
import io
import os

from backend.core.id_card import decodeImage
from backend.core.face_detector import pipelineFaceDetection
from backend.core.face_recognizer import extractEmbeddings
from backend.core.liveness import checkLiveness
from backend.api.register import MAX_FILE_SIZE, ALLOWED_FORMATS
from backend.database.user_controller import searchUser_byEmbedding

load_dotenv()
LIVENESS_THRESHOLD = float(os.getenv("LIVENESS_THRESHOLD", 0.6))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.45))

async def ws_loginUser(websocket: WebSocket):
    await websocket.accept()

    app = websocket.app
    recognizer = app.state.recognizer
    liveness_session = app.state.liveness_session

    try:
        while True:
            # 1. Ricevi frame
            image_bytes = await websocket.receive_bytes()
            validation_result = checkImageFrameWS(image_bytes)
            if not validation_result["valid"]:
                await websocket.send_json({"status": "ERROR", "message": validation_result["message"]})
                continue

            # 2. Decodifica immagine
            image = decodeImage(image_bytes)
            if image is None:
                await websocket.send_json({"status": "ERROR", "message": "Fotogramma non valido."})
                continue

            # 3. Face detection
            face, cropped_face = pipelineFaceDetection(recognizer, image)
            embedding, score = extractEmbeddings(face)
            if embedding is None or face is None:
                await websocket.send_json({"status": "WAITING_FACE", "message": "Nessun volto rilevato nell'immagine."})
                continue

            # 4. Liveness check
            liveness_result = checkLiveness(liveness_session, image, face.bbox, LIVENESS_THRESHOLD)
            if not liveness_result["is_live"]:
                await websocket.send_json({"status": "SPOOF_ATTACK", 
                                           "attack_type": liveness_result["attack_type"],
                                           "liveness_score": liveness_result["score"],
                                           "liveness_probabilities": liveness_result["probabilities"],
                                           "liveness_threshold": liveness_result["treshold"]
                                           })
                continue
            # 5. Cerca in db
            user_result = searchUser_byEmbedding(embedding, SIMILARITY_THRESHOLD)
            
            # 6. Risposta
            payload = {
                "status": "MATCH" if user_result.isMatch else "NO_MATCH",
                "attack_type": liveness_result["attack_type"],
                "similarity": round(user_result.similarity, 3),
                "liveness_score": round(liveness_result["score"], 3),
                "liveness_probabilities": liveness_result["probabilities"],
                "liveness_threshold": liveness_result["treshold"],
                "similarity_threshold": SIMILARITY_THRESHOLD,
                "vector_score": round(user_result.vectorScore, 3) if user_result.vectorScore is not None else 0.0,
                "embedding_score": round(score, 3),
                "user": user_result.user.model_dump() if user_result.user else None,
            }
            await websocket.send_json(payload)

    except WebSocketException as e:
       pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))

def checkImageFrameWS(frameBytes: bytes) -> dict[str, str | bool]:
    # Controlla se vuoto
    if(len(frameBytes) == 0):
        return {
            "valid": False,
            "message": "Fotogramma vuoto."
        }

    # Controlla dimensione
    if(len(frameBytes) > MAX_FILE_SIZE):
        return {
            "valid": False,
            "message": "Fotogramma troppo grande."
        }

    # Controlla se è un'immagine valida
    try:
        with Image.open(io.BytesIO(frameBytes)) as img:
            img_format = img.format
            img.verify()
    except Exception:
        return {
                    "valid": False,
                    "message": "Fotogramma corrotto o non valido."
                }
    
    # Controlla il formato
    if img_format not in ALLOWED_FORMATS:
        return {
            "valid": False,
            "message": f"Il contenuto del frame non corrisponde ai formati consentiti."
        }

    return {
        "valid": True,
        "message": "Fotogramma valido."
    }