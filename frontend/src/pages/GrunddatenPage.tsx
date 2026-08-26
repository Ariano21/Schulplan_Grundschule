import { useState, type FormEvent, type ReactNode } from "react";
import { useAuth } from "../auth/AuthContext";
import { useResource } from "../api/useResource";
import type { Fach, Klasse, Lehrer, Raum, Zeitslot } from "../api/types";

const WOCHENTAGE = ["", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"];

type Tab = "klassen" | "lehrer" | "faecher" | "raeume" | "zeitslots";

const TABS: { key: Tab; label: string }[] = [
  { key: "klassen", label: "Klassen" },
  { key: "lehrer", label: "Lehrkräfte" },
  { key: "faecher", label: "Fächer" },
  { key: "raeume", label: "Räume" },
  { key: "zeitslots", label: "Zeitraster" },
];

export default function GrunddatenPage() {
  const [tab, setTab] = useState<Tab>("klassen");

  return (
    <div>
      <h2>Grunddaten</h2>
      <p style={{ color: "var(--ink-soft)", marginTop: "0.4rem" }}>
        Klassen, Lehrkräfte, Fächer, Räume und Zeitraster — die Bausteine, aus denen der Stundenplan entsteht.
      </p>
      <div className="tab-bar" style={{ marginTop: "1.4rem" }}>
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>
      {tab === "klassen" && <KlassenTab />}
      {tab === "lehrer" && <LehrerTab />}
      {tab === "faecher" && <FaecherTab />}
      {tab === "raeume" && <RaeumeTab />}
      {tab === "zeitslots" && <ZeitslotsTab />}
    </div>
  );
}

function TabShell({
  error,
  children,
  form,
}: {
  error: string | null;
  children: ReactNode;
  form: ReactNode;
}) {
  const { user } = useAuth();
  return (
    <div className="card">
      {error && <div className="error-banner">{error}</div>}
      {children}
      {user?.rolle === "schulleitung" && form}
    </div>
  );
}

function DeleteButton({ onDelete }: { onDelete: () => void }) {
  const { user } = useAuth();
  if (user?.rolle !== "schulleitung") return null;
  return (
    <button className="btn btn-danger" style={{ padding: "0.2rem 0.5rem" }} onClick={onDelete}>
      Entfernen
    </button>
  );
}

function KlassenTab() {
  const { items, error, create, remove } = useResource<Klasse, { bezeichnung: string; jahrgangsstufe: number }>(
    "/klassen"
  );
  const [bezeichnung, setBezeichnung] = useState("");
  const [jahrgangsstufe, setJahrgangsstufe] = useState(1);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await create({ bezeichnung, jahrgangsstufe });
    setBezeichnung("");
  }

  return (
    <TabShell
      error={error}
      form={
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="k-bez">Bezeichnung</label>
            <input id="k-bez" value={bezeichnung} onChange={(e) => setBezeichnung(e.target.value)} placeholder="1a" required />
          </div>
          <div className="field">
            <label htmlFor="k-jg">Jahrgang</label>
            <select id="k-jg" value={jahrgangsstufe} onChange={(e) => setJahrgangsstufe(Number(e.target.value))}>
              {[1, 2, 3, 4].map((jg) => (
                <option key={jg} value={jg}>
                  {jg}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" type="submit">
            Klasse anlegen
          </button>
        </form>
      }
    >
      <table>
        <thead>
          <tr>
            <th>Bezeichnung</th>
            <th>Jahrgang</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((k) => (
            <tr key={k.id}>
              <td>{k.bezeichnung}</td>
              <td>{k.jahrgangsstufe}</td>
              <td>
                <DeleteButton onDelete={() => remove(k.id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TabShell>
  );
}

function LehrerTab() {
  const { items, error, create, remove } = useResource<
    Lehrer,
    { name: string; email: string; deputat_wochenstunden: number }
  >("/lehrer");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [deputat, setDeputat] = useState(28);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await create({ name, email, deputat_wochenstunden: deputat });
    setName("");
    setEmail("");
  }

  return (
    <TabShell
      error={error}
      form={
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="l-name">Name</label>
            <input id="l-name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="l-email">E-Mail</label>
            <input id="l-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="l-deputat">Deputat (Std./Woche)</label>
            <input
              id="l-deputat"
              type="number"
              min={1}
              max={40}
              step={0.5}
              value={deputat}
              onChange={(e) => setDeputat(Number(e.target.value))}
            />
          </div>
          <button className="btn btn-primary" type="submit">
            Lehrkraft anlegen
          </button>
        </form>
      }
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>E-Mail</th>
            <th>Deputat</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((l) => (
            <tr key={l.id}>
              <td>{l.name}</td>
              <td>{l.email}</td>
              <td>{l.deputat_wochenstunden} Std.</td>
              <td>
                <DeleteButton onDelete={() => remove(l.id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TabShell>
  );
}

function FaecherTab() {
  const { items, error, create, remove } = useResource<
    Fach,
    { kuerzel: string; name: string; benoetigter_raumtyp: string | null }
  >("/faecher");
  const [kuerzel, setKuerzel] = useState("");
  const [name, setName] = useState("");
  const [raumtyp, setRaumtyp] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await create({ kuerzel, name, benoetigter_raumtyp: raumtyp || null });
    setKuerzel("");
    setName("");
    setRaumtyp("");
  }

  return (
    <TabShell
      error={error}
      form={
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="f-kuerzel">Kürzel</label>
            <input id="f-kuerzel" value={kuerzel} onChange={(e) => setKuerzel(e.target.value)} placeholder="MA" required />
          </div>
          <div className="field">
            <label htmlFor="f-name">Name</label>
            <input id="f-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Mathematik" required />
          </div>
          <div className="field">
            <label htmlFor="f-raumtyp">Benötigter Raumtyp</label>
            <input id="f-raumtyp" value={raumtyp} onChange={(e) => setRaumtyp(e.target.value)} placeholder="optional" />
          </div>
          <button className="btn btn-primary" type="submit">
            Fach anlegen
          </button>
        </form>
      }
    >
      <table>
        <thead>
          <tr>
            <th>Kürzel</th>
            <th>Name</th>
            <th>Raumtyp</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((f) => (
            <tr key={f.id}>
              <td>{f.kuerzel}</td>
              <td>{f.name}</td>
              <td>{f.benoetigter_raumtyp ?? "—"}</td>
              <td>
                <DeleteButton onDelete={() => remove(f.id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TabShell>
  );
}

function RaeumeTab() {
  const { items, error, create, remove } = useResource<
    Raum,
    { name: string; typ: string; kapazitaet: number | null }
  >("/raeume");
  const [name, setName] = useState("");
  const [typ, setTyp] = useState("Klassenraum");
  const [kapazitaet, setKapazitaet] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await create({ name, typ, kapazitaet: kapazitaet ? Number(kapazitaet) : null });
    setName("");
    setKapazitaet("");
  }

  return (
    <TabShell
      error={error}
      form={
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="r-name">Name</label>
            <input id="r-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Raum 12" required />
          </div>
          <div className="field">
            <label htmlFor="r-typ">Typ</label>
            <input id="r-typ" value={typ} onChange={(e) => setTyp(e.target.value)} placeholder="Klassenraum" />
          </div>
          <div className="field">
            <label htmlFor="r-kap">Kapazität</label>
            <input id="r-kap" type="number" value={kapazitaet} onChange={(e) => setKapazitaet(e.target.value)} placeholder="optional" />
          </div>
          <button className="btn btn-primary" type="submit">
            Raum anlegen
          </button>
        </form>
      }
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Typ</th>
            <th>Kapazität</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id}>
              <td>{r.name}</td>
              <td>{r.typ}</td>
              <td>{r.kapazitaet ?? "—"}</td>
              <td>
                <DeleteButton onDelete={() => remove(r.id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TabShell>
  );
}

function ZeitslotsTab() {
  const { items, error, create, remove } = useResource<
    Zeitslot,
    { wochentag: number; start_zeit: string; end_zeit: string; ist_pause: boolean }
  >("/zeitslots");
  const [wochentag, setWochentag] = useState(1);
  const [start, setStart] = useState("08:00");
  const [ende, setEnde] = useState("08:45");
  const [istPause, setIstPause] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await create({ wochentag, start_zeit: `${start}:00`, end_zeit: `${ende}:00`, ist_pause: istPause });
  }

  const sorted = [...items].sort((a, b) => a.wochentag - b.wochentag || a.start_zeit.localeCompare(b.start_zeit));

  return (
    <TabShell
      error={error}
      form={
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="z-tag">Wochentag</label>
            <select id="z-tag" value={wochentag} onChange={(e) => setWochentag(Number(e.target.value))}>
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>
                  {WOCHENTAGE[d]}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="z-start">Start</label>
            <input id="z-start" type="time" value={start} onChange={(e) => setStart(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="z-ende">Ende</label>
            <input id="z-ende" type="time" value={ende} onChange={(e) => setEnde(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="z-pause">Pause?</label>
            <input id="z-pause" type="checkbox" checked={istPause} onChange={(e) => setIstPause(e.target.checked)} style={{ width: "auto" }} />
          </div>
          <button className="btn btn-primary" type="submit">
            Zeitslot anlegen
          </button>
        </form>
      }
    >
      <table>
        <thead>
          <tr>
            <th>Tag</th>
            <th>Von</th>
            <th>Bis</th>
            <th>Pause</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((z) => (
            <tr key={z.id}>
              <td>{WOCHENTAGE[z.wochentag]}</td>
              <td>{z.start_zeit.slice(0, 5)}</td>
              <td>{z.end_zeit.slice(0, 5)}</td>
              <td>{z.ist_pause ? "ja" : "—"}</td>
              <td>
                <DeleteButton onDelete={() => remove(z.id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TabShell>
  );
}
