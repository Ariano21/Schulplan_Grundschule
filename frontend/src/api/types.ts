export type Rolle = "schulleitung" | "lehrkraft";
export type HalbjahrStatus = "entwurf" | "abstimmung" | "veroeffentlicht";

export interface Klasse {
  id: number;
  bezeichnung: string;
  jahrgangsstufe: number;
  klassenleitung_id: number | null;
}

export interface Lehrer {
  id: number;
  name: string;
  email: string;
  deputat_wochenstunden: number;
}

export interface Fach {
  id: number;
  kuerzel: string;
  name: string;
  benoetigter_raumtyp: string | null;
}

export interface Raum {
  id: number;
  name: string;
  typ: string;
  kapazitaet: number | null;
}

export interface Zeitslot {
  id: number;
  wochentag: number; // 1 = Montag .. 5 = Freitag
  start_zeit: string; // "HH:MM:SS"
  end_zeit: string;
  ist_pause: boolean;
}

export interface Gruppe {
  id: number;
  klasse_id: number;
  bezeichnung: string;
  fach_id: number | null;
}

export interface Halbjahr {
  id: number;
  start_datum: string;
  end_datum: string;
  status: HalbjahrStatus;
}

export interface Unterrichtseinheit {
  id: number;
  halbjahr_id: number;
  gruppe_id: number;
  lehrer_id: number;
  fach_id: number;
  raum_id: number;
  zeitslot_id: number;
}

export interface Konflikt {
  regel: string;
  beschreibung: string;
  kollidierende_einheit_id: number;
}
