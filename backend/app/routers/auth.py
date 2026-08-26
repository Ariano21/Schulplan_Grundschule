from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password
from app.database import get_db
from app.models import Nutzer
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    nutzer = db.query(Nutzer).filter(Nutzer.email == payload.email).first()
    if nutzer is None or not verify_password(payload.password, nutzer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort ist falsch.",
        )
    token = create_access_token(
        subject=str(nutzer.id), rolle=nutzer.rolle.value, schule_id=nutzer.schule_id
    )
    return TokenResponse(access_token=token, rolle=nutzer.rolle, schule_id=nutzer.schule_id)
