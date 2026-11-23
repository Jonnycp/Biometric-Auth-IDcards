from insightface.app import FaceAnalysis
from insightface.app.common import Face
import numpy as np

# Inizializza FaceRecognition (ctx_id = -1 -> CPU)
def initFaceRecognition(model: str = "buffalo_l", det_size: tuple[int, int] = (320, 320)) -> FaceAnalysis:
    app = FaceAnalysis(name=model, root="backend/.insightface", allowed_modules=['detection', 'recognition'], providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=det_size)
    return app

# Estrae facce immagine
def getFaces(detector: FaceAnalysis, image: np.ndarray, det_only: bool = False):
    if image is None or image.size == 0:
        return []
    if det_only:
        assert detector.det_model is not None, "Chiamare initFaceRecognition() prima di getFaces()"
        bboxes, kpss = detector.det_model.detect(image, max_num=0, metric="default")
        if bboxes.shape[0] == 0:
            return []
        faces = [
            Face(bbox=bboxes[i, 0:4],
                kps=kpss[i] if kpss is not None else None,
                det_score=bboxes[i, 4])
            for i in range(bboxes.shape[0])
        ]
        return faces
    else:
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

def pipelineFaceDetection(detector: FaceAnalysis, image: np.ndarray, det_only: bool = False):
    faces = getFaces(detector, image, det_only=det_only)
    #print(faces[0].kps[0][0] - faces[0].kps[1][0] if faces else "No faces detected")
    mainFace = getMainFace(faces)
    if mainFace is None:
        return None, image
    
    croppedImgFace = cropFace(image, mainFace.bbox) 
    return mainFace, croppedImgFace