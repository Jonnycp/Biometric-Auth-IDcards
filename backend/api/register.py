from fastapi import HTTPException, Request, UploadFile, File, Form
from PIL import Image, UnidentifiedImageError
import io

from backend.core.id_card import decodeImage, preprocessIDCard
from backend.core.face_detector import pipelineFaceDetection
from backend.core.face_recognizer import extractEmbeddings
from backend.database.models.user import User, UserResponse
from backend.database.user_controller import createUser

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"} 

async def registerUser(req: Request, 
                       idCardImage: UploadFile = File(..., description="Foto del documento"), 
                       fullName: str = Form(..., description="Nome e cognome dell'utente")):
    # 1. Lettura immagine
    image_bytes = await checkImageFile(idCardImage)
    image = decodeImage(image_bytes)
    if image is None:
       raise HTTPException(status_code=400, detail="File immagine non valido.")

    # 2. Preprocessi CIE
    processed_image, fixes = preprocessIDCard(image)

    # 3. Estrazione embedding
    recognizer = req.app.state.recognizer
    face, cropped_face = pipelineFaceDetection(recognizer, processed_image)
    embedding, score = extractEmbeddings(face)
    if embedding is None:
        raise HTTPException(status_code=400, detail="Nessun volto rilevato nell'immagine.")

    # 4. Salvataggio in db
    user = User(
        fullName=fullName,
        embedding=embedding.tolist(),
        score=score
    )
    result = createUser(user)

    # 5. Response
    return UserResponse(
        message="Utente registrato con successo.",
        user=user,
        score=score,
        fixProspective=fixes["prospective"],
        fixContrast=fixes["contrast"]
    )

async def checkImageFile(file: UploadFile):
    # 1. Verifica tipo MIME
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Formato non supportato. Carica un'immagine JPEG, PNG o WEBP."
        )

    # 2. Verifica dimensione file (unica lettura)
    image_bytes = await file.read(MAX_FILE_SIZE + 1)
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File troppo grande. La dimensione massima consentita è {MAX_FILE_SIZE // (1024 * 1024)} MB."
        )

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Il file caricato è vuoto.")

    # 3. Verifica integrità
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img_format = img.format
            img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="File immagine corrotto o non valido.")

    # Controlla il formato
    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Il contenuto del file ({img_format}) non corrisponde ai formati consentiti."
        )
        
    return image_bytes