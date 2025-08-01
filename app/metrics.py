from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# Métricas RAG
rag_queries_total = Counter(
    'rag_queries_total',
    'Total number of RAG queries processed',
    ['query_type']  # 'rag' or 'web'
)

rag_used_total = Counter(
    'rag_used_total', 
    'Total number of queries answered using domain corpus'
)

rag_fallback_total = Counter(
    'rag_fallback_total',
    'Total number of queries that fell back to web search'
)

rag_latency_seconds = Histogram(
    'rag_latency_seconds',
    'RAG query processing latency in seconds',
    ['operation']  # 'embedding', 'search', 'llm', 'total'
)

rag_similarity_scores = Histogram(
    'rag_similarity_scores',
    'Distribution of similarity scores for RAG hits',
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

rag_hits_count = Histogram(
    'rag_hits_count',
    'Number of hits above threshold per query',
    buckets=[0, 1, 2, 3, 4, 5, 10, 20, 50]
)

rag_collection_size = Gauge(
    'rag_collection_size',
    'Current number of documents in RAG collection'
)

# Métricas de ingesta
ingest_documents_total = Counter(
    'ingest_documents_total',
    'Total number of documents ingested',
    ['file_type', 'status']  # status: 'success' or 'error'
)

ingest_chunks_total = Counter(
    'ingest_chunks_total',
    'Total number of text chunks created during ingestion'
)

ingest_latency_seconds = Histogram(
    'ingest_latency_seconds',
    'Document ingestion latency in seconds',
    ['operation']  # 'extraction', 'chunking', 'embedding', 'storage'
)

class MetricsCollector:
    """Clase para recopilar métricas del sistema RAG"""
    
    @staticmethod
    def record_rag_query(query_type: str):
        """Registra una consulta RAG"""
        rag_queries_total.labels(query_type=query_type).inc()
    
    @staticmethod
    def record_rag_used():
        """Registra uso del corpus RAG"""
        rag_used_total.inc()
    
    @staticmethod
    def record_rag_fallback():
        """Registra fallback a búsqueda web"""
        rag_fallback_total.inc()
    
    @staticmethod
    def record_similarity_scores(scores: list):
        """Registra scores de similitud"""
        for score in scores:
            rag_similarity_scores.observe(score)
    
    @staticmethod
    def record_hits_count(count: int):
        """Registra número de hits"""
        rag_hits_count.observe(count)
    
    @staticmethod
    def update_collection_size(size: int):
        """Actualiza el tamaño de la colección"""
        rag_collection_size.set(size)
    
    @staticmethod
    def record_document_ingest(file_type: str, status: str, chunks_count: int = 0):
        """Registra ingesta de documento"""
        ingest_documents_total.labels(file_type=file_type, status=status).inc()
        if status == 'success' and chunks_count > 0:
            ingest_chunks_total.inc(chunks_count)

def measure_time(operation: str, metric: Histogram):
    """Decorador para medir tiempo de operaciones"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric.labels(operation=operation).observe(duration)
                logger.debug(f"Operation {operation} took {duration:.3f} seconds")
        return wrapper
    return decorator

def measure_rag_latency(operation: str):
    """Decorador específico para medir latencia RAG"""
    return measure_time(operation, rag_latency_seconds)

def measure_ingest_latency(operation: str):
    """Decorador específico para medir latencia de ingesta"""
    return measure_time(operation, ingest_latency_seconds)

def get_metrics() -> str:
    """Obtiene todas las métricas en formato Prometheus"""
    return generate_latest()

def get_metrics_content_type() -> str:
    """Obtiene el content type para métricas"""
    return CONTENT_TYPE_LATEST

# Instancia global
metrics = MetricsCollector()