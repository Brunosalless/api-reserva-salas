from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.core.errors import http_exception_handler, request_validation_error_handler
from app.routers.health import router as health_router

app = FastAPI()

app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(health_router)
