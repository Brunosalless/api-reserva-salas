from fastapi import APIRouter

router = APIRouter()

@router.get("/ok")
def health_check():
    return {"mensagem": "Servidor está funcionando corretamente!"}