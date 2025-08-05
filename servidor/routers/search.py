from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import Response
from typing import Dict, Any, Optional
import logging
import time

from ..auth.handlers import check_api_key_header as check_api_key
from ..services.search import search_router
from ..metrics import get_metrics, get_metrics_content_type, metrics

# Importaciones lazy para evitar problemas con ChromaDB
ingestor = None
rag_system = None

def _get_rag_system():
    global rag_system
    if rag_system is None:
        from ..rag import rag_system as _rag_system
        rag_system = _rag_system
    return rag_system

def _get_ingestor():
    global ingestor
    if ingestor is None:
        from ..ingest import ingestor as _ingestor
        ingestor = _ingestor
    return ingestor

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search")
async def search_endpoint(q: str) -> Dict[str, Any]:
    """
    Endpoint de búsqueda que usa RAG o web automáticamente
    
    - **q**: Consulta de búsqueda
    
    Retorna:
    - Respuesta del sistema RAG si encuentra documentos relevantes
    - Respuesta de búsqueda web si no hay documentos relevantes en RAG
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    try:
        result = search_router.search(q.strip())
        
        # Actualizar métricas de colección
        try:
            collection_info = _get_rag_system().get_collection_info()
            if 'document_count' in collection_info:
                metrics.update_collection_size(collection_info['document_count'])
        except Exception as e:
            logger.warning(f"Error updating collection metrics: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    source_name: Optional[str] = Form(None),
    api_key: str = Depends(check_api_key)
) -> Dict[str, Any]:
    """
    Endpoint para ingestar documentos (requiere autenticación)
    
    - **file**: Archivo a ingestar (PDF, CSV, MD)
    - **source_name**: Nombre opcional para el documento
    
    Requiere API key válida en header Authorization: Bearer <api_key>
    """
    try:
        # Validar tipo de archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        file_extension = file.filename.split('.')[-1].lower()
        supported_types = ['pdf', 'csv', 'md', 'markdown']
        
        if file_extension not in supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported: {supported_types}"
            )
        
        # Ingestar archivo
        result = await _get_ingestor().ingest_upload_file(file)
        
        # Registrar métricas
        status = result.get('status', 'unknown')
        chunks_count = result.get('chunks_created', 0)
        
        metrics.record_document_ingest(
            file_type=file_extension,
            status=status,
            chunks_count=chunks_count
        )
        
        # Actualizar tamaño de colección
        try:
            collection_info = _get_rag_system().get_collection_info()
            if 'document_count' in collection_info:
                metrics.update_collection_size(collection_info['document_count'])
        except Exception as e:
            logger.warning(f"Error updating collection size: {e}")
        
        if status == 'error':
            raise HTTPException(status_code=500, detail=result.get('message', 'Ingestion failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {e}")
        
        # Registrar métrica de error
        file_ext = file.filename.split('.')[-1].lower() if file.filename else 'unknown'
        metrics.record_document_ingest(file_type=file_ext, status='error')
        
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

@router.get("/rag/stats")
async def get_rag_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del sistema RAG
    """
    try:
        search_stats = search_router.get_search_stats()
        collection_stats = _get_ingestor().get_collection_stats()
        
        return {
            "search_system": search_stats,
            "collection": collection_stats,
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@router.get("/metrics")
async def get_prometheus_metrics():
    """
    Endpoint para métricas de Prometheus
    """
    try:
        metrics_data = get_metrics()
        return Response(
            content=metrics_data,
            media_type=get_metrics_content_type()
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")

@router.delete("/rag/collection")
async def clear_collection(api_key: str = Depends(check_api_key)) -> Dict[str, Any]:
    """
    Limpia toda la colección RAG (requiere autenticación)
    
    Requiere API key válida en header Authorization: Bearer <api_key>
    """
    try:
        # Eliminar y recrear colección
        ingestor_instance = _get_ingestor()
        ingestor_instance.chroma_client.delete_collection(ingestor_instance.collection.name)
        ingestor_instance.collection = ingestor_instance.chroma_client.create_collection(
            name=ingestor_instance.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Actualizar métricas
        metrics.update_collection_size(0)
        
        logger.info("RAG collection cleared")
        
        return {
            "status": "success",
            "message": "Collection cleared successfully",
            "documents_remaining": 0
        }
        
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise HTTPException(status_code=500, detail=f"Clear error: {str(e)}")

import time