import logging
from typing import Any, Dict

from groq import Groq

from servidor.settings import Settings
from servidor.usage import DailyTokenCounter

logger = logging.getLogger(__name__)


class GroqClient:
    def __init__(self, settings: Settings, token_counter: DailyTokenCounter):
        self.settings = settings
        self.token_counter = token_counter
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def chat_completion(self, prompt: str, temperature: float = 1.0) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            # Recopilar la respuesta del stream
            response_content = ""
            total_tokens = 0
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response_content += chunk.choices[0].delta.content
                
                # Intentar obtener información de uso si está disponible
                if hasattr(chunk, 'usage') and chunk.usage:
                    total_tokens = chunk.usage.total_tokens

            # Registrar el uso de tokens
            if total_tokens > 0:
                self.token_counter.add_tokens(total_tokens)
            else:
                # Estimación aproximada si no hay datos de uso
                estimated_tokens = len(prompt.split()) + len(response_content.split())
                self.token_counter.add_tokens(estimated_tokens)

            if not response_content.strip():
                logger.error("Empty response from Groq API")
                raise ValueError("Empty response from Groq API")

            return response_content.strip()

        except Exception as e:
            logger.error(f"Error in Groq chat completion: {str(e)}")
            raise
