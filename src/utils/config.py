# src/utils/config.py
from typing import Dict

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Host y puerto
    HOST: str = "localhost"  # Por defecto localhost
    PORT: int = 8000

    # URLs construidas dinámicamente
    @property
    def API_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    @property
    def WEBSOCKET_URL(self) -> str:
        return f"ws://{self.HOST}:{self.PORT}/ws"

    # Configuración de cámara
    CAMERA_ID: str = "CAM_001"
    # CAMERA_SOURCE: int = 0  # 0 para webcam
    CAMERA_SOURCE: str = "video-samples/video2.mp4"

    # Ubicación por defecto (puede ser actualizada en tiempo real)
    DEFAULT_LOCATION: Dict[str, float] = {"lat": 0.0, "lon": 0.0}

    # Configuración del modelo
    MODEL_ID: str = "weapons_v2_adrian/9"
    CONFIDENCE_THRESHOLD: float = 0.5

    # Tiempos de cooldown para alertas (en segundos)
    ALERT_COOLDOWN: int = 2

    # Configuración de video
    VIDEO_OUTPUT_PATH: str = "output.mp4"
    FRAME_RATE: int = 30

    # Roboflow
    ROBOFLOW_API_KEY: str = ""

    class Config:
        env_file = ".env"


# Crear instancia de configuración
settings = Settings()
