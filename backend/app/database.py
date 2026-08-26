from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


def _make_engine():
    url = settings.database_url
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        # In-Memory-SQLite braucht einen einzigen geteilten Connection-Pool,
        # sonst sieht jede Session eine eigene, leere Datenbank (nur für Tests relevant).
        poolclass = StaticPool if ":memory:" in url else None
        kwargs = {"connect_args": connect_args}
        if poolclass:
            kwargs["poolclass"] = poolclass
        return create_engine(url, **kwargs)
    return create_engine(url)


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
