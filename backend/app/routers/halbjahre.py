from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import CurrentUser, get_current_user, require_schulleitung
from app.models import Halbjahr, HalbjahrStatus
from app.schemas import HalbjahrCreate, HalbjahrOut

router = APIRouter(prefix="/halbjahre", tags=["halbjahre"])


@router.post("", response_model=HalbjahrOut, status_code=status.HTTP_201_CREATED)
def create_halbjahr(
    payload: HalbjahrCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_schulleitung),
):
    # Status-Übergänge (Entwurf -> Abstimmung -> Veröffentlicht) sind laut
    # Fundament-Sprint außerhalb des Scopes; jedes neue Halbjahr startet als Entwurf.
    halbjahr = Halbjahr(
        schule_id=user.schule_id,
        start_datum=payload.start_datum,
        end_datum=payload.end_datum,
        status=HalbjahrStatus.entwurf,
    )
    db.add(halbjahr)
    db.commit()
    db.refresh(halbjahr)
    return halbjahr


@router.get("", response_model=list[HalbjahrOut])
def list_halbjahre(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return db.query(Halbjahr).filter(Halbjahr.schule_id == user.schule_id).all()
