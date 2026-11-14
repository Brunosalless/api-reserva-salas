from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "message": "Erro de validação",
            "errors": [
                {
                    "field": ".".join(str(part) for part in error["loc"]),
                    "message": "Campo obrigatório"
                    if error["type"] == "missing"
                    else "Valor inválido",
                }
                for error in exc.errors()
            ],
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, str):
        message = exc.detail
    else:
        try:
            message = HTTPStatus(exc.status_code).phrase
        except ValueError:
            message = "Erro HTTP"

    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "message": message},
        headers=exc.headers,
    )
