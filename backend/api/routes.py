from fastapi import APIRouter
from backend.api.register import registerUser

router = APIRouter()
router.add_api_route("/register", registerUser, methods=["POST"], summary="Registra un nuovo utente", description="Registra un nuovo utente nel sistema, estraendo l'embedding del volto dalla foto del documento fornita.")