import serial
import time

def conectar_nextion(puerto="/dev/ttyS0", baudrate=9600):
    try:
        ser = serial.Serial(puerto, baudrate, timeout=1)
        time.sleep(2)  # Esperar a que se establezca la conexión
        print("Conectado a pantalla Nextion")
        return ser
    except Exception as e:
        print("No se pudo conectar con Nextion:", e)
        return None

def cambiar_imagen(ser, imagen_id=1):
    try:
        comando = f"pic0.pic={imagen_id}" + "\xFF\xFF\xFF"
        ser.write(comando.encode())
        print(f"📺 Imagen cambiada a ID {imagen_id}")
    except Exception as e:
        print("❌ Error al enviar comando a Nextion:", e)