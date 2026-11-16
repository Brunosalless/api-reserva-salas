from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    capacidade: Mapped[int] = mapped_column()
    localizacao: Mapped[str] = mapped_column(String(255))