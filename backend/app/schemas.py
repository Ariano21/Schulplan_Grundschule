from datetime import date, time

from pydantic import BaseModel, EmailStr, Field

from app.models import HalbjahrStatus, Rolle


# --- Auth ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rolle: Rolle
    schule_id: int


# --- Grunddaten ---

class KlasseCreate(BaseModel):
    bezeichnung: str = Field(min_length=1, max_length=32)
    jahrgangsstufe: int = Field(ge=1, le=4)
    klassenleitung_id: int | None = None


class KlasseOut(KlasseCreate):
    id: int
    model_config = {"from_attributes": True}


class LehrerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    deputat_wochenstunden: float = Field(gt=0, le=40)


class LehrerOut(LehrerCreate):
    id: int
    model_config = {"from_attributes": True}


class FachCreate(BaseModel):
    kuerzel: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1, max_length=128)
    benoetigter_raumtyp: str | None = None


class FachOut(FachCreate):
    id: int
    model_config = {"from_attributes": True}


class RaumCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    typ: str = "Klassenraum"
    kapazitaet: int | None = None


class RaumOut(RaumCreate):
    id: int
    model_config = {"from_attributes": True}


class ZeitslotCreate(BaseModel):
    wochentag: int = Field(ge=1, le=5)
    start_zeit: time
    end_zeit: time
    ist_pause: bool = False


class ZeitslotOut(ZeitslotCreate):
    id: int
    model_config = {"from_attributes": True}


class GruppeCreate(BaseModel):
    klasse_id: int
    bezeichnung: str = Field(min_length=1, max_length=64)
    fach_id: int | None = None


class GruppeOut(GruppeCreate):
    id: int
    model_config = {"from_attributes": True}


# --- Halbjahr ---

class HalbjahrCreate(BaseModel):
    start_datum: date
    end_datum: date


class HalbjahrOut(BaseModel):
    id: int
    start_datum: date
    end_datum: date
    status: HalbjahrStatus
    model_config = {"from_attributes": True}


# --- Unterrichtseinheit ---

class UnterrichtseinheitCreate(BaseModel):
    halbjahr_id: int
    gruppe_id: int
    lehrer_id: int
    fach_id: int
    raum_id: int
    zeitslot_id: int


class UnterrichtseinheitOut(UnterrichtseinheitCreate):
    id: int
    model_config = {"from_attributes": True}


class Konflikt(BaseModel):
    regel: str
    beschreibung: str
    kollidierende_einheit_id: int


class KonfliktFehler(BaseModel):
    detail: str = "Konflikt mit bestehendem Plan"
    konflikte: list[Konflikt]
