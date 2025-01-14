# src/utils/config.py
from typing import Dict

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API y servidor
    API_URL: str = "http://localhost:8000"
    WEBSOCKET_URL: str = "ws://localhost:8000/ws"

    # Configuración de cámara
    CAMERA_ID: str = "CAM_001"
    CAMERA_SOURCE: int = 0  # 0 para webcam

    # Ubicación por defecto (puede ser actualizada en tiempo real)
    DEFAULT_LOCATION: Dict[str, float] = {"lat": 0.0, "lon": 0.0}

    # Configuración del modelo
    MODEL_ID: str = "weapons_v2_adrian/4"
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