import asyncio
import logging
from typing import Dict, Any, Optional, Union
from contextlib import asynccontextmanager
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class HttpClientError(Exception):
    """Excepción base para errores del cliente HTTP"""
    pass

class HttpTimeoutError(HttpClientError):
    """Error de timeout en peticiones HTTP"""
    pass

class HttpConnectionError(HttpClientError):
    """Error de conexión HTTP"""
    pass

class HttpClientManager:
    """Cliente HTTP unificado con manejo de errores, reintentos y pooling de conexiones"""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: int = 5
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configuración de límites de conexión
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea el cliente HTTP"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=self.limits,
                headers=self._default_headers,
                follow_redirects=True
            )
        return self._client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición HTTP con reintentos automáticos"""
        try:
            client = await self._get_client()
            
            # Combinar headers por defecto con los proporcionados
            request_headers = self._default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = await client.request(
                method=method,
                url=url,
                headers=request_headers,
                **kwargs
            )
            
            response.raise_for_status()
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Timeout en petición {method} {url}: {e}")
            raise HttpTimeoutError(f"Timeout al acceder a {url}")
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión {method} {url}: {e}")
            raise HttpConnectionError(f"Error de conexión a {url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP {method} {url}: {e.response.status_code}")
            raise HttpClientError(f"Error HTTP {e.response.status_code} en {url}")
        except Exception as e:
            logger.error(f"Error inesperado {method} {url}: {e}")
            raise HttpClientError(f"Error inesperado al acceder a {url}: {str(e)}")
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición GET"""
        return await self._make_request("GET", url, headers=headers, params=params, **kwargs)
    
    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición POST"""
        return await self._make_request("POST", url, headers=headers, data=data, json=json, **kwargs)
    
    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición PUT"""
        return await self._make_request("PUT", url, headers=headers, data=data, json=json, **kwargs)
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición DELETE"""
        return await self._make_request("DELETE", url, headers=headers, **kwargs)
    
    async def close(self):
        """Cierra el cliente HTTP"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    @asynccontextmanager
    async def session(self):
        """Context manager para manejo automático de sesiones"""
        try:
            yield self
        finally:
            await self.close()

# Instancia global del cliente HTTP
_http_client: Optional[HttpClientManager] = None

def get_http_client() -> HttpClientManager:
    """Obtiene la instancia global del cliente HTTP"""
    global _http_client
    if _http_client is None:
        _http_client = HttpClientManager()
    return _http_client

async def close_http_client():
    """Cierra la instancia global del cliente HTTP"""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None