import asyncio

import cv2
import supervision as sv
from aiohttp_retry import Union

from src.core.model import YOLOModel, load_model
from src.utils.alert_sender import AlertSender
from src.utils.config import settings


class VideoProcessor:
    def __init__(self, source: Union[str, int]):
        self.model = load_model()
        self.alert_sender = AlertSender()
        self.source = source
        self.is_running = False

        # Anotadores para visualización
        self.box_annotator = sv.BoxAnnotator()

        # Variables para video
        self.cap = None
        self.out = None
        self.skip_frames = 2
        self.frame_count = 0
        self.processing_scale = 0.5

        # Sistema de control de alertas
        self.alert_counts = {1: 0, 2: 0}
        self.last_bulk_alert_time = {1: 0, 2: 0}
        self.alert_thresholds = {
            1: 5,  # guns: 5 detecciones
            2: 15,  # risk_woman: 10 detecciones
        }
        self.bulk_alert_cooldown = 20  # 20 segundos
        self.monitoring_enabled = {1: True, 2: True}

    async def initialize(self):
        """Inicializa las capturas de video"""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la fuente de video")

        # Optimizaciones de buffer
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))

        self.out = cv2.VideoWriter(
            "output.mp4",
            cv2.VideoWriter_fourcc(*"mp4v"),
            30 // self.skip_frames,  # Ajustar FPS según frames saltados
            (frame_width, frame_height),
        )

    async def should_monitor(self, class_id: int, current_time: float) -> bool:
        """Determina si se debe monitorear una clase específica"""
        if not self.monitoring_enabled[class_id]:
            # Verificar si pasaron los 5 minutos
            if (
                current_time - self.last_bulk_alert_time[class_id]
            ) > self.bulk_alert_cooldown:
                print(
                    f"📥 Reactivando monitoreo para clase {self.model.get_class_name(class_id)}"
                )
                self.monitoring_enabled[class_id] = True
                return True
            return False
        return True

    async def process_detections(self, results, frame):
        current_time = asyncio.get_event_loop().time()

        if len(results) > 0:
            for i in range(len(results)):
                class_id = results.class_id[i]
                confidence = results.confidence[i]

                # Solo procesar guns y risk_woman
                if class_id in [1, 2]:
                    # Verificar si debemos monitorear esta clase
                    if not await self.should_monitor(class_id, current_time):
                        continue

                    self.alert_counts[class_id] += 1
                    threshold = self.alert_thresholds[class_id]

                    if self.alert_counts[class_id] >= threshold:
                        class_name = self.model.get_class_name(class_id)
                        print(
                            f"🚨 ¡ALERTA MASIVA! Detectados {self.alert_counts[class_id]} {class_name} "
                            f"- Última detección con confianza: {confidence:.2f}"
                        )
                        await self.alert_sender.send_bulk_alert(
                            class_id, confidence, self.alert_counts[class_id]
                        )

                        # Desactivar monitoreo para esta clase
                        self.monitoring_enabled[class_id] = False
                        self.last_bulk_alert_time[class_id] = current_time
                        self.alert_counts[class_id] = 0
                        print(
                            f"📤 Pausando monitoreo para {class_name} durante 20 segundos"
                        )

            # Siempre anotar las detecciones en el frame
            frame = self.box_annotator.annotate(scene=frame, detections=results)

        return frame

    async def cleanup(self):
        """Limpia los recursos del video"""
        self.is_running = False
        if hasattr(self, "cap") and self.cap:
            self.cap.release()
        if hasattr(self, "out") and self.out:
            self.out.release()
        cv2.destroyAllWindows()
        print("🧹 Recursos liberados correctamente")

    async def stop(self):
        """Detiene el procesamiento de video"""
        self.is_running = False
        await self.cleanup()
        print("⏹️ Procesamiento de video detenido")

    async def process_video(self):
        await self.initialize()
        self.is_running = True

        try:
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("Fin del video o error en la captura")
                    break

                self.frame_count += 1

                # Procesar solo algunos frames para optimización
                if self.frame_count % self.skip_frames != 0:
                    self.out.write(frame)
                    cv2.imshow("Sistema de Detección de Seguridad", frame)
                    continue

                # Procesar frame redimensionado
                height, width = frame.shape[:2]
                processed_frame = cv2.resize(
                    frame,
                    (
                        int(width * self.processing_scale),
                        int(height * self.processing_scale),
                    ),
                )

                results = self.model.predict(processed_frame)

                # Escalar detecciones al tamaño original
                if len(results.xyxy) > 0:
                    results.xyxy = results.xyxy * (1 / self.processing_scale)

                annotated_frame = await self.process_detections(results, frame)

                self.out.write(annotated_frame)
                cv2.imshow("Sistema de Detección de Seguridad", annotated_frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    print("Deteniendo procesamiento (ESC presionado)")
                    break

                await asyncio.sleep(0.001)

        except Exception as e:
            print(f"Error en el procesamiento: {e}")
        finally:
            await self.cleanup()
