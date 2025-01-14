import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.responses import HTMLResponse

from src.api.schemas import GeneralMessage, ProtectionAlert, StatusResponse
from src.core.video_processor import VideoProcessor
from src.utils.alert_sender import AlertSender
from src.utils.config import settings

router = APIRouter()
video_processor = None
processing_task = None


@router.post("/control/start")
async def start_video_processing():
    """
    Inicia el procesamiento de video
    """
    global video_processor, processing_task
    try:
        if not video_processor:
            video_processor = VideoProcessor(source=settings.CAMERA_SOURCE)
            await video_processor.initialize()

        if not video_processor.is_running:
            processing_task = asyncio.create_task(video_processor.process_video())
            return {"status": "success", "message": "Procesamiento de video iniciado"}
        return {"status": "info", "message": "El procesamiento ya está en curso"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al iniciar el video: {str(e)}"
        )


@router.post("/control/stop")
async def stop_video_processing():
    """
    Detiene el procesamiento de video
    """
    global video_processor, processing_task
    try:
        if video_processor and video_processor.is_running:
            if processing_task:
                processing_task.cancel()
            await video_processor.stop()
            return {"status": "success", "message": "Procesamiento de video detenido"}
        return {"status": "info", "message": "El procesamiento ya está detenido"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al detener el video: {str(e)}"
        )


@router.get("/status")
async def get_status() -> StatusResponse:
    """
    Obtiene el estado del sistema
    """
    return StatusResponse(
        status="online",
        active_connections=0,
        video_processing=video_processor.is_running if video_processor else False,
    )


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


@router.get("/health", response_class=HTMLResponse)
async def health_check():
    """
    Endpoint de verificación de salud del sistema
    """
    html_content = """
    <html>
        <body>
            <h1 style="color: green; text-align: center;">OK</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


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


# Función de limpieza (opcional)
@router.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    global video_processor, processing_task
    if video_processor:
        if processing_task:
            processing_task.cancel()
        await video_processor.cleanup()
