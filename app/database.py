import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL or not DATABASE_URL.strip():
    raise RuntimeError("A variável de ambiente DATABASE_URL deve ser definida.")

connect_args = (
    {"check_same_thread": False}
    if make_url(DATABASE_URL).get_backend_name() == "sqlite"
    else {}
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)

if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        has_autocommit = hasattr(dbapi_connection, "autocommit")
        if has_autocommit:
            previous_autocommit = dbapi_connection.autocommit
            dbapi_connection.autocommit = True

        try:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()
        finally:
            if has_autocommit:
                dbapi_connection.autocommit = previous_autocommit

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
