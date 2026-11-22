from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from PIL import Image
from dotenv import load_dotenv
import io
import os

from backend.core.id_card import decodeImage
from backend.core.face_detector import pipelineFaceDetection
from backend.core.face_recognizer import computeEmbedding
from backend.core.liveness import checkLiveness
from backend.api.register import MAX_FILE_SIZE, ALLOWED_FORMATS
from backend.database.user_controller import searchUser_byEmbedding

load_dotenv()
LIVENESS_THRESHOLD = float(os.getenv("LIVENESS_THRESHOLD", 0.6))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.45))
FRAMES_LIVENESS = int(os.getenv("FRAMES_LIVENESS", 45))
MAX_SPOOF_ATTACKS = int(os.getenv("MAX_SPOOF_ATTACKS", 10))
STATIC_THRESHOLD = float(os.getenv("STATIC_THRESHOLD", 0.0005))

async def ws_loginUser(websocket: WebSocket):
    await websocket.accept()

    app = websocket.app
    recognizer = app.state.recognizer
    liveness_session = app.state.livenessSession

    #PARAMETRI LIVENESS
    liveness_scores = []
    kps_history = []
    best_frame = None
    best_face = None
    best_score = -1.0
    perc_kps_variance = 0.0
    spoof_attack_detected_count = 0

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
            face, cropped_face = pipelineFaceDetection(recognizer, image, det_only=True)
            if face is None:
                liveness_scores.clear()
                kps_history.clear()
                best_frame = None
                best_face = None
                best_score = -1.0
                spoof_attack_detected_count = 0
                
                await websocket.send_json({"status": "WAITING_FACE", "message": "Nessun volto rilevato nell'immagine."})
                continue

            # 4. Liveness check
            liveness_result = checkLiveness(liveness_session, image, face.bbox, LIVENESS_THRESHOLD)

            # 4.1 Aggiorna punteggi liveness e fotogramma migliore
            liveness_scores.append(liveness_result["score"])
            kps_history.append(face.kps)
            if float(face.det_score) > best_score:
                best_score = float(face.det_score)
                best_frame = image
                best_face = face
            progress = int((len(liveness_scores) / FRAMES_LIVENESS) * 100)

            if not liveness_result["is_live"]:
                spoof_attack_detected_count += 1

            # 4.2 Listen frames for liveness
            print(f"Frame {len(liveness_scores)}/{FRAMES_LIVENESS} - Liveness score: {liveness_result['score']:.3f} - Progress: {progress}% - Spoof attacks detected: {spoof_attack_detected_count}/{MAX_SPOOF_ATTACKS}")
            if len(liveness_scores) < FRAMES_LIVENESS:
                if(spoof_attack_detected_count > MAX_SPOOF_ATTACKS):
                    await websocket.send_json({"status": "SPOOF_ATTACK", 
                                               "attack_type": liveness_result["attack_type"],
                                               "liveness_score": round(liveness_result["score"], 3),
                                               "liveness_probabilities": liveness_result["probabilities"],
                                               "liveness_threshold": liveness_result["treshold"],
                                               "liveness_static_variance": perc_kps_variance,
                                               "liveness_progress": progress
                                               })
                    liveness_scores.clear()
                    kps_history.clear()
                    best_frame = None
                    best_face = None
                    best_score = -1.0
                    spoof_attack_detected_count = 0
                    continue
                else:
                    await websocket.send_json({"status": "WAITING_LIVENESS", 
                                               "liveness_score": round(liveness_result["score"], 3),
                                               "liveness_probabilities": liveness_result["probabilities"],
                                               "liveness_threshold": liveness_result["treshold"],
                                               "liveness_static_variance": perc_kps_variance,
                                               "liveness_progress": progress
                                               })
                    continue
            else:
                avg_liveness_score = sum(liveness_scores) / len(liveness_scores)
                kps_variance = calculateKpsVariance(kps_history)
                perc_kps_variance = 100 - round(min(100.0, (kps_variance / STATIC_THRESHOLD) * 100), 2)
                print("Average liveness score:", avg_liveness_score, "KPS variance:", kps_variance)

                liveness_scores.clear()
                kps_history.clear()
                spoof_attack_detected_count = 0

                is_liveness_ok = avg_liveness_score >= LIVENESS_THRESHOLD
                is_motion_ok = kps_variance > STATIC_THRESHOLD

                if not (is_liveness_ok and is_motion_ok):
                    if not is_liveness_ok:
                        reason = liveness_result["attack_type"]
                    else:
                        reason = "STATIC_FACE"

                    await websocket.send_json({"status": "SPOOF_ATTACK", 
                                               "attack_type": reason,
                                               "liveness_score": round(avg_liveness_score, 3),
                                               "liveness_probabilities": liveness_result["probabilities"],
                                               "liveness_threshold": liveness_result["treshold"],
                                               "liveness_static_variance": round(perc_kps_variance, 3),
                                               "liveness_progress": progress
                                               })
                    best_frame = None
                    best_face = None
                    best_score = -1.0
                    continue
                
                # 5. Cerca in db
                if best_frame is None or best_face is None:
                    await websocket.send_json({"status": "ERROR", "message": "Nessun volto valido trovato."})
                    continue
                best_embedding, _ = computeEmbedding(recognizer, best_frame, best_face)
                best_frame = None
                best_face = None
                if best_embedding is None:
                    best_score = -1.0
                    await websocket.send_json({"status": "ERROR", "message": "Nessun embedding valido trovato."})
                    continue

                user_result = searchUser_byEmbedding(best_embedding, SIMILARITY_THRESHOLD)
                
                # 6. Risposta
                payload = {
                    "status": "MATCH" if user_result.isMatch else "NO_MATCH",
                    "attack_type": liveness_result["attack_type"],
                    "similarity": round(user_result.similarity, 3),
                    "liveness_score": round(avg_liveness_score, 3),
                    "liveness_probabilities": liveness_result["probabilities"],
                    "liveness_threshold": liveness_result["treshold"],
                    "liveness_static_variance": round(perc_kps_variance, 3),
                    "similarity_threshold": SIMILARITY_THRESHOLD,
                    "vector_score": round(user_result.vectorScore, 3) if user_result.vectorScore is not None else 0.0,
                    "embedding_score": round(best_score, 3),
                    "user": user_result.user.model_dump(mode="json") if user_result.user and (user_result.similarity >= SIMILARITY_THRESHOLD-0.10) else None,
                }
                await websocket.send_json(payload)
                break #termina la connessione

    except (WebSocketException, WebSocketDisconnect) as e:
       pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e)[:120])

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

import numpy as np

# Calcola microvarianza kps
def calculateKpsVariance(kps_history: list[np.ndarray]) -> float:
    kps = np.array(kps_history, dtype=np.float32)  # Shape: (N, 5, 2)
    if len(kps) < 5:
        return 0.0

    # Estrai le coordinate X di occhio dx (0), occhio sx (1) e naso (2) su tutti i frame
    right_eye_x = kps[:, 0, 0]
    left_eye_x  = kps[:, 1, 0]
    nose_x      = kps[:, 2, 0]

    eye_widths = left_eye_x - right_eye_x

    # Filtra eventuali frame anomali dove gli occhi sono troppo vicini o invertiti
    valid_mask = eye_widths >= 10.0
    if np.sum(valid_mask) < 5:
        return 0.0

    # Calcola il rapporto Yaw per ogni frame valido (~0.5 quando guardi dritto)
    yaw_values = (nose_x[valid_mask] - right_eye_x[valid_mask]) / eye_widths[valid_mask]

    # Restituisce la deviazione standard dello Yaw (identica a mov_std dello script)
    return float(np.std(yaw_values))
