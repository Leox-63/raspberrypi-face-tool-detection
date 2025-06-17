import cv2
from picamera2 import Picamera2
import time
import mediapipe as mp
import tflite_runtime.interpreter as tflite
import numpy as np
import csv
from datetime import datetime

# Carga el modelo TFLite de herramientas
interpreter = tflite.Interpreter(model_path="tu_modelo_herramientas.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (160, 120)})
picam2.configure(preview_config)
picam2.start()
time.sleep(1)

mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

csv_file = open("detecciones.csv", mode="a", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["timestamp", "rostro_detectado", "herramienta_detectada"])

try:
    while True:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detección de manos y gesto de tomar
        mano_gesto_tomar = False
        results = hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                y_punta_medio = hand_landmarks.landmark[12].y
                y_palma = hand_landmarks.landmark[0].y
                if abs(y_punta_medio - y_palma) < 0.12:
                    mano_gesto_tomar = True

        rostro_detectado = False
        herramienta_detectada = ""

        # Solo si la mano está en gesto de tomar, ejecuta rostro y TFLite
        if mano_gesto_tomar:
            # Detección de rostro
            face_results = face_detection.process(rgb)
            if face_results.detections:
                rostro_detectado = True
                for detection in face_results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)

            # Detección de herramientas con TFLite (solo cuando hay gesto)
            # Preprocesa el frame para el modelo
            input_shape = input_details[0]['shape']
            img_resized = cv2.resize(frame, (input_shape[2], input_shape[1]))
            input_data = np.expand_dims(img_resized, axis=0).astype(np.float32) / 255.0
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])

            # Procesa la salida (esto depende de cómo entrenaste tu modelo)
            # Ejemplo: si output_data es [ [prob_herramienta1, prob_herramienta2, ...] ]
            class_names = ["scissors", "hammer", "wrench", "screwdriver"]  # Cambia por tus clases
            pred_idx = int(np.argmax(output_data))
            confidence = float(np.max(output_data))
            if confidence > 0.7:  # Ajusta el umbral según tu modelo
                herramienta_detectada = class_names[pred_idx]
                cv2.putText(frame, herramienta_detectada, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # Solo guarda si hay rostro y herramienta detectada
            if rostro_detectado and herramienta_detectada:
                csv_writer.writerow([datetime.now().isoformat(), True, herramienta_detectada])
                csv_file.flush()
                print(f"Evento registrado: rostro y {herramienta_detectada}")

        cv2.imshow("Caritas, manitas y herramientas detectadas", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(" Cerrando... Besitos, amigui.")
            break
except KeyboardInterrupt:
    print("\nInterrumpido. Cerrando...")

csv_file.close()
cv2.destroyAllWindows()