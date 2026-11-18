
import os

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import SessionLocal
from app.models import User

load_dotenv()


def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) > 72:
        raise ValueError("A senha não pode ultrapassar 72 bytes.")

    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )


def main() -> None:
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if not admin_email or not admin_password:
        raise RuntimeError(
            "Defina ADMIN_EMAIL e ADMIN_PASSWORD no arquivo .env."
        )

    if len(admin_password.encode("utf-8")) > 72:
        raise ValueError("A senha não pode ultrapassar 72 bytes.")

    with SessionLocal() as db:
        usuario_existente = db.scalar(
            select(User).where(User.email == admin_email)
        )

        if usuario_existente:
            print("O usuário administrador já existe. Nenhuma alteração realizada.")
            return

        admin = User(
            nome="Administrador",
            email=admin_email,
            senha_hash=gerar_hash_senha(admin_password),
            papel="admin",
        )

        db.add(admin)
        db.commit()

        print("Administrador criado com sucesso!")


if __name__ == "__main__":
    main()
