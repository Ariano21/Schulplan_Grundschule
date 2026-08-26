from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import CurrentUser, get_current_user, require_grunddaten_editierbar
from app.models import Fach, Gruppe, Klasse, Lehrer, Raum, Zeitslot
from app.schemas import (
    FachCreate,
    FachOut,
    GruppeCreate,
    GruppeOut,
    KlasseCreate,
    KlasseOut,
    LehrerCreate,
    LehrerOut,
    RaumCreate,
    RaumOut,
    ZeitslotCreate,
    ZeitslotOut,
)

router = APIRouter(tags=["grunddaten"])


def _register_crud(path: str, model, create_schema, out_schema, *, schule_scoped: bool = True, after_create=None):
    """Registriert Create/List/Delete für eine Grunddaten-Ressource.

    Schreibzugriff (POST/DELETE) verlangt Schulleitung + editierbare Grunddaten
    (kein Halbjahr in Abstimmung/veröffentlicht). Lesen ist jeder eingeloggten
    Person der Schule erlaubt.
    """

    @router.post(path, response_model=out_schema, status_code=status.HTTP_201_CREATED, name=f"create_{path}")
    def create(
        payload: create_schema,
        db: Session = Depends(get_db),
        user: CurrentUser = Depends(require_grunddaten_editierbar),
    ):
        data = payload.model_dump()
        if schule_scoped:
            data["schule_id"] = user.schule_id
        obj = model(**data)
        db.add(obj)
        db.flush()
        if after_create is not None:
            after_create(db, obj)
        db.commit()
        db.refresh(obj)
        return obj

    @router.get(path, response_model=list[out_schema], name=f"list_{path}")
    def list_all(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
        query = db.query(model)
        if schule_scoped:
            query = query.filter(model.schule_id == user.schule_id)
        return query.all()

    @router.delete(path + "/{item_id}", status_code=status.HTTP_204_NO_CONTENT, name=f"delete_{path}")
    def delete(
        item_id: int,
        db: Session = Depends(get_db),
        user: CurrentUser = Depends(require_grunddaten_editierbar),
    ):
        obj = db.get(model, item_id)
        if obj is None or (schule_scoped and getattr(obj, "schule_id", None) != user.schule_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nicht gefunden.")
        db.delete(obj)
        db.commit()


def _standardgruppe_anlegen(db: Session, klasse: Klasse) -> None:
    """Jede Klasse bekommt eine Standardgruppe, die die ganze Klasse repräsentiert
    (Architektur-Dokument: unterrichtseinheiten referenziert immer eine Gruppe,
    nie wahlweise Klasse oder Gruppe)."""
    db.add(Gruppe(klasse_id=klasse.id, bezeichnung=klasse.bezeichnung, fach_id=None))


_register_crud("/klassen", Klasse, KlasseCreate, KlasseOut, after_create=_standardgruppe_anlegen)
_register_crud("/lehrer", Lehrer, LehrerCreate, LehrerOut)
_register_crud("/faecher", Fach, FachCreate, FachOut)
_register_crud("/raeume", Raum, RaumCreate, RaumOut)
_register_crud("/zeitslots", Zeitslot, ZeitslotCreate, ZeitslotOut)
_register_crud("/gruppen", Gruppe, GruppeCreate, GruppeOut, schule_scoped=False)
