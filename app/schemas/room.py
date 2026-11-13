from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


class RoomCreate(BaseModel):
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    capacidade: Annotated[int, Field(strict=True, gt=0)]
    localizacao: str

    @field_validator("localizacao")
    @classmethod
    def validate_localizacao(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A localização não pode ser vazia ou conter apenas espaços.")
        return value


class RoomRead(RoomCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
