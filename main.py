from fastapi import FastAPI

app = FastAPI()

@app.get("/ok")
def verificar_status():
    return {"mensagem": "Servidor está funcionando corretamente!"}