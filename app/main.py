from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.dependencies import get_settings
from app.routers import chat, health

app = FastAPI(
    title="Jarvis Analyst API",
    version="2.0.0",
    description="FastAPI chat API with Groq compound-beta model (includes DeepSeek, Meta, and other models)",
)

app.include_router(health.router)
app.include_router(chat.router)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
