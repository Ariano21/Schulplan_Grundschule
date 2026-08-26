import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import { api, ApiError } from "../api/client";
import { useResource } from "../api/useResource";
import type {
  Fach,
  Gruppe,
  Halbjahr,
  Klasse,
  Konflikt,
  Lehrer,
  Raum,
  Unterrichtseinheit,
  Zeitslot,
} from "../api/types";

const WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"];

export default function StundenplanPage() {
  const { user } = useAuth();
  const { items: halbjahre, create: createHalbjahr, error: halbjahrError } = useResource<
    Halbjahr,
    { start_datum: string; end_datum: string }
  >("/halbjahre");
  const { items: klassen } = useResource<Klasse, never>("/klassen");
  const { items: gruppen } = useResource<Gruppe, never>("/gruppen");
  const { items: zeitslots } = useResource<Zeitslot, never>("/zeitslots");
  const { items: lehrerListe } = useResource<Lehrer, never>("/lehrer");
  const { items: faecher } = useResource<Fach, never>("/faecher");
  const { items: raeume } = useResource<Raum, never>("/raeume");

  const [halbjahrId, setHalbjahrId] = useState<number | null>(null);
  const [klasseId, setKlasseId] = useState<number | null>(null);
  const [einheiten, setEinheiten] = useState<Unterrichtseinheit[]>([]);
  const [activeCell, setActiveCell] = useState<Zeitslot | null>(null);

  useEffect(() => {
    if (halbjahre.length > 0 && halbjahrId === null) setHalbjahrId(halbjahre[0].id);
  }, [halbjahre, halbjahrId]);

  useEffect(() => {
    if (klassen.length > 0 && klasseId === null) setKlasseId(klassen[0].id);
  }, [klassen, klasseId]);

  useEffect(() => {
    if (!halbjahrId) {
      setEinheiten([]);
      return;
    }
    api.get<Unterrichtseinheit[]>(`/unterrichtseinheiten?halbjahr_id=${halbjahrId}`).then(setEinheiten);
  }, [halbjahrId]);

  const gruppe = useMemo(() => gruppen.find((g) => g.klasse_id === klasseId) ?? null, [gruppen, klasseId]);

  const zeitraster = useMemo(() => {
    const zeiten = Array.from(new Set(zeitslots.map((z) => z.start_zeit))).sort();
    return zeiten.map((start) => ({
      start,
      byTag: WOCHENTAGE.map((_, i) => zeitslots.find((z) => z.wochentag === i + 1 && z.start_zeit === start) ?? null),
    }));
  }, [zeitslots]);

  function einheitFuer(zeitslotId: number): Unterrichtseinheit | undefined {
    if (!gruppe) return undefined;
    return einheiten.find((e) => e.zeitslot_id === zeitslotId && e.gruppe_id === gruppe.id);
  }

  function nameFor<T extends { id: number }>(liste: T[], id: number, field: keyof T): string {
    const item = liste.find((x) => x.id === id);
    return item ? String(item[field]) : "?";
  }

  async function handleCreated(neue: Unterrichtseinheit) {
    setEinheiten((prev) => [...prev, neue]);
    setActiveCell(null);
  }

  if (halbjahre.length === 0) {
    return <NeuesHalbjahr error={halbjahrError} onCreate={createHalbjahr} />;
  }

  return (
    <div>
      <h2>Stundenplan</h2>
      <div className="grid-controls">
        <div className="field">
          <label htmlFor="hj">Halbjahr</label>
          <select id="hj" value={halbjahrId ?? ""} onChange={(e) => setHalbjahrId(Number(e.target.value))}>
            {halbjahre.map((h) => (
              <option key={h.id} value={h.id}>
                {h.start_datum} – {h.end_datum} ({h.status})
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="kl">Klasse</label>
          <select id="kl" value={klasseId ?? ""} onChange={(e) => setKlasseId(Number(e.target.value))}>
            {klassen.map((k) => (
              <option key={k.id} value={k.id}>
                {k.bezeichnung}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!gruppe && <p style={{ color: "var(--ink-faint)" }}>Für diese Klasse existiert noch keine Gruppe.</p>}

      {gruppe && zeitraster.length === 0 && (
        <p style={{ color: "var(--ink-faint)" }}>Noch kein Zeitraster angelegt (siehe Grunddaten).</p>
      )}

      {gruppe && zeitraster.length > 0 && (
        <div className="timetable" style={{ gridTemplateColumns: `5.5rem repeat(${WOCHENTAGE.length}, 1fr)` }}>
          <div className="timetable-head"></div>
          {WOCHENTAGE.map((tag) => (
            <div className="timetable-head" key={tag}>
              {tag}
            </div>
          ))}
          {zeitraster.map((row) => (
            <RowFragment
              key={row.start}
              row={row}
              einheitFuer={einheitFuer}
              nameFor={nameFor}
              lehrerListe={lehrerListe}
              faecher={faecher}
              raeume={raeume}
              istSchulleitung={user?.rolle === "schulleitung"}
              onCellClick={setActiveCell}
            />
          ))}
        </div>
      )}

      {activeCell && gruppe && halbjahrId && (
        <UnterrichtseinheitModal
          zeitslot={activeCell}
          gruppe={gruppe}
          halbjahrId={halbjahrId}
          lehrerListe={lehrerListe}
          faecher={faecher}
          raeume={raeume}
          einheiten={einheiten}
          onClose={() => setActiveCell(null)}
          onCreated={handleCreated}
        />
      )}
    </div>
  );
}

interface Row {
  start: string;
  byTag: (Zeitslot | null)[];
}

function RowFragment({
  row,
  einheitFuer,
  nameFor,
  lehrerListe,
  faecher,
  raeume,
  istSchulleitung,
  onCellClick,
}: {
  row: Row;
  einheitFuer: (zeitslotId: number) => Unterrichtseinheit | undefined;
  nameFor: <T extends { id: number }>(liste: T[], id: number, field: keyof T) => string;
  lehrerListe: Lehrer[];
  faecher: Fach[];
  raeume: Raum[];
  istSchulleitung: boolean;
  onCellClick: (z: Zeitslot) => void;
}) {
  return (
    <>
      <div className="time-label">{row.start.slice(0, 5)}</div>
      {row.byTag.map((slot, i) => {
        if (!slot) return <div className="cell" key={`empty-${i}`}></div>;
        if (slot.ist_pause) {
          return (
            <div className="cell pause" key={`slot-${slot.id}`}>
              Pause
            </div>
          );
        }
        const einheit = einheitFuer(slot.id);
        if (einheit) {
          return (
            <div className="cell filled" key={`slot-${slot.id}`}>
              <div className="cell-entry">
                <b>{nameFor(faecher, einheit.fach_id, "kuerzel")}</b>
                <span>{nameFor(lehrerListe, einheit.lehrer_id, "name")}</span>
                <span>{nameFor(raeume, einheit.raum_id, "name")}</span>
              </div>
            </div>
          );
        }
        return (
          <div className="cell" key={`slot-${slot.id}`}>
            {istSchulleitung && (
              <button className="cell-add" onClick={() => onCellClick(slot)} aria-label="Unterrichtseinheit setzen">
                +
              </button>
            )}
          </div>
        );
      })}
    </>
  );
}

function UnterrichtseinheitModal({
  zeitslot,
  gruppe,
  halbjahrId,
  lehrerListe,
  faecher,
  raeume,
  onClose,
  onCreated,
}: {
  zeitslot: Zeitslot;
  gruppe: Gruppe;
  halbjahrId: number;
  lehrerListe: Lehrer[];
  faecher: Fach[];
  raeume: Raum[];
  einheiten: Unterrichtseinheit[];
  onClose: () => void;
  onCreated: (e: Unterrichtseinheit) => void;
}) {
  const [fachId, setFachId] = useState(faecher[0]?.id ?? 0);
  const [lehrerId, setLehrerId] = useState(lehrerListe[0]?.id ?? 0);
  const [raumId, setRaumId] = useState(raeume[0]?.id ?? 0);
  const [konflikte, setKonflikte] = useState<Konflikt[] | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setKonflikte(null);
    setSubmitting(true);
    try {
      const created = await api.post<Unterrichtseinheit>("/unterrichtseinheiten", {
        halbjahr_id: halbjahrId,
        gruppe_id: gruppe.id,
        lehrer_id: lehrerId,
        fach_id: fachId,
        raum_id: raumId,
        zeitslot_id: zeitslot.id,
      });
      onCreated(created);
    } catch (err) {
      if (err instanceof ApiError && err.konflikte) {
        setKonflikte(err.konflikte);
      } else {
        setKonflikte([{ regel: "?", beschreibung: "Unerwarteter Fehler.", kollidierende_einheit_id: 0 }]);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <h3 style={{ fontSize: "1rem" }}>
          {WOCHENTAGE_LABEL(zeitslot.wochentag)}, {zeitslot.start_zeit.slice(0, 5)}
        </h3>
        <div className="field">
          <label htmlFor="m-fach">Fach</label>
          <select id="m-fach" value={fachId} onChange={(e) => setFachId(Number(e.target.value))}>
            {faecher.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="m-lehrer">Lehrkraft</label>
          <select id="m-lehrer" value={lehrerId} onChange={(e) => setLehrerId(Number(e.target.value))}>
            {lehrerListe.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="m-raum">Raum</label>
          <select id="m-raum" value={raumId} onChange={(e) => setRaumId(Number(e.target.value))}>
            {raeume.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>

        {konflikte && (
          <div>
            {konflikte.map((k, i) => (
              <div className="conflict-box" key={i}>
                <span className="regel">{k.regel}</span>
                {k.beschreibung}
              </div>
            ))}
          </div>
        )}

        <div style={{ display: "flex", gap: "0.6rem", justifyContent: "flex-end" }}>
          <button type="button" className="btn" onClick={onClose}>
            Abbrechen
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting || !fachId || !lehrerId || !raumId}>
            {submitting ? "Speichert…" : "Setzen"}
          </button>
        </div>
      </form>
    </div>
  );
}

function WOCHENTAGE_LABEL(tag: number): string {
  return WOCHENTAGE[tag - 1] ?? "?";
}

function NeuesHalbjahr({
  error,
  onCreate,
}: {
  error: string | null;
  onCreate: (payload: { start_datum: string; end_datum: string }) => Promise<void>;
}) {
  const { user } = useAuth();
  const [start, setStart] = useState("2026-02-01");
  const [ende, setEnde] = useState("2026-07-31");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onCreate({ start_datum: start, end_datum: ende });
  }

  if (user?.rolle !== "schulleitung") {
    return <p style={{ color: "var(--ink-faint)" }}>Es wurde noch kein Halbjahr angelegt.</p>;
  }

  return (
    <div className="card" style={{ maxWidth: 420 }}>
      <h3 style={{ fontSize: "1rem", marginBottom: "0.8rem" }}>Erstes Halbjahr anlegen</h3>
      {error && <div className="error-banner">{error}</div>}
      <form className="inline-form" style={{ borderTop: "none", paddingTop: 0, marginTop: 0 }} onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="hj-start">Start</label>
          <input id="hj-start" type="date" value={start} onChange={(e) => setStart(e.target.value)} required />
        </div>
        <div className="field">
          <label htmlFor="hj-ende">Ende</label>
          <input id="hj-ende" type="date" value={ende} onChange={(e) => setEnde(e.target.value)} required />
        </div>
        <button className="btn btn-primary" type="submit">
          Anlegen
        </button>
      </form>
    </div>
  );
}
