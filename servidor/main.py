from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import logging

from servidor.config import get_settings
from servidor.core.error_handler import register_error_handlers
from servidor.routers import chat, health

# Importación lazy de search para evitar problemas con ChromaDB
try:
    from servidor.routers import search
    search_available = True
except ImportError as e:
    print(f"Warning: RAG search not available: {e}")
    search_available = False

# Importación del router de preguntas
try:
    from servidor.routers import questions
    questions_available = True
except ImportError as e:
    print(f"Warning: Questions system not available: {e}")
    questions_available = False

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description=settings.app.app_description,
    debug=settings.app.debug
)

# Registrar manejadores de errores centralizados
register_error_handlers(app)

# Incluir routers
app.include_router(health.router)
app.include_router(chat.router, prefix="/api")

if search_available:
    app.include_router(search.router, prefix="/api/v1", tags=["search", "rag"])

if questions_available and settings.QUESTIONS_ENABLED:
    app.include_router(questions.router, prefix="/api/v1", tags=["questions"])

# Servir archivos estáticos
if settings.app.static_files_enabled:
    app.mount(settings.app.static_files_path, StaticFiles(directory=settings.app.static_files_directory), name="static")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.allowed_origins_list,
    allow_credentials=settings.security.allow_credentials,
    allow_methods=settings.security.allowed_methods,
    allow_headers=settings.security.allowed_headers,
)


@app.get("/")
async def root():
    return FileResponse(f"{settings.app.static_files_directory}/index.html")




if __name__ == "__main__":
    import uvicorn
    
    # Usar configuración del servidor desde settings
    uvicorn_config = settings.app.server_config
    uvicorn.run(app, **uvicorn_config)
