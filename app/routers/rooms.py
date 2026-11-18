from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomRead


router = APIRouter(prefix="/api/rooms", tags=["salas"])


def verificar_admin():
    # TODO: Por enquanto não faz nada, porque o login ainda não existe, mas futuramente vai verificar se o usuário é admin
    pass


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verificar_admin)])
def criar_sala(dados: RoomCreate, db: Session = Depends(get_db)):
    nova_sala = Room(nome=dados.nome, capacidade=dados.capacidade, localizacao=dados.localizacao)
    db.add(nova_sala)
    db.commit()
    db.refresh(nova_sala)
    return nova_sala    