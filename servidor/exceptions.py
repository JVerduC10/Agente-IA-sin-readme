"""Excepciones unificadas del sistema"""

class AISystemException(Exception):
    """Excepción base del sistema AI"""
    pass

class SearchException(AISystemException):
    """Excepciones relacionadas con búsqueda"""
    pass

class RAGException(AISystemException):
    """Excepciones relacionadas con RAG"""
    pass

class WebScrapingException(AISystemException):
    """Excepciones relacionadas con web scraping"""
    pass

# Alias para compatibilidad
WebSearchError = SearchException
WebScrapingError = WebScrapingException
