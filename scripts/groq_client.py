import requests
import logging
from typing import Dict, Any
from app.settings import Settings
from app.usage import DailyTokenCounter

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, settings: Settings, token_counter: DailyTokenCounter):
        self.settings = settings
        self.token_counter = token_counter
    
    def _create_payload(self, prompt: str) -> Dict[str, Any]:
        return {
            "model": self.settings.GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    def _create_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response: requests.Response) -> str:
        if response.status_code == 401:
            logger.error("Invalid Groq API key")
            raise requests.exceptions.HTTPError("Invalid Groq API key", response=response)
        
        if response.status_code != 200:
            logger.error(f"HTTP error from Groq API: {response.status_code}")
            response.raise_for_status()
        
        try:
            data = response.json()
        except ValueError as e:
            logger.error("Invalid response structure from Groq API")
            raise ValueError("Invalid JSON response from Groq API") from e
        
        try:
            content = data["choices"][0]["message"]["content"]
            if not content:
                logger.error("Missing content in Groq API response")
                raise ValueError("Empty content in Groq API response")
            return content.strip()
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error processing Groq response: {str(e)}")
            raise ValueError("Invalid response structure from Groq API") from e
    
    async def chat_completion(self, prompt: str, timeout: int = 30) -> str:
        try:
            response = requests.post(
                self.settings.GROQ_BASE_URL,
                headers=self._create_headers(),
                json=self._create_payload(prompt),
                timeout=timeout
            )
            
            answer = self._handle_response(response)
            
            try:
                data = response.json()
                if "usage" in data and "total_tokens" in data["usage"]:
                    total_tokens = data["usage"]["total_tokens"]
                    self.token_counter.add_tokens(total_tokens)
            except Exception as e:
                logger.warning(f"Could not track token usage: {e}")
            
            return answer
            
        except requests.exceptions.Timeout:
            logger.error("Request timeout to Groq API")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error to Groq API: {e}")
            raise