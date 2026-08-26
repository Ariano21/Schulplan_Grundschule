# Frontend

React (Vite + TypeScript), wie in der Architektur-Grundlage festgelegt. Setzt
FE-1 bis FE-4 aus dem Fundament-Sprint um.

## Lokal starten

Backend muss laufen (siehe `../backend/README.md`), dann:

```bash
cd frontend
npm install
npm run dev
```

Läuft auf `http://localhost:5173`. Zum Testen mit Demodaten:
`python -m scripts.seed_dev` im Backend ausführen (siehe dortige README),
danach einloggen mit `leitung@demo.schule` / `geheim123` (Schulleitung) oder
`meyer@demo.schule` / `geheim123` (Lehrkraft).

## Was drin ist

- `src/pages/LoginPage.tsx` – Login (FE-1)
- `src/pages/GrunddatenPage.tsx` – Verwaltung von Klassen, Lehrkräften,
  Fächern, Räumen, Zeitraster; Schreibrechte nur für die Rolle Schulleitung,
  serverseitig durchgesetzt, hier nur zur Führung ausgeblendet (FE-2)
- `src/pages/StundenplanPage.tsx` – Grid + Zelle setzen + Inline-Konfliktanzeige
  bei H1–H3-Verletzung, direkt aus der strukturierten API-Antwort (FE-3, FE-4)

## Bewusst nicht enthalten

Kein PWA-Offline-Modus (laut Fundament-Sprint kein MVP-Thema, siehe
Technologie-Stack-Abschnitt im Architektur-Dokument), keine Bearbeitung
mehrerer Gruppen pro Klasse in der UI (Backend unterstützt es, UI zeigt
aktuell nur die Standardgruppe einer Klasse), kein Freigabe-Checkliste-Flow
(braucht H4–H7, außerhalb des Sprints).
