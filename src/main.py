import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
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


@app.on_event("startup")
async def startup_event():
    """Iniciar la API"""
    print("🚀 API iniciada correctamente")


@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {"message": "Security IA System", "status": "running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Esto permite conexiones desde cualquier IP
        port=settings.PORT,
        reload=True,
    )
