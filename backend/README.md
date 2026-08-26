# Backend

FastAPI + PostgreSQL, wie in der Architektur-Grundlage festgelegt. Setzt den
Fundament-Sprint um: Grunddaten-CRUD, Auth mit Rollen, und Unterrichtseinheiten
mit den drei DB-abgesicherten Constraints H1–H3 (Lehrer-, Gruppen-, Raum-Kollision).

## Lokal starten

```bash
docker compose up
```

Läuft dann auf `http://localhost:8000`, API-Doku unter `/docs`.

## Ohne Docker (z. B. für Tests)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # DATABASE_URL bei Bedarf anpassen
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Die Tests laufen gegen eine In-Memory-SQLite-DB (siehe `tests/conftest.py`),
nicht gegen Postgres – schnell genug für jeden Commit, aber kein Ersatz für
einen Postgres-Smoketest vor dem ersten echten Deploy (UNIQUE-Verhalten ist
gleich, aber nicht jedes Detail zwischen den beiden Dialekten).

## Neue Migration erzeugen

```bash
alembic revision --autogenerate -m "beschreibung"
```

## Was aus dem Fundament-Sprint hier drin ist

- `app/models.py` – die zwölf Tabellen aus dem Architektur-Dokument (DB-1–DB-4)
- `app/auth.py`, `app/deps.py` – Passwort-Hashing, JWT, Rollen- und Status-Gates
- `app/routers/grunddaten.py` – CRUD für Klassen/Lehrer/Fächer/Räume/Zeitslots/Gruppen (API-1)
- `app/routers/halbjahre.py` – Halbjahr anlegen, Status fix "Entwurf" (API-2)
- `app/routers/unterrichtseinheiten.py` – Kernstück: prüft H1–H3 proaktiv und
  liefert strukturierte Konfliktobjekte statt eines nackten Fehlercodes (API-3)
- `tests/test_constraints.py` – QA-1
- `tests/test_roles.py` – QA-2

Bewusst **nicht** enthalten (siehe Fundament-Sprint-Dokument, Abschnitt
"Außerhalb dieses Sprints"): H4–H7, weiche Constraints, Status-Übergänge
Abstimmung/Veröffentlicht, Solver, PDF-Export, Vertretung.
