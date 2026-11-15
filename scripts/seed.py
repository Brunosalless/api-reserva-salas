
import os

import bcrypt
from dotenv import load_dotenv

load_dotenv()


def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")

    if len(senha_bytes) > 72:
        raise ValueError("A senha não pode ultrapassar 72 bytes.")

    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)

    return senha_hash.decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )


def main() -> None:
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        raise RuntimeError(
            "Defina ADMIN_EMAIL e ADMIN_PASSWORD no arquivo .env."
        )

    print("Configuração do administrador encontrada.")
    print("O seed do banco aguarda os modelos da T-4.")


if __name__ == "__main__":
    main()
