from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    email: EmailStr
    senha: str = Field(repr=False)

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A senha não pode ser vazia ou conter apenas espaços.")
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    email: EmailStr
    papel: Literal["user", "admin"]
