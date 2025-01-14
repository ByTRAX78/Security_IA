import asyncio

import cv2
import supervision as sv

from src.core.model import YOLOModel, load_model
from src.utils.alert_sender import AlertSender
from src.utils.config import settings


class VideoProcessor:
    def __init__(self, source: int = 0):
        self.model = load_model()
        self.alert_sender = AlertSender()
        self.source = source
        self.is_running = False

        # Anotadores para visualización
        self.box_annotator = sv.BoxAnnotator()

        self.last_alert_time = {}
        self.alert_cooldown = 2

        # Variables para el video
        self.cap = None
        self.out = None

    async def initialize(self):
        """Inicializa las capturas de video"""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la fuente de video")

        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))

        self.out = cv2.VideoWriter(
            "output.mp4",
            cv2.VideoWriter_fourcc(*"mp4v"),
            30,
            (frame_width, frame_height),
        )

    async def process_detections(self, results, frame):
        if len(results) > 0:
            for i in range(len(results)):
                class_id = results.class_id[i]
                confidence = results.confidence[i]

                current_time = asyncio.get_event_loop().time()
                if (
                    class_id not in self.last_alert_time
                    or (current_time - self.last_alert_time[class_id])
                    > self.alert_cooldown
                ):

                    class_name = self.model.get_class_name(class_id)
                    if class_id in [0, 1, 2]:
                        print(
                            f"⚠️ ¡ALERTA! {class_name} detectado - Confianza: {confidence:.2f}"
                        )
                        await self.alert_sender.send_alert(class_id, confidence)
                        self.last_alert_time[class_id] = current_time

            # Anotar frame con detecciones
            frame = self.box_annotator.annotate(scene=frame, detections=results)

        return frame

    async def process_video(self):
        await self.initialize()
        self.is_running = True

        try:
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("Fin del video o error en la captura")
                    break

                results = self.model.predict(frame)
                annotated_frame = await self.process_detections(results, frame)

                self.out.write(annotated_frame)
                cv2.imshow("Sistema de Detección de Seguridad", annotated_frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    print("Deteniendo procesamiento (ESC presionado)")
                    break

                await asyncio.sleep(0.01)

        except Exception as e:
            print(f"Error en el procesamiento: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()

    async def stop(self):
        self.is_running = False
        await self.cleanup()
