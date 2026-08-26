from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import CurrentUser, get_current_user, require_schulleitung
from app.models import Unterrichtseinheit
from app.schemas import Konflikt, UnterrichtseinheitCreate, UnterrichtseinheitOut

router = APIRouter(prefix="/unterrichtseinheiten", tags=["unterrichtseinheiten"])


def _finde_konflikte(db: Session, payload: UnterrichtseinheitCreate, ausgenommen_id: int | None = None) -> list[Konflikt]:
    """Prüft H1-H3 proaktiv, bevor die DB-UNIQUE-Constraints greifen, damit die
    API strukturierte Konfliktobjekte statt eines nackten Integrity-Errors liefert."""
    basis = db.query(Unterrichtseinheit).filter(
        Unterrichtseinheit.halbjahr_id == payload.halbjahr_id,
        Unterrichtseinheit.zeitslot_id == payload.zeitslot_id,
    )
    if ausgenommen_id is not None:
        basis = basis.filter(Unterrichtseinheit.id != ausgenommen_id)

    konflikte: list[Konflikt] = []

    lehrer_konflikt = basis.filter(Unterrichtseinheit.lehrer_id == payload.lehrer_id).first()
    if lehrer_konflikt is not None:
        konflikte.append(
            Konflikt(
                regel="H1",
                beschreibung="Lehrkraft ist in diesem Zeitslot bereits in einer anderen Unterrichtseinheit eingeplant.",
                kollidierende_einheit_id=lehrer_konflikt.id,
            )
        )

    gruppen_konflikt = basis.filter(Unterrichtseinheit.gruppe_id == payload.gruppe_id).first()
    if gruppen_konflikt is not None:
        konflikte.append(
            Konflikt(
                regel="H2",
                beschreibung="Gruppe hat in diesem Zeitslot bereits ein anderes Fach.",
                kollidierende_einheit_id=gruppen_konflikt.id,
            )
        )

    raum_konflikt = basis.filter(Unterrichtseinheit.raum_id == payload.raum_id).first()
    if raum_konflikt is not None:
        konflikte.append(
            Konflikt(
                regel="H3",
                beschreibung="Raum ist in diesem Zeitslot bereits belegt.",
                kollidierende_einheit_id=raum_konflikt.id,
            )
        )

    return konflikte


@router.post("", response_model=UnterrichtseinheitOut, status_code=status.HTTP_201_CREATED)
def create_unterrichtseinheit(
    payload: UnterrichtseinheitCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_schulleitung),
):
    konflikte = _finde_konflikte(db, payload)
    if konflikte:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Konflikt mit bestehendem Plan", "konflikte": [k.model_dump() for k in konflikte]},
        )

    obj = Unterrichtseinheit(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as exc:
        # Sicherheitsnetz gegen Race Conditions: die DB-UNIQUE-Constraints
        # (H1-H3) greifen auch, falls zwei Anfragen gleichzeitig ankommen.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Konflikt mit bestehendem Plan (gleichzeitige Änderung).",
        ) from exc
    db.refresh(obj)
    return obj


@router.get("", response_model=list[UnterrichtseinheitOut])
def list_unterrichtseinheiten(
    halbjahr_id: int, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)
):
    return db.query(Unterrichtseinheit).filter(Unterrichtseinheit.halbjahr_id == halbjahr_id).all()
