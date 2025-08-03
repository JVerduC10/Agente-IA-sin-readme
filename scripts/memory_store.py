#!/usr/bin/env python3
"""
Sistema de memoria vectorial para DeepSearch.
Permite almacenar y recuperar consultas y respuestas previas usando embeddings.
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass, asdict

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Entrada de memoria que almacena consulta, respuesta y metadatos."""
    query: str
    response: str
    query_type: str
    timestamp: str
    sources: List[str]
    confidence: float
    embedding_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        return cls(**data)

class MemoryStoreError(Exception):
    """Excepción para errores del sistema de memoria."""
    pass

class VectorMemoryStore:
    """Sistema de memoria vectorial para almacenar y recuperar consultas similares."""
    
    def __init__(self, 
                 collection_name: str = "deepsearch_memory",
                 persist_directory: str = "./memoria_vectorial",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 max_entries: int = 1000,
                 similarity_threshold: float = 0.7):
        """
        Inicializa el sistema de memoria vectorial.
        
        Args:
            collection_name: Nombre de la colección en ChromaDB
            persist_directory: Directorio para persistir la base de datos
            embedding_model: Modelo para generar embeddings
            max_entries: Máximo número de entradas a mantener
            similarity_threshold: Umbral de similitud para considerar una consulta similar
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        
        # Verificar dependencias
        if chromadb is None:
            raise MemoryStoreError("ChromaDB no está instalado. Instalar con: pip install chromadb")
        
        if SentenceTransformer is None:
            raise MemoryStoreError("SentenceTransformers no está instalado. Instalar con: pip install sentence-transformers")
        
        # Inicializar componentes
        self._init_chroma_client()
        self._init_embedding_model()
        self._init_collection()
        
        logger.info(f"VectorMemoryStore inicializado: {collection_name}")
    
    def _init_chroma_client(self):
        """Inicializa el cliente de ChromaDB."""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Cliente ChromaDB inicializado en: {self.persist_directory}")
            
        except Exception as e:
            raise MemoryStoreError(f"Error inicializando ChromaDB: {e}")
    
    def _init_embedding_model(self):
        """Inicializa el modelo de embeddings."""
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Modelo de embeddings cargado: {self.embedding_model_name}")
            
        except Exception as e:
            raise MemoryStoreError(f"Error cargando modelo de embeddings: {e}")
    
    def _init_collection(self):
        """Inicializa o obtiene la colección de ChromaDB."""
        try:
            # Intentar obtener colección existente
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Colección existente cargada: {self.collection_name}")
                
            except Exception:
                # Crear nueva colección
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "DeepSearch memory store"}
                )
                logger.info(f"Nueva colección creada: {self.collection_name}")
                
        except Exception as e:
            raise MemoryStoreError(f"Error inicializando colección: {e}")
    
    def _generate_embedding_id(self, query: str, query_type: str) -> str:
        """Genera un ID único para la entrada basado en la consulta."""
        content = f"{query}_{query_type}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def store_memory(self, 
                    query: str, 
                    response: str, 
                    query_type: str,
                    sources: List[str] = None,
                    confidence: float = 1.0) -> str:
        """
        Almacena una nueva entrada en la memoria.
        
        Args:
            query: Consulta original
            response: Respuesta generada
            query_type: Tipo de consulta (web, rag, etc.)
            sources: URLs o fuentes utilizadas
            confidence: Nivel de confianza en la respuesta
            
        Returns:
            ID de la entrada almacenada
        """
        try:
            # Generar embedding para la consulta
            embedding = self.embedding_model.encode(query).tolist()
            
            # Crear entrada de memoria
            embedding_id = self._generate_embedding_id(query, query_type)
            
            memory_entry = MemoryEntry(
                query=query,
                response=response,
                query_type=query_type,
                timestamp=datetime.now().isoformat(),
                sources=sources or [],
                confidence=confidence,
                embedding_id=embedding_id
            )
            
            # Almacenar en ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[query],
                metadatas=[memory_entry.to_dict()],
                ids=[embedding_id]
            )
            
            # Limpiar entradas antiguas si excedemos el límite
            self._cleanup_old_entries()
            
            logger.info(f"Memoria almacenada: {embedding_id[:8]}... para consulta: {query[:50]}...")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Error almacenando memoria: {e}")
            raise MemoryStoreError(f"Error almacenando memoria: {e}")
    
    def search_similar_queries(self, 
                              query: str, 
                              query_type: str = None,
                              max_results: int = 3,
                              time_window_hours: int = 24) -> List[Tuple[MemoryEntry, float]]:
        """
        Busca consultas similares en la memoria.
        
        Args:
            query: Consulta a buscar
            query_type: Filtrar por tipo de consulta
            max_results: Máximo número de resultados
            time_window_hours: Ventana de tiempo en horas para considerar entradas
            
        Returns:
            Lista de tuplas (MemoryEntry, similarity_score)
        """
        try:
            # Generar embedding para la consulta
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Calcular tiempo límite
            time_limit = datetime.now() - timedelta(hours=time_window_hours)
            
            # Buscar en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results * 2,  # Obtener más para filtrar
                include=["metadatas", "distances"]
            )
            
            similar_entries = []
            
            if results['metadatas'] and results['metadatas'][0]:
                for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                    # Convertir distancia a similitud (ChromaDB usa distancia coseno)
                    similarity = 1 - distance
                    
                    # Filtrar por umbral de similitud
                    if similarity < self.similarity_threshold:
                        continue
                    
                    # Crear entrada de memoria
                    memory_entry = MemoryEntry.from_dict(metadata)
                    
                    # Filtrar por tipo de consulta si se especifica
                    if query_type and memory_entry.query_type != query_type:
                        continue
                    
                    # Filtrar por ventana de tiempo
                    entry_time = datetime.fromisoformat(memory_entry.timestamp)
                    if entry_time < time_limit:
                        continue
                    
                    similar_entries.append((memory_entry, similarity))
            
            # Ordenar por similitud y limitar resultados
            similar_entries.sort(key=lambda x: x[1], reverse=True)
            similar_entries = similar_entries[:max_results]
            
            logger.info(f"Encontradas {len(similar_entries)} consultas similares para: {query[:50]}...")
            return similar_entries
            
        except Exception as e:
            logger.error(f"Error buscando consultas similares: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la memoria."""
        try:
            count = self.collection.count()
            
            # Obtener algunas entradas recientes para análisis
            recent_results = self.collection.get(
                limit=10,
                include=["metadatas"]
            )
            
            query_types = {}
            if recent_results['metadatas']:
                for metadata in recent_results['metadatas']:
                    query_type = metadata.get('query_type', 'unknown')
                    query_types[query_type] = query_types.get(query_type, 0) + 1
            
            return {
                "total_entries": count,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model_name,
                "similarity_threshold": self.similarity_threshold,
                "query_types_sample": query_types,
                "max_entries": self.max_entries
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def _cleanup_old_entries(self):
        """Limpia entradas antiguas si excedemos el límite máximo."""
        try:
            count = self.collection.count()
            
            if count > self.max_entries:
                # Obtener todas las entradas con metadatos
                all_results = self.collection.get(
                    include=["metadatas"]
                )
                
                if all_results['ids'] and all_results['metadatas']:
                    # Crear lista de entradas con timestamps
                    entries_with_time = []
                    for entry_id, metadata in zip(all_results['ids'], all_results['metadatas']):
                        timestamp = metadata.get('timestamp')
                        if timestamp:
                            entries_with_time.append((entry_id, timestamp))
                    
                    # Ordenar por timestamp (más antiguas primero)
                    entries_with_time.sort(key=lambda x: x[1])
                    
                    # Eliminar las más antiguas
                    entries_to_delete = count - self.max_entries + 10  # Eliminar un poco más para evitar limpiezas frecuentes
                    ids_to_delete = [entry[0] for entry in entries_with_time[:entries_to_delete]]
                    
                    if ids_to_delete:
                        self.collection.delete(ids=ids_to_delete)
                        logger.info(f"Eliminadas {len(ids_to_delete)} entradas antiguas de la memoria")
                        
        except Exception as e:
            logger.error(f"Error limpiando entradas antiguas: {e}")
    
    def clear_memory(self):
        """Limpia toda la memoria."""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self._init_collection()
            logger.info("Memoria completamente limpiada")
            
        except Exception as e:
            logger.error(f"Error limpiando memoria: {e}")
            raise MemoryStoreError(f"Error limpiando memoria: {e}")

def create_memory_store(settings=None) -> Optional[VectorMemoryStore]:
    """
    Factory function para crear un VectorMemoryStore.
    
    Args:
        settings: Objeto de configuración con parámetros opcionales
        
    Returns:
        VectorMemoryStore instance o None si hay errores
    """
    try:
        # Configuración por defecto
        config = {
            "collection_name": "deepsearch_memory",
            "persist_directory": "./memoria_vectorial",
            "embedding_model": "all-MiniLM-L6-v2",
            "max_entries": 1000,
            "similarity_threshold": 0.7
        }
        
        # Sobrescribir con configuración del settings si existe
        if settings:
            if hasattr(settings, 'MEMORY_COLLECTION_NAME'):
                config["collection_name"] = settings.MEMORY_COLLECTION_NAME
            if hasattr(settings, 'MEMORY_PERSIST_DIR'):
                config["persist_directory"] = settings.MEMORY_PERSIST_DIR
            if hasattr(settings, 'MEMORY_EMBEDDING_MODEL'):
                config["embedding_model"] = settings.MEMORY_EMBEDDING_MODEL
            if hasattr(settings, 'MEMORY_MAX_ENTRIES'):
                config["max_entries"] = settings.MEMORY_MAX_ENTRIES
            if hasattr(settings, 'MEMORY_SIMILARITY_THRESHOLD'):
                config["similarity_threshold"] = settings.MEMORY_SIMILARITY_THRESHOLD
        
        return VectorMemoryStore(**config)
        
    except Exception as e:
        logger.error(f"Error creando memory store: {e}")
        return None

if __name__ == "__main__":
    # Ejemplo de uso
    try:
        memory = VectorMemoryStore()
        
        # Almacenar una consulta
        memory_id = memory.store_memory(
            query="¿Qué es la inteligencia artificial?",
            response="La inteligencia artificial es una rama de la informática...",
            query_type="web",
            sources=["https://example.com"],
            confidence=0.9
        )
        
        print(f"Memoria almacenada: {memory_id}")
        
        # Buscar consultas similares
        similar = memory.search_similar_queries("¿Cómo funciona la IA?")
        print(f"Consultas similares encontradas: {len(similar)}")
        
        # Estadísticas
        stats = memory.get_memory_stats()
        print(f"Estadísticas: {stats}")
        
    except Exception as e:
        print(f"Error en ejemplo: {e}")