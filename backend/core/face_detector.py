from insightface.app import FaceAnalysis
import numpy as np

# Inizializza FaceRecognition (ctx_id = -1 -> CPU)
def initFaceRecognition(model: str = "buffalo_l", det_size: tuple[int, int] = (320, 320)) -> FaceAnalysis:
    app = FaceAnalysis(name=model, root="../.insightface", allowed_modules=['detection', 'recognition'])
    app.prepare(ctx_id=-1, det_size=det_size)
    return app

# Estrae facce immagine
def getFaces(detector: FaceAnalysis, image: np.ndarray):
    if image is None or image.size == 0:
        return []
    return detector.get(image)

# Estrae faccia più grande
def getMainFace(faces: list):
    # ogni face ha:
    # .bbox: (x1, y1, x2, y2)
    # .det_score: confidenza rilevamento
    # .embedding: vettore embedding del volto
    # .kps: punti chiave del volto (occhi, naso, bocca)

    if not faces:
        return None
    return max(faces, key=lambda face: (face.bbox[2]-face.bbox[0]) * (face.bbox[3]-face.bbox[1])) #area più grande

# Ritaglio bbox faccia
def cropFace(image: np.ndarray, bbox: np.ndarray, margin_perc: int = 0):
    x1, y1, x2, y2 = bbox
    h, w = image.shape[:2]

    if margin_perc > 0:
        margin_x = int((x2 - x1))
        margin_y = int((y2 - y1))
        x1 = int(max(0, x1 - margin_x))
        y1 = int(max(0, y1 - margin_y))
        x2 = int(min(w, x2 + margin_x))
        y2 = int(min(h, y2 + margin_y))
    else:
        x1 = int(max(0, x1))
        y1 = int(max(0, y1))
        x2 = int(min(w, x2))
        y2 = int(min(h, y2))
    
    crop = image[y1:y2, x1:x2]
    
    if crop.size <= 0:
        return None
    return crop

def pipelineFaceDetection(detector: FaceAnalysis, image: np.ndarray):
    faces = getFaces(detector, image)
    mainFace = getMainFace(faces)
    if mainFace is None:
        return None, image
    
    croppedImgFace = cropFace(image, mainFace.bbox) 
    return mainFace, croppedImgFace