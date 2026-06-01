from collections.abc import Iterator

from flask import g
from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# Deterministic names for every index/constraint. Without this, autogenerate
# emits unnamed (None) constraints, which SQLite's batch migrations reject with
# "Constraint must have a name". With it, names are stable across MySQL/SQLite
# and migrations can drop a constraint by the same name they created it under.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _engine_kwargs(url: str) -> dict:
    """Engine options that differ between SQLite and a networked DB (MySQL)."""
    if url.startswith("sqlite"):
        # SQLite is a local file, so there's no connection to pre-ping. Flask's
        # dev server handles requests on multiple threads; check_same_thread=False
        # lets SQLAlchemy's pool hand a connection back across those threads.
        return {"connect_args": {"check_same_thread": False}}
    # MySQL (or any networked DB): drop stale pooled connections before using them.
    return {"pool_pre_ping": True}


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(engine, expire_on_commit=False)


if settings.database_url.startswith("sqlite"):
    # SQLite ignores foreign keys unless asked, per-connection. MySQL/InnoDB
    # enforces them natively, so this is only wired up for SQLite.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_session() -> Session:
    """Return the request-scoped Session, opening one on first use.

    The session lives on Flask's `g`, so every handler in a request shares it
    and `close_session` (wired up as a teardown in the app factory) closes it
    when the request ends.
    """
    if "db_session" not in g:
        g.db_session = SessionLocal()
    return g.db_session


def close_session(_exc: BaseException | None = None) -> None:
    """Close the request-scoped Session, if one was opened. Teardown handler."""
    session: Session | None = g.pop("db_session", None)
    if session is not None:
        session.close()


# Re-exported for callers that want to iterate (e.g. scripts) without Flask's
# request context. Most app code should use get_session() instead.
def session_scope() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
