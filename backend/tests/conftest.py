import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"

import datetime

import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token, hash_password
from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models import Fach, Gruppe, Halbjahr, HalbjahrStatus, Klasse, Lehrer, Nutzer, Raum, Rolle, Schule, Zeitslot


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def grunddaten(db_session):
    """Legt eine Schule mit je einer Klasse/Gruppe/Lehrkraft/Fach/Raum/Zeitslot an."""
    schule = Schule(name="Grundschule am Teich", bundesland="NRW", schulform="Grundschule")
    db_session.add(schule)
    db_session.flush()

    lehrer_a = Lehrer(schule_id=schule.id, name="Frau Meyer", email="meyer@schule.example", deputat_wochenstunden=28)
    lehrer_b = Lehrer(schule_id=schule.id, name="Herr Kaya", email="kaya@schule.example", deputat_wochenstunden=28)
    db_session.add_all([lehrer_a, lehrer_b])
    db_session.flush()

    klasse_a = Klasse(schule_id=schule.id, bezeichnung="1a", jahrgangsstufe=1, klassenleitung_id=lehrer_a.id)
    klasse_b = Klasse(schule_id=schule.id, bezeichnung="1b", jahrgangsstufe=1, klassenleitung_id=lehrer_b.id)
    db_session.add_all([klasse_a, klasse_b])
    db_session.flush()

    gruppe_a = Gruppe(klasse_id=klasse_a.id, bezeichnung="1a gesamt")
    gruppe_b = Gruppe(klasse_id=klasse_b.id, bezeichnung="1b gesamt")
    db_session.add_all([gruppe_a, gruppe_b])
    db_session.flush()

    fach = Fach(schule_id=schule.id, kuerzel="MA", name="Mathematik")
    raum_a = Raum(schule_id=schule.id, name="Raum 1", typ="Klassenraum")
    raum_b = Raum(schule_id=schule.id, name="Raum 2", typ="Klassenraum")
    db_session.add_all([fach, raum_a, raum_b])
    db_session.flush()

    zeitslot = Zeitslot(
        schule_id=schule.id,
        wochentag=1,
        start_zeit=datetime.time(8, 0),
        end_zeit=datetime.time(8, 45),
        ist_pause=False,
    )
    db_session.add(zeitslot)
    db_session.flush()

    halbjahr = Halbjahr(
        schule_id=schule.id,
        start_datum=datetime.date(2026, 2, 1),
        end_datum=datetime.date(2026, 7, 31),
        status=HalbjahrStatus.entwurf,
    )
    db_session.add(halbjahr)
    db_session.flush()

    schulleitung = Nutzer(
        schule_id=schule.id,
        email="leitung@schule.example",
        password_hash=hash_password("geheim123"),
        rolle=Rolle.schulleitung,
    )
    lehrkraft = Nutzer(
        schule_id=schule.id,
        email=lehrer_a.email,
        password_hash=hash_password("geheim123"),
        rolle=Rolle.lehrkraft,
        lehrer_id=lehrer_a.id,
    )
    db_session.add_all([schulleitung, lehrkraft])
    db_session.commit()

    return {
        "schule": schule,
        "lehrer_a": lehrer_a,
        "lehrer_b": lehrer_b,
        "klasse_a": klasse_a,
        "klasse_b": klasse_b,
        "gruppe_a": gruppe_a,
        "gruppe_b": gruppe_b,
        "fach": fach,
        "raum_a": raum_a,
        "raum_b": raum_b,
        "zeitslot": zeitslot,
        "halbjahr": halbjahr,
        "schulleitung": schulleitung,
        "lehrkraft": lehrkraft,
    }


def auth_header(nutzer: Nutzer) -> dict:
    token = create_access_token(subject=str(nutzer.id), rolle=nutzer.rolle.value, schule_id=nutzer.schule_id)
    return {"Authorization": f"Bearer {token}"}
