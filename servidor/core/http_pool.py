"""Cliente HTTP optimizado con pooling de conexiones y retry logic."""

import asyncio
import logging
from typing import Any, Dict, Optional, Union
from contextlib import asynccontextmanager

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class HTTPClientPool:
    """Cliente HTTP singleton con pooling de conexiones optimizado."""
    
    _instance: Optional['HTTPClientPool'] = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._limits = httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100,
            keepalive_expiry=30.0
        )
        self._timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=10.0,
            pool=5.0
        )
    
    @classmethod
    async def get_instance(cls) -> 'HTTPClientPool':
        """Obtiene la instancia singleton del pool HTTP."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        """Inicializa el cliente HTTP."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                limits=self._limits,
                timeout=self._timeout,
                follow_redirects=True,
                verify=True
            )
            logger.info("Cliente HTTP inicializado con pooling optimizado")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
    )
    async def get(
        self, 
        url: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición GET con retry automático."""
        if not self._client:
            await self._initialize()
        
        try:
            response = await self._client.get(
                url, 
                params=params, 
                headers=headers, 
                **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} for GET {url}")
            raise
        except Exception as e:
            logger.error(f"Error en GET {url}: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
    )
    async def post(
        self, 
        url: str, 
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición POST con retry automático."""
        if not self._client:
            await self._initialize()
        
        try:
            response = await self._client.post(
                url, 
                data=data, 
                json=json, 
                headers=headers, 
                **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} for POST {url}")
            raise
        except Exception as e:
            logger.error(f"Error en POST {url}: {e}")
            raise
    
    async def put(
        self, 
        url: str, 
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición PUT."""
        if not self._client:
            await self._initialize()
        
        try:
            response = await self._client.put(
                url, 
                data=data, 
                json=json, 
                headers=headers, 
                **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Error en PUT {url}: {e}")
            raise
    
    async def delete(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Realiza una petición DELETE."""
        if not self._client:
            await self._initialize()
        
        try:
            response = await self._client.delete(
                url, 
                headers=headers, 
                **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Error en DELETE {url}: {e}")
            raise
    
    @asynccontextmanager
    async def stream(self, method: str, url: str, **kwargs):
        """Context manager para streaming de respuestas."""
        if not self._client:
            await self._initialize()
        
        async with self._client.stream(method, url, **kwargs) as response:
            yield response
    
    async def close(self):
        """Cierra el cliente HTTP."""
        if self._client:
            await self._client.aclose()
            self._client = None
            # Evitar logging durante cleanup para prevenir errores
    
    @classmethod
    async def cleanup(cls):
        """Limpia la instancia singleton."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            # Evitar logging durante cleanup para prevenir errores


# Funciones de conveniencia para uso directo
async def http_get(url: str, **kwargs) -> httpx.Response:
    """Función de conveniencia para GET."""
    pool = await HTTPClientPool.get_instance()
    return await pool.get(url, **kwargs)


async def http_post(url: str, **kwargs) -> httpx.Response:
    """Función de conveniencia para POST."""
    pool = await HTTPClientPool.get_instance()
    return await pool.post(url, **kwargs)


async def http_put(url: str, **kwargs) -> httpx.Response:
    """Función de conveniencia para PUT."""
    pool = await HTTPClientPool.get_instance()
    return await pool.put(url, **kwargs)


async def http_delete(url: str, **kwargs) -> httpx.Response:
    """Función de conveniencia para DELETE."""
    pool = await HTTPClientPool.get_instance()
    return await pool.delete(url, **kwargs)


# Cleanup automático al cerrar la aplicación
import atexit

def _cleanup_on_exit():
    """Cleanup automático al salir."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(HTTPClientPool.cleanup())
        else:
            loop.run_until_complete(HTTPClientPool.cleanup())
    except Exception:
        pass  # Ignorar errores durante cleanup

atexit.register(_cleanup_on_exit)