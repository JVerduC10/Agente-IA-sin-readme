"""Cliente para la API de Groq."""

import os
from typing import Any, Dict, List, Optional

from groq import Groq

from servidor.config.settings import get_settings

settings = get_settings()


class GroqClient:
    """Cliente para interactuar con la API de Groq."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Inicializa el cliente de Groq.

        Args:
            api_key: API key de Groq. Si no se proporciona, se usa GROQ_API_KEY del entorno.
            model: Modelo a usar. Si no se proporciona, se usa GROQ_MODEL del entorno.
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL or "llama-3.1-70b-versatile"

        if not self.api_key:
            raise ValueError("API key de Groq es requerida")

        self.client = Groq(api_key=self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Realiza una completación de chat usando Groq.

        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Temperatura para la generación
            max_tokens: Máximo número de tokens
            stream: Si usar streaming
            **kwargs: Argumentos adicionales

        Returns:
            Respuesta de la API de Groq
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs,
            )

            if stream:
                return response

            return {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                        },
                        "finish_reason": choice.finish_reason,
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            raise Exception(f"Error en chat completion con Groq: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Obtiene la lista de modelos disponibles.

        Returns:
            Lista de nombres de modelos disponibles
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            # Fallback a modelos conocidos si la API falla
            return [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "deepseek-r1-distill-llama-70b",
            ]

    def validate_connection(self) -> bool:
        """Valida la conexión con la API de Groq.

        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Intenta obtener la lista de modelos como test de conexión
            self.client.models.list()
            return True
        except Exception:
            return False
