# Raspberry Pi Face and Tool Detection System

A computer vision system for Raspberry Pi that detects faces and tools using MediaPipe and machine learning, with gesture-based triggering for optimized performance.

## Features

- **Face Detection**: Real-time face detection using MediaPipe
- **Tool Detection**: Custom tool recognition system
- **Gesture Triggering**: Only runs detection when hand shows "grabbing" gesture
- **CSV Logging**: Automatic logging of detection events with timestamps
- **Optimized Performance**: Designed specifically for Raspberry Pi hardware

## Project Structure

```
├── Rostro_Herramientas/     # Main face and tool detection module
├── LwM2M Client/           # LWM2M client implementation
├── RanokAI/               # AI-related modules
├── yolov5/                # YOLOv5 integration (deprecated due to performance)
├── detecciones.csv        # Detection event logs
└── requirements.txt       # Python dependencies
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

## Usage

Run the main detection system:
```bash
cd Rostro_Herramientas
python main.py
```

## Hardware Requirements

- Raspberry Pi 4 (recommended)
- Camera module or USB camera
- Minimum 4GB RAM

## Performance Notes

- Uses MediaPipe for efficient face detection
- Gesture-based triggering reduces CPU usage
- TensorFlow Lite models recommended for custom tool detection
- YOLOv5 found to be too resource-intensive for Pi hardware

## Future Development

- [ ] Custom TensorFlow Lite model training for tool detection
- [ ] Enhanced gesture recognition
- [ ] Real-time data streaming via LWM2M
- [ ] Mobile app integration

## License

MIT License
