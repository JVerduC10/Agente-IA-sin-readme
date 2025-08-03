import logging
import asyncio
from typing import Any, Dict, List
import httpx
from servidor.settings import Settings
from servidor.usage import DailyTokenCounter
from servidor.utils.search import buscar_web, WebSearchError
from servidor.utils.scrape import extraer_contenido_multiple, WebScrapingError

logger = logging.getLogger(__name__)

class BingClient:
    """Cliente que usa Bing Search + web scraping para generar respuestas competitivas"""
    
    def __init__(self, settings: Settings, token_counter: DailyTokenCounter):
        self.settings = settings
        self.token_counter = token_counter
        
    async def chat_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Genera una respuesta usando búsqueda web de Bing y análisis de contenido"""
        try:
            # Extraer términos de búsqueda del prompt
            search_query = self._extract_search_terms(prompt)
            
            # Realizar búsqueda web
            search_results = await buscar_web(
                search_query, 
                self.settings, 
                top=self.settings.MAX_SEARCH_RESULTS
            )
            
            if not search_results:
                return "Lo siento, no pude encontrar información relevante para tu consulta."
            
            # Extraer contenido de las páginas
            urls = [result['url'] for result in search_results[:3]]  # Limitar a 3 URLs
            
            try:
                contenidos = await extraer_contenido_multiple(
                    urls, 
                    self.settings
                )
            except WebScrapingError as e:
                logger.warning(f"Error en scraping: {e}")
                contenidos = []
            
            # Generar respuesta basada en el contenido encontrado
            response = await self._generate_response(
                prompt, 
                search_results, 
                contenidos, 
                temperature
            )
            
            # Estimar tokens para el contador
            estimated_tokens = len(prompt.split()) + len(response.split())
            self.token_counter.add_tokens(estimated_tokens)
            
            return response
            
        except WebSearchError as e:
            logger.error(f"Error en búsqueda web: {e}")
            return f"Error al buscar información: {str(e)}"
        except Exception as e:
            logger.error(f"Error en Bing client: {e}")
            raise
    
    def _extract_search_terms(self, prompt: str) -> str:
        """Extrae términos de búsqueda relevantes del prompt"""
        # Limpiar el prompt para búsqueda
        import re
        
        # Remover signos de puntuación y normalizar
        query = re.sub(r'[¿?¡!.,;:]', ' ', prompt)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remover palabras comunes
        stop_words = [
            "qué", "cuál", "cómo", "dónde", "cuándo", "por", "quién", 
            "es", "la", "el", "de", "en", "un", "una", "y", "o", "pero",
            "me", "puedes", "ayudar", "explicar", "decir", "contar"
        ]
        
        words = query.split()
        filtered_words = [
            word for word in words 
            if word.lower() not in stop_words and len(word) > 2
        ]
        
        search_query = " ".join(filtered_words) if filtered_words else prompt
        
        logger.info(f"Términos de búsqueda extraídos: '{prompt}' -> '{search_query}'")
        return search_query
    
    async def _generate_response(
        self, 
        prompt: str, 
        search_results: List[Dict], 
        contenidos: List[str], 
        temperature: float
    ) -> str:
        """Genera una respuesta basada en los resultados de búsqueda y contenido"""
        
        # Combinar información de búsqueda y contenido
        context_parts = []
        
        # Agregar snippets de búsqueda
        for i, result in enumerate(search_results[:3]):
            context_parts.append(
                f"Fuente {i+1}: {result['titulo']}\n"
                f"Resumen: {result['snippet']}\n"
                f"URL: {result['url']}\n"
            )
        
        # Agregar contenido extraído si está disponible
        for i, contenido in enumerate(contenidos[:3]):
            if contenido and len(contenido.strip()) > 50:
                context_parts.append(
                    f"Contenido detallado {i+1}:\n{contenido[:800]}...\n"
                )
        
        if not context_parts:
            return "No pude obtener suficiente información para responder tu consulta."
        
        # Generar respuesta estructurada
        response = self._synthesize_answer(prompt, context_parts, temperature)
        
        return response
    
    def _synthesize_answer(
        self, 
        prompt: str, 
        context_parts: List[str], 
        temperature: float
    ) -> str:
        """Sintetiza una respuesta basada en el contexto disponible"""
        
        # Análisis simple del tipo de pregunta
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["qué es", "define", "definición"]):
            return self._generate_definition_response(context_parts)
        elif any(word in prompt_lower for word in ["cómo", "pasos", "proceso"]):
            return self._generate_how_to_response(context_parts)
        elif any(word in prompt_lower for word in ["cuándo", "fecha", "tiempo"]):
            return self._generate_temporal_response(context_parts)
        elif any(word in prompt_lower for word in ["dónde", "lugar", "ubicación"]):
            return self._generate_location_response(context_parts)
        else:
            return self._generate_general_response(prompt, context_parts)
    
    def _generate_definition_response(self, context_parts: List[str]) -> str:
        """Genera una respuesta de definición"""
        response = "Basándome en la información encontrada:\n\n"
        
        # Extraer definiciones de los snippets
        for part in context_parts:
            if "Resumen:" in part:
                lines = part.split('\n')
                for line in lines:
                    if line.startswith("Resumen:"):
                        definition = line.replace("Resumen:", "").strip()
                        if definition:
                            response += f"• {definition}\n"
        
        response += "\n📚 Fuentes consultadas:\n"
        for i, part in enumerate(context_parts):
            if "URL:" in part:
                lines = part.split('\n')
                for line in lines:
                    if line.startswith("URL:"):
                        url = line.replace("URL:", "").strip()
                        response += f"[{i+1}] {url}\n"
        
        return response
    
    def _generate_how_to_response(self, context_parts: List[str]) -> str:
        """Genera una respuesta de procedimiento"""
        response = "Según la información encontrada, aquí tienes los pasos:\n\n"
        
        step_counter = 1
        for part in context_parts:
            if "Contenido detallado" in part:
                content = part.split(":\n", 1)[1] if ":\n" in part else part
                # Buscar pasos numerados o con viñetas
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                        response += f"{step_counter}. {line}\n"
                        step_counter += 1
        
        if step_counter == 1:
            # Si no se encontraron pasos, usar los snippets
            for part in context_parts:
                if "Resumen:" in part:
                    lines = part.split('\n')
                    for line in lines:
                        if line.startswith("Resumen:"):
                            info = line.replace("Resumen:", "").strip()
                            if info:
                                response += f"{step_counter}. {info}\n"
                                step_counter += 1
        
        return response
    
    def _generate_temporal_response(self, context_parts: List[str]) -> str:
        """Genera una respuesta temporal"""
        response = "Información temporal encontrada:\n\n"
        
        for part in context_parts:
            if "Resumen:" in part or "Contenido detallado" in part:
                content = part.split(":\n", 1)[1] if ":\n" in part else part
                # Buscar fechas y referencias temporales
                import re
                dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b|\b(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b', content, re.IGNORECASE)
                if dates:
                    response += f"📅 Fechas relevantes: {', '.join(dates)}\n"
                
                # Agregar contexto
                lines = content.split('\n')
                for line in lines[:3]:  # Primeras 3 líneas
                    if line.strip():
                        response += f"• {line.strip()}\n"
        
        return response
    
    def _generate_location_response(self, context_parts: List[str]) -> str:
        """Genera una respuesta de ubicación"""
        response = "Información de ubicación encontrada:\n\n"
        
        for part in context_parts:
            if "Resumen:" in part:
                lines = part.split('\n')
                for line in lines:
                    if line.startswith("Resumen:"):
                        location_info = line.replace("Resumen:", "").strip()
                        if location_info:
                            response += f"📍 {location_info}\n"
        
        return response
    
    def _generate_general_response(self, prompt: str, context_parts: List[str]) -> str:
        """Genera una respuesta general"""
        response = f"Respuesta a tu consulta sobre: {prompt}\n\n"
        
        # Combinar información relevante
        key_info = []
        for part in context_parts:
            if "Resumen:" in part:
                lines = part.split('\n')
                for line in lines:
                    if line.startswith("Resumen:"):
                        info = line.replace("Resumen:", "").strip()
                        if info and info not in key_info:
                            key_info.append(info)
        
        for i, info in enumerate(key_info[:5]):  # Máximo 5 puntos
            response += f"• {info}\n"
        
        # Agregar fuentes
        response += "\n🔗 Fuentes consultadas:\n"
        source_count = 1
        for part in context_parts:
            if "URL:" in part:
                lines = part.split('\n')
                for line in lines:
                    if line.startswith("URL:"):
                        url = line.replace("URL:", "").strip()
                        response += f"[{source_count}] {url}\n"
                        source_count += 1
                        if source_count > 3:  # Máximo 3 fuentes
                            break
                if source_count > 3:
                    break
        
        return response