import enum
from datetime import date, time, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HalbjahrStatus(str, enum.Enum):
    entwurf = "entwurf"
    abstimmung = "abstimmung"
    veroeffentlicht = "veroeffentlicht"


class Rolle(str, enum.Enum):
    schulleitung = "schulleitung"
    lehrkraft = "lehrkraft"


def _enum(python_enum, name: str):
    return Enum(python_enum, name=name, native_enum=False, validate_strings=True)


class Schule(Base):
    __tablename__ = "schulen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bundesland: Mapped[str] = mapped_column(String(64), nullable=False)
    schulform: Mapped[str] = mapped_column(String(64), nullable=False, default="Grundschule")

    halbjahre: Mapped[list["Halbjahr"]] = relationship(back_populates="schule")
    klassen: Mapped[list["Klasse"]] = relationship(back_populates="schule")
    lehrer: Mapped[list["Lehrer"]] = relationship(back_populates="schule")
    faecher: Mapped[list["Fach"]] = relationship(back_populates="schule")
    raeume: Mapped[list["Raum"]] = relationship(back_populates="schule")
    zeitslots: Mapped[list["Zeitslot"]] = relationship(back_populates="schule")
    nutzer: Mapped[list["Nutzer"]] = relationship(back_populates="schule")


class Halbjahr(Base):
    __tablename__ = "halbjahre"
    __table_args__ = (UniqueConstraint("schule_id", "start_datum", name="uq_halbjahr_schule_start"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    start_datum: Mapped[date] = mapped_column(Date, nullable=False)
    end_datum: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[HalbjahrStatus] = mapped_column(
        _enum(HalbjahrStatus, "halbjahr_status"), nullable=False, default=HalbjahrStatus.entwurf
    )

    schule: Mapped["Schule"] = relationship(back_populates="halbjahre")


class Zeitslot(Base):
    __tablename__ = "zeitslots"
    __table_args__ = (
        UniqueConstraint("schule_id", "wochentag", "start_zeit", name="uq_zeitslot_schule_tag_start"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    wochentag: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=Montag .. 5=Freitag
    start_zeit: Mapped[time] = mapped_column(Time, nullable=False)
    end_zeit: Mapped[time] = mapped_column(Time, nullable=False)
    ist_pause: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    schule: Mapped["Schule"] = relationship(back_populates="zeitslots")


class Lehrer(Base):
    __tablename__ = "lehrer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    deputat_wochenstunden: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)

    schule: Mapped["Schule"] = relationship(back_populates="lehrer")
    qualifikationen: Mapped[list["LehrerQualifikation"]] = relationship(back_populates="lehrer")
    verfuegbarkeit: Mapped[list["LehrerVerfuegbarkeit"]] = relationship(back_populates="lehrer")


class Klasse(Base):
    __tablename__ = "klassen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    bezeichnung: Mapped[str] = mapped_column(String(32), nullable=False)
    jahrgangsstufe: Mapped[int] = mapped_column(Integer, nullable=False)
    klassenleitung_id: Mapped[int | None] = mapped_column(ForeignKey("lehrer.id"), nullable=True)

    schule: Mapped["Schule"] = relationship(back_populates="klassen")
    gruppen: Mapped[list["Gruppe"]] = relationship(back_populates="klasse")


class Gruppe(Base):
    __tablename__ = "gruppen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    klasse_id: Mapped[int] = mapped_column(ForeignKey("klassen.id"), nullable=False)
    bezeichnung: Mapped[str] = mapped_column(String(64), nullable=False)
    fach_id: Mapped[int | None] = mapped_column(ForeignKey("faecher.id"), nullable=True)

    klasse: Mapped["Klasse"] = relationship(back_populates="gruppen")


class Fach(Base):
    __tablename__ = "faecher"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    kuerzel: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    benoetigter_raumtyp: Mapped[str | None] = mapped_column(String(64), nullable=True)

    schule: Mapped["Schule"] = relationship(back_populates="faecher")


class LehrerQualifikation(Base):
    __tablename__ = "lehrer_qualifikationen"
    __table_args__ = (UniqueConstraint("lehrer_id", "fach_id", name="uq_qualifikation_lehrer_fach"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lehrer_id: Mapped[int] = mapped_column(ForeignKey("lehrer.id"), nullable=False)
    fach_id: Mapped[int] = mapped_column(ForeignKey("faecher.id"), nullable=False)

    lehrer: Mapped["Lehrer"] = relationship(back_populates="qualifikationen")


class LehrerVerfuegbarkeit(Base):
    __tablename__ = "lehrer_verfuegbarkeit"
    __table_args__ = (UniqueConstraint("lehrer_id", "zeitslot_id", name="uq_verfuegbarkeit_lehrer_zeitslot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lehrer_id: Mapped[int] = mapped_column(ForeignKey("lehrer.id"), nullable=False)
    zeitslot_id: Mapped[int] = mapped_column(ForeignKey("zeitslots.id"), nullable=False)

    lehrer: Mapped["Lehrer"] = relationship(back_populates="verfuegbarkeit")


class Stundentafel(Base):
    __tablename__ = "stundentafel"
    __table_args__ = (
        UniqueConstraint("fach_id", "jahrgangsstufe", "halbjahr_id", name="uq_stundentafel_fach_jahrgang_halbjahr"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fach_id: Mapped[int] = mapped_column(ForeignKey("faecher.id"), nullable=False)
    jahrgangsstufe: Mapped[int] = mapped_column(Integer, nullable=False)
    halbjahr_id: Mapped[int] = mapped_column(ForeignKey("halbjahre.id"), nullable=False)
    wochenstunden_soll: Mapped[int] = mapped_column(Integer, nullable=False)


class Raum(Base):
    __tablename__ = "raeume"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    typ: Mapped[str] = mapped_column(String(64), nullable=False, default="Klassenraum")
    kapazitaet: Mapped[int | None] = mapped_column(Integer, nullable=True)

    schule: Mapped["Schule"] = relationship(back_populates="raeume")


class Unterrichtseinheit(Base):
    """Der eigentliche Stundenplaneintrag. H1-H3 sind hier als UNIQUE-Constraints erzwungen."""

    __tablename__ = "unterrichtseinheiten"
    __table_args__ = (
        UniqueConstraint("lehrer_id", "zeitslot_id", "halbjahr_id", name="uq_h1_lehrer_kollision"),
        UniqueConstraint("gruppe_id", "zeitslot_id", "halbjahr_id", name="uq_h2_gruppen_kollision"),
        UniqueConstraint("raum_id", "zeitslot_id", "halbjahr_id", name="uq_h3_raum_kollision"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    halbjahr_id: Mapped[int] = mapped_column(ForeignKey("halbjahre.id"), nullable=False)
    gruppe_id: Mapped[int] = mapped_column(ForeignKey("gruppen.id"), nullable=False)
    lehrer_id: Mapped[int] = mapped_column(ForeignKey("lehrer.id"), nullable=False)
    fach_id: Mapped[int] = mapped_column(ForeignKey("faecher.id"), nullable=False)
    raum_id: Mapped[int] = mapped_column(ForeignKey("raeume.id"), nullable=False)
    zeitslot_id: Mapped[int] = mapped_column(ForeignKey("zeitslots.id"), nullable=False)


class Nutzer(Base):
    __tablename__ = "nutzer"
    __table_args__ = (UniqueConstraint("email", name="uq_nutzer_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schule_id: Mapped[int] = mapped_column(ForeignKey("schulen.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rolle: Mapped[Rolle] = mapped_column(_enum(Rolle, "nutzer_rolle"), nullable=False)
    lehrer_id: Mapped[int | None] = mapped_column(ForeignKey("lehrer.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    schule: Mapped["Schule"] = relationship(back_populates="nutzer")
