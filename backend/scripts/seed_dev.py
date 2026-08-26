"""Füllt eine leere Datenbank mit Demodaten für die lokale Entwicklung.

Nutzung:
    cd backend && source .venv/bin/activate
    python -m scripts.seed_dev

Legt eine Schule mit zwei Klassen, zwei Lehrkräften, einem Fach, zwei Räumen,
einem Montags-Zeitraster und einem Entwurfs-Halbjahr an. Login:
  Schulleitung: leitung@demo.schule / geheim123
  Lehrkraft:    meyer@demo.schule / geheim123
"""

import datetime

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Fach,
    Gruppe,
    Halbjahr,
    HalbjahrStatus,
    Klasse,
    Lehrer,
    Nutzer,
    Raum,
    Rolle,
    Schule,
    Zeitslot,
)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Schule).first() is not None:
        print("Datenbank enthält bereits Daten – Abbruch, um nichts zu duplizieren.")
        return

    schule = Schule(name="Grundschule am Teich", bundesland="NRW", schulform="Grundschule")
    db.add(schule)
    db.flush()

    lehrer_meyer = Lehrer(schule_id=schule.id, name="Frau Meyer", email="meyer@demo.schule", deputat_wochenstunden=28)
    lehrer_kaya = Lehrer(schule_id=schule.id, name="Herr Kaya", email="kaya@demo.schule", deputat_wochenstunden=28)
    db.add_all([lehrer_meyer, lehrer_kaya])
    db.flush()

    klasse_a = Klasse(schule_id=schule.id, bezeichnung="1a", jahrgangsstufe=1, klassenleitung_id=lehrer_meyer.id)
    klasse_b = Klasse(schule_id=schule.id, bezeichnung="1b", jahrgangsstufe=1, klassenleitung_id=lehrer_kaya.id)
    db.add_all([klasse_a, klasse_b])
    db.flush()

    db.add_all(
        [
            Gruppe(klasse_id=klasse_a.id, bezeichnung="1a"),
            Gruppe(klasse_id=klasse_b.id, bezeichnung="1b"),
        ]
    )

    fach = Fach(schule_id=schule.id, kuerzel="MA", name="Mathematik")
    raum1 = Raum(schule_id=schule.id, name="Raum 1", typ="Klassenraum")
    raum2 = Raum(schule_id=schule.id, name="Raum 2", typ="Klassenraum")
    db.add_all([fach, raum1, raum2])

    start = datetime.time(8, 0)
    for i in range(4):
        h = (datetime.datetime.combine(datetime.date.today(), start) + datetime.timedelta(minutes=45 * i)).time()
        ende = (datetime.datetime.combine(datetime.date.today(), h) + datetime.timedelta(minutes=45)).time()
        db.add(Zeitslot(schule_id=schule.id, wochentag=1, start_zeit=h, end_zeit=ende, ist_pause=False))

    db.add(
        Halbjahr(
            schule_id=schule.id,
            start_datum=datetime.date(2026, 2, 1),
            end_datum=datetime.date(2026, 7, 31),
            status=HalbjahrStatus.entwurf,
        )
    )

    db.add_all(
        [
            Nutzer(
                schule_id=schule.id,
                email="leitung@demo.schule",
                password_hash=hash_password("geheim123"),
                rolle=Rolle.schulleitung,
            ),
            Nutzer(
                schule_id=schule.id,
                email=lehrer_meyer.email,
                password_hash=hash_password("geheim123"),
                rolle=Rolle.lehrkraft,
                lehrer_id=lehrer_meyer.id,
            ),
        ]
    )

    db.commit()
    db.close()
    print("Demodaten angelegt.")


if __name__ == "__main__":
    main()
