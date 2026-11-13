from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.room import RoomCreate, RoomRead
from app.schemas.user import UserCreate, UserRead


ROOM = {"nome": "Sala A", "capacidade": 10, "localizacao": "Bloco A"}
USER = {"nome": "Ana", "email": "ana@example.com", "senha": " secret "}


@pytest.mark.parametrize(
    "schema,payload,field",
    [
        (schema, {**ROOM, "id": 1, field: value}, field)
        for schema in (RoomCreate, RoomRead)
        for field, values in (
            ("nome", ("", " \t\n")),
            ("localizacao", ("", " \t\n")),
            ("capacidade", (0, -1, 1.5, 2.0, True, "2")),
        )
        for value in values
    ]
    + [
        (UserCreate, {**USER, field: value}, field)
        for field, values in (
            ("nome", ("", " \t\n")),
            ("email", ("invalido",)),
            ("senha", ("", " \t\n")),
            ("papel", ("user", "admin")),
            ("senha_hash", ("hash",)),
        )
        for value in values
    ]
    + [
        (UserCreate, {key: value for key, value in USER.items() if key != "senha"}, "senha"),
        (UserRead, {"id": 1, **USER, "papel": "owner"}, "papel"),
    ],
)
def test_invalid_input(schema, payload, field):
    with pytest.raises(ValidationError) as caught:
        schema.model_validate(payload)
    assert any(error["loc"] == (field,) for error in caught.value.errors())


def test_valid_creation_preserves_password_and_normalizes_name():
    user = UserCreate(**{**USER, "nome": " Ana "})
    assert user.model_dump() == USER
    assert "secret" not in repr(user)
    room = RoomCreate(**{**ROOM, "nome": " Sala A "})
    assert room.model_dump() == ROOM


@pytest.mark.parametrize("papel", ["user", "admin"])
def test_read_from_attributes_excludes_credentials(papel):
    public = {"id": 1, "nome": USER["nome"], "email": USER["email"], "papel": papel}
    source = SimpleNamespace(**public, senha=USER["senha"], senha_hash="HASH_MARKER")
    user = UserRead.model_validate(source)
    assert user.model_dump() == public
    assert "senha" not in user.model_dump_json()
    assert RoomRead.model_validate(SimpleNamespace(id=1, **ROOM)).model_dump() == {
        "id": 1, **ROOM
    }
