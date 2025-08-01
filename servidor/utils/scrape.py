import logging
import re
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from app.settings import Settings

logger = logging.getLogger(__name__)


class WebScrapingError(Exception):
    """Excepción personalizada para errores de web scraping"""
    pass


async def leer_pagina(url: str, settings: Settings, max_len: Optional[int] = None) -> str:
    """
    Extrae texto limpio de una URL.
    
    Args:
        url: URL de la página a leer
        settings: Configuración de la aplicación
        max_len: Longitud máxima del texto (por defecto usa MAX_PAGE_LENGTH)
    
    Returns:
        Texto limpio extraído de la página
    
    Raises:
        WebScrapingError: Si hay un error al leer la página
    """
    if max_len is None:
        max_len = settings.MAX_PAGE_LENGTH
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        async with httpx.AsyncClient(
            timeout=settings.WEB_SCRAPE_TIMEOUT,
            follow_redirects=True,
            headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
        # Verificar que el contenido sea HTML
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            logger.warning(f"Contenido no HTML detectado en {url}: {content_type}")
            return f"[Contenido no HTML: {content_type}]"
        
        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        
        # Remover scripts, estilos y otros elementos no deseados
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
            tag.decompose()
        
        # Remover comentarios
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith("<!--")):
            comment.extract()
        
        # Extraer texto del body o del documento completo
        body = soup.find("body")
        if body:
            text_content = body.get_text(separator=" ", strip=True)
        else:
            text_content = soup.get_text(separator=" ", strip=True)
        
        # Limpiar espacios en blanco excesivos
        text_content = re.sub(r"\s+", " ", text_content)
        
        # Truncar si es necesario
        if len(text_content) > max_len:
            text_content = text_content[:max_len] + "..."
        
        logger.info(f"Página leída exitosamente: {url} ({len(text_content)} caracteres)")
        return text_content
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP al leer página {url}: {e.response.status_code}")
        raise WebScrapingError(f"Error HTTP {e.response.status_code} al acceder a {url}")
    except httpx.TimeoutException:
        logger.error(f"Timeout al leer página: {url}")
        raise WebScrapingError(f"Timeout al acceder a {url}")
    except Exception as e:
        logger.error(f"Error inesperado al leer página {url}: {str(e)}")
        raise WebScrapingError(f"Error al leer {url}: {str(e)}")


def limpiar_texto(texto: str) -> str:
    """
    Limpia y normaliza texto extraído de páginas web.
    
    Args:
        texto: Texto a limpiar
    
    Returns:
        Texto limpio y normalizado
    """
    # Remover caracteres de control y espacios excesivos
    texto = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    
    # Remover líneas muy cortas que probablemente sean ruido
    lineas = texto.split(".")
    lineas_filtradas = [linea.strip() for linea in lineas if len(linea.strip()) > 10]
    
    return ". ".join(lineas_filtradas)


async def extraer_contenido_multiple(urls: list[str], settings: Settings) -> list[str]:
    """
    Extrae contenido de múltiples URLs de forma concurrente.
    
    Args:
        urls: Lista de URLs a procesar
        settings: Configuración de la aplicación
    
    Returns:
        Lista de textos extraídos (en el mismo orden que las URLs)
    """
    import asyncio
    
    async def extraer_con_manejo_errores(url: str) -> str:
        try:
            return await leer_pagina(url, settings)
        except WebScrapingError as e:
            logger.warning(f"Error al extraer contenido de {url}: {e}")
            return f"[Error al leer {url}: {e}]"
    
    # Procesar URLs concurrentemente
    tareas = [extraer_con_manejo_errores(url) for url in urls]
    resultados = await asyncio.gather(*tareas, return_exceptions=True)
    
    # Convertir excepciones a strings de error
    textos = []
    for i, resultado in enumerate(resultados):
        if isinstance(resultado, Exception):
            textos.append(f"[Error al procesar {urls[i]}: {resultado}]")
        else:
            textos.append(resultado)
    
    return textos