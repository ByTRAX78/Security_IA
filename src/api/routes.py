from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, WebSocket

from src.api.schemas import GeneralMessage, ProtectionAlert, StatusResponse
from src.core.video_processor import VideoProcessor
from src.utils.alert_sender import AlertSender

router = APIRouter()
video_processor = None


@router.on_event("startup")
async def startup_event():
    global video_processor
    try:
        video_processor = VideoProcessor(source=0)
        await video_processor.initialize()
        print("✅ Sistema iniciado correctamente")
    except Exception as e:
        print(f"❌ Error al iniciar el sistema: {str(e)}")


@router.on_event("shutdown")
async def shutdown_event():
    if video_processor:
        await video_processor.cleanup()
        print("👋 Sistema detenido correctamente")


@router.get("/status")
async def get_status() -> StatusResponse:
    return StatusResponse(
        status="online",
        active_connections=0,
        video_processing=video_processor.is_running if video_processor else False,
    )


@router.post("/control/start")
async def start_video_processing():
    """
    Inicia el procesamiento de video
    """
    if not video_processor.is_running:
        await video_processor.process_video()
        return {"status": "success", "message": "Procesamiento de video iniciado"}
    return {"status": "info", "message": "El procesamiento ya está en curso"}


@router.post("/control/stop")
async def stop_video_processing():
    """
    Detiene el procesamiento de video
    """
    if video_processor.is_running:
        await video_processor.stop()
        return {"status": "success", "message": "Procesamiento de video detenido"}
    return {"status": "info", "message": "El procesamiento ya está detenido"}


@router.post("/protection", response_model=dict)
async def handle_protection(alert: ProtectionAlert):
    try:
        result = {
            "status": "received",
            "message": "Alerta de protección registrada",
            "timestamp": datetime.now().isoformat(),
            "details": alert.dict(),
        }
        print(f"✅ Alerta recibida: {alert.dict()}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket para streaming de detecciones en tiempo real
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Procesar datos recibidos del cliente si es necesario
            # Enviar actualizaciones de detecciones al cliente
    except Exception as e:
        print(f"Error en WebSocket: {e}")
    finally:
        await websocket.close()
