import pyttsx3

def hablar_sexy(texto):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    
    # Opcional: elige una voz en español si está disponible
    for voice in engine.getProperty('voices'):
        if "spanish" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.say(texto)
    engine.runAndWait()