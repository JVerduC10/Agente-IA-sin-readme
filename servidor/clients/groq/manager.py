"""Gestor de modelos y proveedores de IA."""

import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .client import GroqClient
from servidor.config.settings import get_settings

# Eliminado enum Provider - Sistema monocliente Groq


class ModelManager:
    """Gestor centralizado para modelos de IA y proveedores."""

    def __init__(self):
        """Inicializa el gestor de modelos con Groq únicamente."""
        self._groq_client = None
        self._initialize_groq()

    def _initialize_groq(self):
        """Inicializa el cliente Groq."""
        try:
            settings = get_settings()
            groq_api_key = settings.GROQ_API_KEY
            if groq_api_key:
                self._groq_client = GroqClient(api_key=groq_api_key)
            else:
                raise ValueError("GROQ_API_KEY no configurada")
        except Exception as e:
            print(f"Error inicializando Groq: {e}")

    def get_available_providers(self) -> List[str]:
        """Obtiene la lista de proveedores disponibles.

        Returns:
            Lista con solo Groq
        """
        return ["groq"] if self._groq_client else []

    def get_available_models(
        self, provider: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Obtiene los modelos disponibles de Groq.

        Args:
            provider: Ignorado - solo Groq disponible

        Returns:
            Diccionario con modelos de Groq
        """
        if self._groq_client:
            return {"groq": self._groq_client.get_available_models()}
        return {}

    def get_client(self, provider: Optional[str] = None):
        """Obtiene el cliente Groq.

        Args:
            provider: Ignorado - solo Groq disponible

        Returns:
            Cliente Groq
        """
        if not self._groq_client:
            raise ValueError("Cliente Groq no disponible")
        return self._groq_client

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Realiza una completación de chat con Groq.

        Args:
            messages: Lista de mensajes en formato OpenAI
            provider: Ignorado - solo Groq disponible
            model: Modelo específico a usar
            temperature: Temperatura para la generación
            max_tokens: Máximo número de tokens
            stream: Si usar streaming
            **kwargs: Argumentos adicionales

        Returns:
            Respuesta de la API
        """
        if not self._groq_client:
            raise ValueError("Cliente Groq no disponible")

        # Si se especifica un modelo, actualizar el cliente
        if model and hasattr(self._groq_client, "model"):
            original_model = self._groq_client.model
            self._groq_client.model = model
            try:
                result = await self._groq_client.chat_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs,
                )
                return result
            finally:
                self._groq_client.model = original_model
        else:
            return await self._groq_client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs,
            )

    async def _execute_with_provider(
        self, provider: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        """Ejecuta una completación con Groq.

        Args:
            provider: Ignorado - solo Groq disponible
            messages: Mensajes para la completación
            **kwargs: Argumentos adicionales

        Returns:
            Respuesta de la API
        """
        if not self._groq_client:
            raise ValueError("Cliente Groq no disponible")
        return await self._groq_client.chat_completion(messages=messages, **kwargs)

    def validate_providers(self) -> Dict[str, bool]:
        """Valida la conexión con Groq.

        Returns:
            Diccionario con el estado de Groq
        """
        status = {}
        try:
            status["groq"] = (
                self._groq_client.validate_connection() if self._groq_client else False
            )
        except Exception:
            status["groq"] = False

        return status

    def set_default_provider(self, provider: str):
        """Establece el proveedor por defecto (solo Groq disponible).

        Args:
            provider: Nombre del proveedor
        """
        if provider != "groq":
            raise ValueError(f"Solo Groq está disponible, no {provider}")

        if not self._groq_client:
            raise ValueError("Cliente Groq no disponible")

    def get_provider_info(self) -> Dict[str, Any]:
        """Obtiene información detallada de Groq.

        Returns:
            Información de proveedor y modelos
        """
        info = {
            "default_provider": "groq",
            "available_providers": self.get_available_providers(),
            "provider_status": self.validate_providers(),
            "available_models": self.get_available_models(),
        }

        return info
