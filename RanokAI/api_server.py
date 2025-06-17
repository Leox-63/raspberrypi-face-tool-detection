# api_server.py
from fastapi import FastAPI
from tts_engine import hablar_sexy
from nextion_control import conectar_nextion, cambiar_imagen

app = FastAPI()
ser = conectar_nextion()

@app.get("/")
def raiz():
    return {"status": "Diosa digital online ✨"}

@app.post("/modo_cute")
def modo_cute():
    if ser:
        cambiar_imagen(ser, 1)
    hablar_sexy("Activando modo cute, mi amor")
    return {"mensaje": "Modo cute activado"}

@app.post("/chisme")
def chisme():
    hablar_sexy("Ay amor, te cuento un chisme de las IAs")
    return {"mensaje": "Chisme contado"}