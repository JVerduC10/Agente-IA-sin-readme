import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from servidor.config.settings import get_settings
from servidor.core.error_handler import ExternalServiceError, handle_errors
from servidor.core.http_client import get_http_client

settings = get_settings()
logger = logging.getLogger(__name__)

MAX_PAGE_LENGTH = settings.app.max_page_length


class WebScrapingError(ExternalServiceError):
    """Excepción personalizada para errores de web scraping"""

    def __init__(self, message: str, service: str = "web_scraping"):
        super().__init__(message, service)


@handle_errors("web_scraping")
async def leer_pagina(url: str, max_len: Optional[int] = None) -> str:
    """
    Extrae texto limpio de una URL.

    Args:
        url: URL de la página a leer
        max_len: Longitud máxima del texto (por defecto usa MAX_PAGE_LENGTH)

    Returns:
        Texto limpio extraído de la página

    Raises:
        WebScrapingError: Si hay un error al leer la página
    """
    if max_len is None:
        max_len = MAX_PAGE_LENGTH

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        # Usar el cliente HTTP unificado
        http_client = get_http_client()
        response = await http_client.get(
            url, headers=headers, timeout=settings.app.web_scrape_timeout
        )

        # Verificar que el contenido sea HTML
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            logger.warning(f"Contenido no HTML detectado en {url}: {content_type}")
            return f"[Contenido no HTML: {content_type}]"

        # Parsear HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Remover scripts, estilos y otros elementos no deseados
        for tag in soup(
            ["script", "style", "nav", "header", "footer", "aside", "noscript"]
        ):
            tag.decompose()

        # Remover comentarios
        for comment in soup.find_all(
            string=lambda text: isinstance(text, str)
            and text.strip().startswith("<!--")
        ):
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

        logger.info(
            f"Página leída exitosamente: {url} ({len(text_content)} caracteres)"
        )
        return text_content

    except Exception as e:
        logger.error(f"Error al leer página {url}: {str(e)}")
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


@handle_errors("web_scraping_multiple")
async def extraer_contenido_multiple(urls: list[str]) -> list[str]:
    """
    Extrae contenido de múltiples URLs de forma secuencial.

    Args:
        urls: Lista de URLs a procesar

    Returns:
        Lista de textos extraídos (en el mismo orden que las URLs)
    """
    textos = []

    for url in urls:
        try:
            texto = await leer_pagina(url)
            textos.append(texto)
        except WebScrapingError as e:
            logger.warning(f"Error al extraer contenido de {url}: {e}")
            textos.append(f"[Error al leer {url}: {e}]")
        except Exception as e:
            logger.error(f"Error inesperado al procesar {url}: {e}")
            textos.append(f"[Error inesperado al procesar {url}: {e}]")

    return textos
