import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.core.video_processor import VideoProcessor
from src.utils.alert_sender import AlertSender
from src.utils.config import settings

app = FastAPI(title="Security IA System")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(router)

# Variables globales para el procesamiento de video
video_processor = None
processing_task = None


@app.on_event("startup")
async def startup_event():
    """Iniciar el procesamiento de video cuando arranca la API"""
    global video_processor, processing_task
    try:
        print("🚀 Iniciando sistema...")

        # Inicializar el procesador de video
        video_processor = VideoProcessor(source=settings.CAMERA_SOURCE)
        await video_processor.initialize()

        # Iniciar el procesamiento en segundo plano
        processing_task = asyncio.create_task(video_processor.process_video())

        print("✅ Sistema iniciado correctamente")

    except Exception as e:
        print(f"❌ Error al iniciar el sistema: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    global video_processor, processing_task
    try:
        if processing_task:
            processing_task.cancel()
        if video_processor:
            await video_processor.cleanup()
        print("👋 Sistema detenido correctamente")
    except Exception as e:
        print(f"❌ Error al detener el sistema: {str(e)}")


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "Security IA System",
        "status": "running",
        "video_processing": video_processor is not None and video_processor.is_running,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
