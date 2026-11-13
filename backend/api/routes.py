from fastapi import APIRouter
from fastapi import status

from backend.database.models.user import UserResponse, UserResult
from backend.api.register import registerUser
from backend.api.login import ws_loginUser

router = APIRouter()

router.add_api_route("/register", 
                     registerUser, 
                     methods=["POST"], 
                     response_model=UserResponse, 
                     status_code=status.HTTP_201_CREATED, 
                     summary="Registra un nuovo utente",
                     description="Registra un nuovo utente nel sistema, estraendo l'embedding del volto dalla foto del documento fornita.")

router.add_api_websocket_route("/login",
                               ws_loginUser,
                                 name="Realtime login")