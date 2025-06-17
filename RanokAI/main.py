import threading
import uvicorn
from api_server import app
from whisper_listener import ejecutar_comando_por_voz
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    # Hilo para correr el servidor web
    hilo_api = threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
    hilo_api.daemon = True
    hilo_api.start()

    # Bucle de escucha por voz
    while True:
        ejecutar_comando_por_voz()