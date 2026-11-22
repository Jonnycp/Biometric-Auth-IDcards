from pydantic import BaseModel, Field
from datetime import datetime, timezone

class User(BaseModel):
    fullName: str = Field(..., min_length=2, max_length=150, description="Nome e cognome dell'utente")
    score: float = Field(..., description="Punteggio di similarità del volto")
    embedding: list[float] = Field(..., description="Vettore embedding")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserPublic(BaseModel):
    fullName: str
    createdAt: datetime

    @classmethod
    def fromUser(cls, user):
        return cls(
            fullName=user.fullName,
            createdAt=user.createdAt
        )

class UserResult(BaseModel):
    isMatch: bool
    user: UserPublic | None = None
    similarity: float
    vectorScore: float | None = None

class UserResponse(BaseModel):
    message: str
    user: UserPublic | None = None
    score: float = 0.0
    fixProspective: bool = False
    fixContrast: bool = False
