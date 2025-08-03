import logging
import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
import trafilatura

logger = logging.getLogger(__name__)

class ExtractionError(Exception):
    """Excepción personalizada para errores de extracción de contenido"""
    pass

def leer_contenido(url: str, max_len: int = 1500, timeout: int = 10) -> Optional[str]:
    """
    Extrae texto limpio de una URL usando trafilatura como método principal
    y BeautifulSoup como fallback.
    
    Args:
        url: URL de la página a leer
        max_len: Longitud máxima del texto extraído
        timeout: Timeout para la petición HTTP
    
    Returns:
        Texto limpio extraído de la página o None si falla
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Verificar que el contenido sea HTML
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            logger.warning(f"Contenido no HTML detectado en {url}: {content_type}")
            return None
        
        # Intentar primero con trafilatura (más preciso)
        try:
            texto = trafilatura.extract(response.text)
            if texto and len(texto.strip()) > 50:  # Verificar que extrajo contenido útil
                texto_limpio = limpiar_texto(texto)
                if len(texto_limpio) > max_len:
                    texto_limpio = texto_limpio[:max_len] + "..."
                logger.info(f"Contenido extraído con trafilatura: {url} ({len(texto_limpio)} caracteres)")
                return texto_limpio
        except Exception as e:
            logger.warning(f"Trafilatura falló para {url}: {e}")
        
        # Fallback a BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        
        # Remover scripts, estilos y otros elementos no deseados
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
            tag.decompose()
        
        # Extraer texto del body o del documento completo
        body = soup.find("body")
        if body:
            text_content = body.get_text(separator=" ", strip=True)
        else:
            text_content = soup.get_text(separator=" ", strip=True)
        
        # Limpiar y truncar
        texto_limpio = limpiar_texto(text_content)
        if len(texto_limpio) > max_len:
            texto_limpio = texto_limpio[:max_len] + "..."
        
        logger.info(f"Contenido extraído con BeautifulSoup: {url} ({len(texto_limpio)} caracteres)")
        return texto_limpio
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP al leer página {url}: {e.response.status_code}")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al leer página: {url}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al leer página {url}: {str(e)}")
        return None

def limpiar_texto(texto: str) -> str:
    """
    Limpia y normaliza texto extraído de páginas web.
    
    Args:
        texto: Texto a limpiar
    
    Returns:
        Texto limpio y normalizado
    """
    if not texto:
        return ""
    
    # Remover caracteres de control y espacios excesivos
    texto = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    
    # Remover líneas muy cortas que probablemente sean ruido
    lineas = texto.split(".")
    lineas_filtradas = [linea.strip() for linea in lineas if len(linea.strip()) > 10]
    
    return ". ".join(lineas_filtradas).strip()

def extraer_contenido_multiple(urls: list[str], max_len: int = 1500) -> list[str]:
    """
    Extrae contenido de múltiples URLs de forma secuencial.
    
    Args:
        urls: Lista de URLs a procesar
        max_len: Longitud máxima por texto extraído
    
    Returns:
        Lista de textos extraídos (en el mismo orden que las URLs)
    """
    resultados = []
    
    for url in urls:
        try:
            contenido = leer_contenido(url, max_len)
            if contenido:
                resultados.append(contenido)
            else:
                resultados.append(f"[Error al leer {url}]")
        except Exception as e:
            logger.warning(f"Error al extraer contenido de {url}: {e}")
            resultados.append(f"[Error al procesar {url}: {e}]")
    
    return resultados