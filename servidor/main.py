import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Configurar logging para mostrar mensajes de debug
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from seguridad.dependencies import get_settings
from servidor.routers import chat, health, results
# Importación lazy de search para evitar problemas con ChromaDB
try:
    from servidor.routers import search
    search_available = True
except ImportError as e:
    print(f"Warning: RAG search not available: {e}")
    search_available = False

app = FastAPI(
    title="Jarvis Analyst API",
    version="3.1.0",
    description="FastAPI chat API with Groq compound-beta model and RAG search capabilities",
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(results.router)
app.include_router(results.router, prefix="/api", tags=["api"])
if search_available:
    app.include_router(search.router, prefix="/api/v1", tags=["search", "rag"])

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="archivos_estaticos"), name="static")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return FileResponse("archivos_estaticos/index.html")


@app.get("/results")
async def results_page():
    """Página web para visualizar resultados de evaluaciones"""
    return FileResponse("archivos_estaticos/results.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
