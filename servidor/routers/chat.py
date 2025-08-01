import logging
import asyncio
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import Optional, Literal

from app.dependencies import get_settings
from app.security import check_api_key
from app.settings import Settings
from app.usage import DailyTokenCounter
from app.utils.search import buscar_web, refinar_query, WebSearchError
from app.utils.scrape import extraer_contenido_multiple, WebScrapingError
from scripts.groq_client import GroqClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class Msg(BaseModel):
    prompt: str
    query_type: Optional[Literal["scientific", "creative", "general", "web"]] = "general"
    temperature: Optional[float] = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt_length(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        if len(v) > 1000:
            raise ValueError("Prompt too long")
        return v
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 2):
            raise ValueError("Temperature must be between 0 and 2")
        return v


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    detail: str


@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def chat_endpoint(
    request: Request, msg: Msg, settings: Settings = Depends(get_settings)
) -> ChatResponse:
    api_key = request.headers.get("X-API-Key")
    if settings.API_KEYS and not check_api_key(api_key or "", settings):
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Determinar temperatura basada en el tipo de consulta
        if msg.temperature is not None:
            temperature = msg.temperature
        else:
            temperature = settings.temperature_map.get(msg.query_type, 0.7)
        
        # Verificar si es una consulta web
        if msg.query_type == "web":
            answer = await deepsearch_flow(msg.prompt, settings)
            return ChatResponse(answer=answer)
        
        # Flujo tradicional para otros tipos de consulta
        answer = await legacy_chat_flow(msg.prompt, temperature, settings)
        return ChatResponse(answer=answer)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def legacy_chat_flow(prompt: str, temperature: float, settings: Settings) -> str:
    """
    Flujo de chat tradicional sin búsqueda web.
    """
    token_counter = DailyTokenCounter()
    groq_client = GroqClient(settings, token_counter)
    response = await groq_client.chat_completion(prompt, temperature=temperature)
    return response


async def deepsearch_flow(question: str, settings: Settings, max_iters: int = None) -> str:
    """
    Flujo de búsqueda web profunda: buscar -> leer -> razonar.
    
    Args:
        question: Pregunta del usuario
        settings: Configuración de la aplicación
        max_iters: Máximo número de iteraciones (por defecto usa MAX_SEARCH_ITERATIONS)
    
    Returns:
        Respuesta fundamentada con información web
    """
    if max_iters is None:
        max_iters = settings.MAX_SEARCH_ITERATIONS
    
    logger.info(f"Iniciando búsqueda web para: {question}")
    
    try:
        query = await refinar_query(question)
        previous_answer = None
        
        for iteration in range(max_iters):
            logger.info(f"Iteración {iteration + 1}/{max_iters} - Query: {query}")
            
            # Paso 1: Buscar en la web
            try:
                resultados = await buscar_web(query, settings)
                if not resultados:
                    logger.warning(f"No se encontraron resultados para: {query}")
                    break
            except WebSearchError as e:
                logger.error(f"Error en búsqueda web: {e}")
                if iteration == 0:
                    return f"Error en la búsqueda web: {e}. No se pudo obtener información actualizada."
                break
            
            # Paso 2: Leer contenido de las páginas
            urls = [r["url"] for r in resultados if r["url"]]
            if not urls:
                logger.warning("No se encontraron URLs válidas")
                break
                
            try:
                textos = await extraer_contenido_multiple(urls, settings)
            except Exception as e:
                logger.error(f"Error al extraer contenido: {e}")
                textos = [f"Error al leer contenido: {e}"]
            
            # Paso 3: Construir contexto para el modelo
            contexto = construir_contexto_web(resultados, textos)
            
            # Paso 4: Generar respuesta con el modelo
            prompt = construir_prompt_rag(question, contexto)
            
            token_counter = DailyTokenCounter()
            groq_client = GroqClient(settings, token_counter)
            
            try:
                answer = await groq_client.chat_completion(
                    prompt, 
                    temperature=settings.temperature_map["web"]
                )
            except Exception as e:
                logger.error(f"Error al generar respuesta: {e}")
                return f"Error al generar respuesta: {e}"
            
            # Paso 5: Verificar si necesita más búsqueda
            if not necesita_mas_busqueda(answer) or iteration == max_iters - 1:
                logger.info(f"Búsqueda completada en {iteration + 1} iteraciones")
                return answer
            
            # Preparar siguiente iteración
            query = await refinar_query(question, answer)
            previous_answer = answer
        
        # Si llegamos aquí, se agotaron las iteraciones
        return previous_answer or "No se pudo obtener información suficiente de la web."
        
    except Exception as e:
        logger.error(f"Error inesperado en deepsearch_flow: {e}")
        return f"Error en la búsqueda web: {e}"


def construir_contexto_web(resultados: List[Dict[str, str]], textos: List[str]) -> str:
    """
    Construye el contexto web a partir de los resultados y textos extraídos.
    """
    contexto_partes = []
    
    for i, (resultado, texto) in enumerate(zip(resultados, textos)):
        parte = f"""FUENTE {i+1}:
Título: {resultado['titulo']}
URL: {resultado['url']}
Descripción: {resultado['snippet']}
Contenido: {texto[:500]}...
"""
        contexto_partes.append(parte)
    
    return "\n\n".join(contexto_partes)


def construir_prompt_rag(question: str, contexto: str) -> str:
    """
    Construye el prompt RAG con la información web.
    """
    return f"""Eres un asistente de investigación especializado. Tu tarea es responder preguntas usando ÚNICAMENTE la información web proporcionada a continuación.

INSTRUCCIONES:
1. Usa solo la información de las fuentes web proporcionadas
2. Proporciona respuestas precisas y objetivas
3. Menciona datos concretos cuando sea relevante
4. Si la información es insuficiente, indícalo claramente
5. Mantén un tono profesional y factual

INFORMACIÓN WEB:
{contexto}

PREGUNTA DEL USUARIO: {question}

RESPUESTA:"""


def necesita_mas_busqueda(answer: str) -> bool:
    """
    Determina si la respuesta indica que se necesita más información.
    """
    indicadores = [
        "información insuficiente",
        "información es insuficiente",
        "no se encontró información",
        "no se encontró información relevante",
        "requiere más detalles",
        "requiere más detalles específicos",
        "información limitada",
        "necesita más búsqueda",
        "más información necesaria"
    ]
    
    answer_lower = answer.lower()
    return any(indicador in answer_lower for indicador in indicadores)
