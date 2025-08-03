import logging
from typing import List, Dict, Any, Optional
import json
from groq import Groq

from .settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class RAGSystem:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedder = None
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self._initialized = False
    
    def _lazy_init(self):
        """Inicialización lazy para evitar problemas de importación"""
        if self._initialized:
            return
            
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            from sentence_transformers import SentenceTransformer
            
            # Inicializar ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Obtener colección
            try:
                self.collection = self.chroma_client.get_collection(settings.RAG_COLLECTION)
            except:
                # Si no existe, crear colección vacía sin embedding function por defecto
                self.collection = self.chroma_client.create_collection(
                    name=settings.RAG_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                    embedding_function=None  # Usaremos nuestros propios embeddings
                )
            
            # Inicializar modelo de embeddings
            self.embedder = SentenceTransformer(settings.RAG_EMBEDDING_MODEL)
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise
    
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
                n_results=5,
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
                if similarity >= settings.RAG_SCORE_THRESHOLD:
                    hits.append({
                        'document': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'index': i + 1
                    })
            
            logger.info(f"Query: '{query}' - Hits encontrados: {len(hits)}/{len(results['documents'][0])}")
            
            # Verificar si tenemos suficientes hits
            if len(hits) >= settings.RAG_MIN_HITS:
                return self.rag_search(query, hits)
            else:
                logger.info(f"Insuficientes hits ({len(hits)} < {settings.RAG_MIN_HITS}), usando búsqueda web")
                return None
                
        except Exception as e:
            logger.error(f"Error en rag_router: {e}")
            return None
    
    def rag_search(self, query: str, hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera respuesta usando el corpus propio"""
        try:
            # Construir prompt con fuentes
            sources_text = ""
            references = []
            
            for hit in hits:
                doc = hit['document']
                metadata = hit['metadata']
                similarity = hit['similarity']
                index = hit['index']
                
                source_name = metadata.get('source', 'Unknown')
                chunk_index = metadata.get('chunk_index', 0)
                
                sources_text += f"[{index}] {doc}\n(Fuente: {source_name}, fragmento {chunk_index}, similitud: {similarity:.3f})\n\n"
                
                references.append({
                    'index': index,
                    'source': source_name,
                    'chunk_index': chunk_index,
                    'similarity': similarity,
                    'snippet': doc[:200] + "..." if len(doc) > 200 else doc
                })
            
            # Construir prompt
            prompt = f"""Eres un experto en el dominio específico. Usando ÚNICAMENTE las fuentes proporcionadas a continuación, responde la siguiente pregunta de manera precisa y detallada.

Pregunta: {query}

Fuentes disponibles:
{sources_text}

Instrucciones:
1. Responde ÚNICAMENTE basándote en la información de las fuentes proporcionadas
2. Si la información no está en las fuentes, indica claramente que no tienes esa información
3. Cita las fuentes relevantes usando los números [1], [2], etc.
4. Sé preciso y específico en tu respuesta
5. Si hay información contradictoria entre fuentes, menciónalo

Respuesta:"""
            
            # Llamar al LLM
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto que responde únicamente basándose en las fuentes proporcionadas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Baja temperatura para respuestas precisas
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "references": references,
                "source_type": "rag",
                "query": query,
                "hits_used": len(hits)
            }
            
        except Exception as e:
            logger.error(f"Error en rag_search: {e}")
            return {
                "error": f"Error generando respuesta RAG: {str(e)}",
                "source_type": "rag_error"
            }
    
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Busca documentos relevantes usando embeddings"""
        try:
            self._lazy_init()
            
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode([query]).tolist()[0]
            
            # Buscar documentos similares
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            return {
                "documents": results['documents'][0] if results['documents'] else [],
                "metadatas": results['metadatas'][0] if results['metadatas'] else [],
                "similarities": [1 - dist for dist in results['distances'][0]] if results['distances'] else [],
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error en search_documents: {e}")
            return {"error": str(e)}
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtiene información de la colección"""
        try:
            self._lazy_init()
            count = self.collection.count()
            return {
                "collection_name": settings.RAG_COLLECTION,
                "document_count": count,
                "score_threshold": settings.RAG_SCORE_THRESHOLD,
                "min_hits": settings.RAG_MIN_HITS,
                "embedding_model": settings.RAG_EMBEDDING_MODEL
            }
        except Exception as e:
            return {"error": str(e)}

# Instancia global
rag_system = RAGSystem()