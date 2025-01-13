import time

import cv2
import supervision as sv
from inference import get_model


def load_model():
    print("Cargando modelo...")
    return get_model(model_id="weapons_v2_adrian/3")


# Cargar el modelo una sola vez
model = load_model()

# Configurar la captura de video
video_path = "video-muestra/video2.mp4"
cap = cv2.VideoCapture(video_path)

# Obtener propiedades del video
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Configurar el video writer para guardar el resultado
out = cv2.VideoWriter(
    "output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, (frame_width, frame_height)
)

# Crear los anotadores una sola vez
bounding_box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Variable para controlar el tiempo entre alertas
last_alert_time = {}
alert_cooldown = 2  # Tiempo en segundos entre alertas

# Diccionario de clases
class_names = {0: "Sospechoso", 1: "guns", 2: "risk_woman"}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Fin del video")
        break

    # Realizar inferencia en el frame actual
    results = model.infer(frame)[0]
    detections = sv.Detections.from_inference(results)

    # Procesar las detecciones
    if len(detections) > 0:
        for i in range(len(detections)):
            # Obtener la clase y confianza de la detección
            class_id = detections.class_id[i]
            confidence = detections.confidence[i]

            current_time = time.time()

            # Verificar el tiempo de cooldown para las alertas
            if (
                class_id not in last_alert_time
                or (current_time - last_alert_time[class_id]) > alert_cooldown
            ):
                class_name = class_names[class_id]

                if class_id == 0:  # Sospechoso
                    print(
                        f"⚠️ ¡ALERTA! Persona sospechosa detectada - Confianza: {confidence:.2f}"
                    )
                elif class_id == 1:  # guns
                    print(f"🔫 ¡PELIGRO! Arma detectada - Confianza: {confidence:.2f}")
                elif class_id == 2:  # risk_woman
                    print(
                        f"⚠️ ¡ALERTA! Mujer en situación de riesgo detectada - Confianza: {confidence:.2f}"
                    )

                # Actualizar el tiempo de la última alerta
                last_alert_time[class_id] = current_time

    # Anotar el frame
    annotated_frame = bounding_box_annotator.annotate(
        scene=frame, detections=detections
    )
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=detections
    )

    # Guardar el frame procesado
    out.write(annotated_frame)

    # Mostrar el frame
    cv2.imshow("Sistema de Detección de Seguridad", annotated_frame)

    # Presiona 'ESC' para salir
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Liberar recursos
cap.release()
out.release()
cv2.destroyAllWindows()

# export ROBOFLOW_API_KEY="XvZfPfAfQHKopwxiRSBe"
