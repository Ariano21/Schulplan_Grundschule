from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app.models import Halbjahr, HalbjahrStatus, Nutzer, Rolle

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class CurrentUser:
    def __init__(self, nutzer_id: int, rolle: Rolle, schule_id: int):
        self.nutzer_id = nutzer_id
        self.rolle = rolle
        self.schule_id = schule_id


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return CurrentUser(
        nutzer_id=int(payload["sub"]),
        rolle=Rolle(payload["rolle"]),
        schule_id=int(payload["schule_id"]),
    )


def require_schulleitung(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.rolle != Rolle.schulleitung:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur die Schulleitung darf diese Aktion ausführen.",
        )
    return user


def require_grunddaten_editierbar(
    user: CurrentUser = Depends(require_schulleitung),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """Grunddaten dürfen nur geändert werden, solange kein Halbjahr der Schule
    veröffentlicht oder in Abstimmung ist (Architektur-Dokument, Rollen & Rechte)."""
    aktives_halbjahr = (
        db.query(Halbjahr)
        .filter(
            Halbjahr.schule_id == user.schule_id,
            Halbjahr.status != HalbjahrStatus.entwurf,
        )
        .first()
    )
    if aktives_halbjahr is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Grunddaten sind gesperrt, solange ein Halbjahr in Abstimmung oder veröffentlicht ist.",
        )
    return user
