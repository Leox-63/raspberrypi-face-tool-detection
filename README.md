# Raspberry Pi Face and Tool Detection System

Un sistema completo de visión por computadora para Raspberry Pi que detecta rostros y herramientas usando MediaPipe y machine learning, con activación por gestos para rendimiento optimizado.

## Características

- **Detección de Rostros**: Detección en tiempo real usando MediaPipe
- **Detección de Herramientas**: Sistema de reconocimiento personalizado de herramientas
- **Activación por Gestos**: Solo ejecuta detección cuando la mano muestra gesto de "agarrar"
- **Logging CSV**: Registro automático de eventos de detección con timestamps
- **Cliente LwM2M**: Cliente Python completo que reemplaza implementación Java Leshan
- **Sistema RanokAI**: API server, control Nextion, TTS y reconocimiento de voz
- **Rendimiento Optimizado**: Diseñado específicamente para hardware Raspberry Pi

## Estructura del Proyecto

```
├── Rostro_Herramientas/     # Módulo principal de detección de rostros y herramientas
│   └── main.py             # Script principal de detección con MediaPipe
├── LwM2M Client/           # Cliente LwM2M Python completo
│   ├── main.py             # Cliente LwM2M básico
│   ├── enhanced_main.py    # Cliente mejorado con integración de detección
│   ├── config.json         # Configuración del cliente
│   └── lwm2m_client/       # Módulo del cliente LwM2M
├── RanokAI/               # Módulos relacionados con IA
│   ├── api_server.py       # Servidor API REST
│   ├── nextion_control.py  # Control de pantalla Nextion
│   ├── tts_engine.py       # Motor de texto a voz
│   └── whisper_listener.py # Reconocimiento de voz
├── detecciones.csv        # Logs de eventos de detección
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Python_Proj
```

2. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Uso

### Sistema de Detección
Ejecutar el sistema principal de detección:
```bash
cd Rostro_Herramientas
python main.py
```

### Cliente LwM2M
Ejecutar el cliente LwM2M básico:
```bash
cd "LwM2M Client"
python main.py
```

Ejecutar el cliente mejorado con integración de detección:
```bash
cd "LwM2M Client"
python enhanced_main.py
```

### Sistema RanokAI
Ejecutar los módulos de IA:
```bash
cd RanokAI
python main.py
```

## Hardware Requirements

- Raspberry Pi 4 (recommended)
- Camera module or USB camera
- Minimum 4GB RAM

## Estado del Proyecto

✅ **COMPLETADO:**
- Sistema de detección de rostros y herramientas con MediaPipe
- Cliente LwM2M Python que reemplaza implementación Java Leshan
- Sistema RanokAI con API, TTS y reconocimiento de voz
- Integración completa entre todos los módulos
- Optimización para hardware Raspberry Pi
- Documentación completa

## Notas de Rendimiento

- Usa MediaPipe para detección eficiente de rostros
- Activación por gestos reduce uso de CPU
- Modelos TensorFlow Lite recomendados para detección personalizada de herramientas
- YOLOv5 encontrado muy intensivo para hardware Pi (incluido pero no recomendado)

## Desarrollo Futuro

- [x] Entrenamiento de modelo TensorFlow Lite personalizado para detección de herramientas
- [x] Reconocimiento de gestos mejorado
- [x] Streaming de datos en tiempo real vía LWM2M
- [ ] Integración con aplicación móvil

## License

MIT License
