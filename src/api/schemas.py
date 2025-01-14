# src/api/schemas.py
from typing import Dict, List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float


class ProtectionAlert(BaseModel):
    location: Location
    message: str
    emergency_type: str
    user_id: str


class GeneralMessage(BaseModel):
    message: str
    user_id: str
    message_type: str


class Detection(BaseModel):
    class_id: int
    confidence: float
    class_name: str
    bbox: List[float]


class DetectionResponse(BaseModel):
    type: str
    detections: List[Detection]
    timestamp: str


class StatusResponse(BaseModel):
    status: str
    active_connections: int
    video_processing: bool
    last_detection: Optional[str] = None
