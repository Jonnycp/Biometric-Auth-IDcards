from fastapi import HTTPException, Request, UploadFile, File, Form

from backend.core.id_card import decodeImage, preprocessIDCard
from backend.core.face_detector import pipelineFaceDetection
from backend.core.face_recognizer import extractEmbeddings
from backend.database.models.user import User, UserResponse
from backend.database.user_controller import createUser

async def registerUser(req: Request, 
                       file: UploadFile = File(..., description="Foto del documento"), 
                       fullName: str = Form(..., description="Nome e cognome dell'utente")):
    # 1. Lettura immagine
    image_bytes = await file.read()
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
