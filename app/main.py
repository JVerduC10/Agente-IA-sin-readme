from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

# Configuración de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# Crear la aplicación FastAPI
app = FastAPI(title="IA Agent - Restaurant Assistant", version="1.0.0")

# Modelo de entrada
class Msg(BaseModel):
    prompt: str

# System prompt para el asistente de restaurantes
SYSTEM_PROMPT = (
    "Eres un asistente experto para el sector restaurante. "
    "Responde en español de forma concisa y cita siempre la fuente."
)

# Endpoint principal
@app.post("/chat")
async def chat(msg: Msg):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "temperature": 1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg.prompt}
            ]
        }
        
        response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return {"answer": answer}
        else:
            return {"answer": f"Error API: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

# Endpoint de salud
@app.get("/")
async def root():
    return {"message": "IA Agent - Restaurant Assistant API"}