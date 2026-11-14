from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import http_exception_handler, request_validation_error_handler
from app.schemas.user import UserCreate, UserRead


class SensitiveInput(BaseModel):
    senha: str

    @field_validator("senha")
    @classmethod
    def reject_password(cls, value):
        raise ValueError(f"Sensitive validator context: {value}")


@pytest.fixture
def client():
    app = FastAPI()
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    @app.post("/users", response_model=UserRead)
    def create_user(payload: UserCreate):
        return SimpleNamespace(
            id=1, nome=payload.nome, email=payload.email, papel="user",
            senha=payload.senha, senha_hash="HASH_MARKER",
        )

    @app.post("/sensitive")
    def sensitive(payload: SensitiveInput):
        return {}

    @app.get("/errors/{status_code}")
    def error(status_code: int):
        if status_code == 401:
            raise HTTPException(401, "Login necessário", headers={"WWW-Authenticate": "Bearer"})
        if status_code == 409:
            raise HTTPException(409, "E-mail já cadastrado")
        raise StarletteHTTPException(403, {"senha": "SECRET_MARKER", "traceback": "TRACE_MARKER"})

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    "path,payload,fields",
    [
        ("/users", {}, {"body.nome", "body.email", "body.senha"}),
        ("/users", {"nome": "Ana", "email": "SECRET_MARKER", "senha": "PASSWORD_MARKER"}, {"body.email"}),
        ("/sensitive", {"senha": "PASSWORD_MARKER"}, {"body.senha"}),
    ],
)
def test_validation_errors_do_not_expose_input_or_context(client, path, payload, fields):
    response = client.post(path, json=payload)
    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"status", "message", "errors"}
    assert body["status"] == 422
    assert body["message"] == "Erro de validação"
    assert {error["field"] for error in body["errors"]} == fields
    assert all(set(error) == {"field", "message"} and error["message"] for error in body["errors"])
    assert all(marker not in response.text for marker in ("SECRET_MARKER", "PASSWORD_MARKER", "Traceback", "ValueError"))


@pytest.mark.parametrize(
    "method,path,status,message,header",
    [
        ("GET", "/errors/401", 401, "Login necessário", ("WWW-Authenticate", "Bearer")),
        ("GET", "/missing", 404, "Not Found", None),
        ("GET", "/users", 405, "Method Not Allowed", ("Allow", "POST")),
        ("GET", "/errors/409", 409, "E-mail já cadastrado", None),
        ("GET", "/errors/403", 403, "Forbidden", None),
    ],
)
def test_http_errors_preserve_messages_and_headers(client, method, path, status, message, header):
    response = client.request(method, path)
    assert response.status_code == status
    assert response.json() == {"status": status, "message": message}
    if header:
        assert response.headers[header[0]] == header[1]
    assert all(marker not in response.text for marker in ("SECRET_MARKER", "TRACE_MARKER", "Traceback"))


def test_user_response_excludes_password_and_hash(client):
    response = client.post(
        "/users", json={"nome": "Ana", "email": "ana@example.com", "senha": "PASSWORD_MARKER"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "nome": "Ana", "email": "ana@example.com", "papel": "user"}
    assert "PASSWORD_MARKER" not in response.text
    assert "HASH_MARKER" not in response.text
