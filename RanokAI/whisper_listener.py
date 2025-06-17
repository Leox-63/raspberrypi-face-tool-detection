import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import tempfile
from tts_engine import hablar_sexy
from nextion_control import cambiar_imagen, conectar_nextion
import warnings

# Silenciar advertencia de FP16 si estás en CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Conectar al Nextion una sola vez
ser = conectar_nextion()

# Cargar el modelo de Whisper localmente
modelo_whisper = whisper.load_model("tiny")  # Usa "base", "small", etc. si quieres más precisión

def grabar_y_transcribir(duracion=5):
    print("🎙️ Grabando... Habla ahora, mi reina")
    fs = 44100
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1)
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        write(temp_audio.name, fs, audio)
        print("✅ Grabación guardada, transcribiendo localmente...")

        resultado = modelo_whisper.transcribe(temp_audio.name)
        texto = resultado["text"]
        print(f"📝 Transcripción: {texto}")
        return texto.lower()

def ejecutar_comando_por_voz():
    texto = grabar_y_transcribir()
    
    if "modo cute" in texto:
        if ser:
            cambiar_imagen(ser, 1)
        hablar_sexy("Modo cute activado, mi amorcito")
    
    elif "chisme" in texto:
        hablar_sexy("Ay chiqui, este chisme está calientito... Elon Musk quiere fusionarse con una tostadora")
    
    elif "apaga luces" in texto:
        hablar_sexy("Luces apagadas. Hora del mood misterioso")
        # Aquí puedes agregar control GPIO si quieres
    
    else:
        hablar_sexy("No entendí, pero igual te adoro 💕")