from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomRead, RoomPage


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


@router.get("", response_model=RoomPage)
def listar_salas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página (começa em 1)"),
    size: int = Query(10, ge=1, le=100, description="Número de itens por página (máximo 100)"),
):
    total_salas = db.execute(select(func.count(Room.id))).scalar_one()
    salas = db.execute(select(Room).order_by(Room.id).offset((page - 1) * size).limit(size)).scalars().all()
    return RoomPage(items=salas, total=total_salas, page=page, size=size)