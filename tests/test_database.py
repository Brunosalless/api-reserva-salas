import importlib.util
import sqlite3
from pathlib import Path

import pytest
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, URL, select
from sqlalchemy.exc import IntegrityError


@pytest.fixture(params=["legacy", "transactional"])
def database(request, monkeypatch, tmp_path):
    if request.param == "transactional":
        if not hasattr(sqlite3.Connection, "autocommit"):
            pytest.skip("sqlite3 autocommit requires Python 3.12+")
        original_create_engine = sqlalchemy.create_engine

        def create_engine(url, **kwargs):
            kwargs["connect_args"]["autocommit"] = False
            return original_create_engine(url, **kwargs)

        monkeypatch.setattr(sqlalchemy, "create_engine", create_engine)

    # Override before executing the module: never use a developer's DATABASE_URL.
    url = URL.create("sqlite", database=str(tmp_path / "foreign_keys.sqlite"))
    monkeypatch.setenv("DATABASE_URL", str(url))
    path = Path(__file__).resolve().parents[1] / "app" / "database.py"
    spec = importlib.util.spec_from_file_location("isolated_database", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.expected_autocommit = (
        False if request.param == "transactional"
        else getattr(sqlite3, "LEGACY_TRANSACTION_CONTROL", None)
    )
    try:
        yield module
    finally:
        module.engine.dispose()


def test_foreign_keys_enabled_on_every_new_connection(database):
    engine = database.engine
    with engine.connect() as first, engine.connect() as second:
        assert first.connection.driver_connection is not second.connection.driver_connection
        for connection in (first, second):
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
            raw_connection = connection.connection.driver_connection
            if hasattr(raw_connection, "autocommit"):
                assert raw_connection.autocommit == database.expected_autocommit
    engine.dispose()
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1


@pytest.mark.parametrize("invalid_column", ["sala_id", "usuario_id"])
def test_foreign_keys_and_session_rollback(database, invalid_column):
    # Minimal independent tables also work before the T4 models are merged.
    metadata = MetaData()
    users = Table("users", metadata, Column("id", Integer, primary_key=True))
    rooms = Table("rooms", metadata, Column("id", Integer, primary_key=True))
    reservations = Table(
        "reservations", metadata,
        Column("id", Integer, primary_key=True),
        Column("sala_id", ForeignKey("rooms.id"), nullable=False),
        Column("usuario_id", ForeignKey("users.id"), nullable=False),
    )
    metadata.create_all(database.engine)
    with database.SessionLocal() as session:
        session.execute(users.insert().values(id=1))
        session.execute(rooms.insert().values(id=1))
        session.execute(reservations.insert().values(id=1, sala_id=1, usuario_id=1))
        session.commit()

        # This valid write must also disappear when the failed transaction rolls back.
        session.execute(reservations.insert().values(id=2, sala_id=1, usuario_id=1))
        invalid = {"id": 3, "sala_id": 1, "usuario_id": 1, invalid_column: 999}
        with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
            session.execute(reservations.insert().values(**invalid))
        session.rollback()
        assert session.scalars(select(reservations.c.id)).all() == [1]

        session.execute(reservations.insert().values(id=4, sala_id=1, usuario_id=1))
        session.commit()
        assert session.scalars(select(reservations.c.id).order_by(reservations.c.id)).all() == [1, 4]


def test_non_sqlite_engine_has_no_pragma_listener(monkeypatch):
    # No driver, network connection or real server is needed.
    engine = sqlalchemy.create_mock_engine("postgresql://", lambda *args, **kwargs: None)
    monkeypatch.setenv("DATABASE_URL", "postgresql://")

    def create_engine(url, **kwargs):
        assert kwargs["connect_args"] == {}
        return engine

    def unexpected_listener(*args, **kwargs):
        pytest.fail("SQLite listener must not be registered for PostgreSQL")

    monkeypatch.setattr(sqlalchemy, "create_engine", create_engine)
    monkeypatch.setattr(sqlalchemy.event, "listens_for", unexpected_listener)
    path = Path(__file__).resolve().parents[1] / "app" / "database.py"
    spec = importlib.util.spec_from_file_location("isolated_non_sqlite_database", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.engine is engine
