import logging
from typing import List, Dict, Any, Optional
import json

from servidor.config.settings import get_settings
from servidor.core.error_handler import RAGError, handle_errors
# from .utils.azure_search import azure_chat_completion  # ELIMINADO - Azure integration removed
from servidor.services.model_selector import select_model_from_message

logger = logging.getLogger(__name__)
settings = get_settings()

class RAGSystem:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedder = None
        self._initialized = False
        self.config = settings.rag
    
    @handle_errors("rag_initialization")
    def _lazy_init(self):
        """Inicialización lazy para evitar problemas de importación"""
        if self._initialized:
            return
        
        if not self.config.validate_configuration():
            raise RAGError("Configuración RAG inválida", "initialization")
            
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            from sentence_transformers import SentenceTransformer
            
            # Inicializar ChromaDB
            if self.config.is_client_mode:
                self.chroma_client = chromadb.HttpClient(
                    host=self.config.chroma_host,
                    port=self.config.chroma_port,
                    settings=ChromaSettings(**self.config.chroma_settings)
                )
            else:
                self.chroma_client = chromadb.PersistentClient(
                    path=self.config.chroma_persist_dir,
                    settings=ChromaSettings(**self.config.chroma_settings)
                )
            
            # Obtener o crear colección
            try:
                self.collection = self.chroma_client.get_collection(self.config.collection_name)
                logger.info(f"Colección RAG '{self.config.collection_name}' cargada exitosamente")
            except Exception:
                # Si no existe, crear colección vacía
                self.collection = self.chroma_client.create_collection(
                    name=self.config.collection_name,
                    metadata=self.config.get_collection_metadata(),
                    embedding_function=None  # Usaremos nuestros propios embeddings
                )
                logger.info(f"Colección RAG '{self.config.collection_name}' creada exitosamente")
            
            # Inicializar modelo de embeddings
            self.embedder = SentenceTransformer(self.config.embedding_model)
            self._initialized = True
            logger.info(f"Sistema RAG inicializado con modelo {self.config.embedding_model}")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise RAGError(f"Error al inicializar sistema RAG: {str(e)}", "initialization")
    
    @handle_errors("rag_query_routing")
    def rag_router(self, query: str) -> Optional[Dict[str, Any]]:
        """Decide si usar RAG o búsqueda web basado en similitud"""
        try:
            self._lazy_init()
            
            # Verificar si hay documentos en la colección
            if self.collection.count() == 0:
                logger.info("No hay documentos en la colección RAG")
                return None
            
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode([query]).tolist()[0]
            
            # Buscar documentos similares
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=self.config.max_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                logger.info("No se encontraron documentos")
                return None
            
            # Convertir distancias a scores de similitud (cosine)
            # ChromaDB devuelve distancias, convertimos a similitud: 1 - distance
            similarities = [1 - dist for dist in results['distances'][0]]
            
            # Filtrar hits que superen el umbral
            hits = []
            for i, (doc, metadata, similarity) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0], 
                similarities
            )):
                if similarity >= self.config.score_threshold:
                    hits.append({
                        'document': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'index': i + 1
                    })
            
            logger.info(f"Query: '{query}' - Hits encontrados: {len(hits)}/{len(results['documents'][0])}")
            
            # Verificar si tenemos suficientes hits
            if len(hits) >= self.config.min_hits:
                return self.rag_search(query, hits)
            else:
                logger.info(f"Insuficientes hits ({len(hits)} < {settings.RAG_MIN_HITS}), usando búsqueda web")
                return None
                
        except Exception as e:
            logger.error(f"Error en rag_router: {e}")
            return None
    
    @handle_errors("rag_search")
    def rag_search(self, query: str, hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realizar búsqueda RAG con documentos relevantes"""
        try:
            # Construir contexto con los documentos más relevantes
            context_parts = []
            for hit in hits:
                doc_text = hit['document']
                similarity = hit['similarity']
                metadata = hit.get('metadata', {})
                
                # Agregar información del documento al contexto
                context_part = f"[Documento {hit['index']} - Similitud: {similarity:.3f}]"
                if metadata.get('source'):
                    context_part += f" Fuente: {metadata['source']}"
                context_part += f"\n{doc_text}\n"
                context_parts.append(context_part)
            
            context = "\n".join(context_parts)
            
            # Truncar contexto si es muy largo
            max_context_length = self.config.max_context_length
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            
            logger.info(f"Contexto RAG generado: {len(context)} caracteres")
            
            return {
                'type': 'rag',
                'context': context,
                'hits': hits,
                'total_hits': len(hits)
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda RAG: {str(e)}")
            raise RAGError(f"Error en búsqueda RAG: {str(e)}", "search")
    
    @handle_errors("rag_document_search")
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Buscar documentos similares en la base de datos vectorial"""
        try:
            self._lazy_init()
            
            if self.collection.count() == 0:
                return {
                    'documents': [],
                    'similarities': [],
                    'metadatas': [],
                    'total_documents': 0
                }
            
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode([query]).tolist()[0]
            
            # Buscar documentos similares
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )
            
            # Convertir distancias a scores de similitud
            similarities = [1 - dist for dist in results['distances'][0]] if results['distances'] else []
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'similarities': similarities,
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'total_documents': len(results['documents'][0]) if results['documents'] else 0
            }
            
        except Exception as e:
            logger.error(f"Error en search_documents: {str(e)}")
            raise RAGError(f"Error en búsqueda de documentos: {str(e)}", "document_search")
    
    @handle_errors("rag_collection_info")
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtener información sobre la colección"""
        try:
            self._lazy_init()
            
            count = self.collection.count()
            
            # Obtener una muestra de documentos para análisis
            sample_size = min(10, count) if count > 0 else 0
            sample_docs = []
            
            if sample_size > 0:
                results = self.collection.get(
                    limit=sample_size,
                    include=["documents", "metadatas"]
                )
                
                for i, (doc, metadata) in enumerate(zip(
                    results.get('documents', []),
                    results.get('metadatas', [])
                )):
                    sample_docs.append({
                        'index': i + 1,
                        'preview': doc[:200] + "..." if len(doc) > 200 else doc,
                        'length': len(doc),
                        'metadata': metadata
                    })
            
            return {
                'collection_name': self.config.collection_name,
                'total_documents': count,
                'sample_documents': sample_docs,
                'embedding_model': self.config.embedding_model,
                'chunk_size': self.config.chunk_size
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo información de colección: {str(e)}")
            raise RAGError(f"Error obteniendo información de colección: {str(e)}", "collection_info")

# Instancia global
rag_system = RAGSystem()