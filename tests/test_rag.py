import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from io import BytesIO

from app.main import app
from app.rag import RAGSystem
from app.ingest import DocumentIngestor
from app.search_router import SearchRouter
from app.metrics import metrics
from app.settings import Settings

client = TestClient(app)

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    with patch('app.rag.settings') as mock_settings, \
         patch('app.ingest.settings') as mock_ingest_settings, \
         patch('app.search_router.settings') as mock_search_settings:
        
        # Configure mock settings
        mock_settings.RAG_COLLECTION = "test_collection"
        mock_settings.RAG_SCORE_THRESHOLD = 0.35
        mock_settings.RAG_MIN_HITS = 2
        mock_settings.RAG_CHUNK_SIZE = 300
        mock_settings.RAG_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        mock_settings.CHROMA_PERSIST_DIR = "./test_chroma_db"
        mock_settings.GROQ_API_KEY = "test_key"
        mock_settings.GROQ_MODEL = "test_model"
        
        mock_ingest_settings.configure_mock(**mock_settings.__dict__)
        mock_search_settings.configure_mock(**mock_settings.__dict__)
        
        yield mock_settings

@pytest.fixture
def mock_rag_system(mock_settings):
    """Mock RAG system for testing"""
    with patch('app.rag.chromadb'), \
         patch('app.rag.SentenceTransformer'), \
         patch('app.rag.Groq'):
        
        rag = RAGSystem()
        
        # Mock collection
        rag.collection = Mock()
        rag.collection.count.return_value = 5
        rag.collection.query.return_value = {
            'documents': [['Test document 1', 'Test document 2']],
            'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}, 
                          {'source': 'test.pdf', 'chunk_index': 1}]],
            'distances': [[0.2, 0.3]]  # High similarity (low distance)
        }
        
        # Mock embedder
        rag.embedder = Mock()
        rag.embedder.encode.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
        
        # Mock Groq client
        rag.groq_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test RAG response based on documents"
        rag.groq_client.chat.completions.create.return_value = mock_response
        
        yield rag

@pytest.fixture
def mock_ingestor(mock_settings):
    """Mock document ingestor for testing"""
    with patch('app.ingest.chromadb'), \
         patch('app.ingest.SentenceTransformer'):
        
        ingestor = DocumentIngestor()
        ingestor.collection = Mock()
        ingestor.embedder = Mock()
        ingestor.embedder.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        yield ingestor

class TestRAGHit:
    """Test RAG hit scenario"""
    
    def test_rag_hit_with_sufficient_similarity(self, mock_rag_system):
        """Test que RAG responde cuando encuentra documentos relevantes"""
        query = "What is the test document about?"
        
        # Mock high similarity scores
        mock_rag_system.collection.query.return_value = {
            'documents': [['Relevant test document', 'Another relevant document']],
            'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}, 
                          {'source': 'test.pdf', 'chunk_index': 1}]],
            'distances': [[0.1, 0.15]]  # Very high similarity
        }
        
        result = mock_rag_system.rag_router(query)
        
        assert result is not None
        assert result['source_type'] == 'rag'
        assert 'answer' in result
        assert 'references' in result
        assert len(result['references']) >= mock_rag_system.collection.query()['documents'][0].__len__()
        
        # Verify Groq was called
        mock_rag_system.groq_client.chat.completions.create.assert_called_once()
    
    def test_rag_metrics_on_hit(self, mock_rag_system):
        """Test que las métricas se registran correctamente en hit"""
        with patch.object(metrics, 'record_rag_used') as mock_record_used, \
             patch.object(metrics, 'record_similarity_scores') as mock_record_scores:
            
            search_router = SearchRouter()
            search_router.rag_system = mock_rag_system
            
            result = search_router.search("test query")
            
            assert result['source_type'] == 'rag'
            mock_record_used.assert_called_once()
            mock_record_scores.assert_called_once()

class TestRAGNoHit:
    """Test RAG no-hit scenario (fallback to web)"""
    
    def test_rag_nohit_insufficient_similarity(self, mock_rag_system):
        """Test que RAG hace fallback cuando no hay suficiente similitud"""
        query = "Completely unrelated query about space"
        
        # Mock low similarity scores
        mock_rag_system.collection.query.return_value = {
            'documents': [['Test document', 'Another document']],
            'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}, 
                          {'source': 'test.pdf', 'chunk_index': 1}]],
            'distances': [[0.9, 0.95]]  # Very low similarity (high distance)
        }
        
        result = mock_rag_system.rag_router(query)
        
        assert result is None  # Should return None for fallback
    
    def test_rag_nohit_insufficient_hits(self, mock_rag_system):
        """Test que RAG hace fallback cuando no hay suficientes hits"""
        query = "Query with only one relevant result"
        
        # Mock only one document above threshold
        mock_rag_system.collection.query.return_value = {
            'documents': [['Relevant document']],
            'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}]],
            'distances': [[0.2]]  # Only one hit
        }
        
        result = mock_rag_system.rag_router(query)
        
        # Should return None because we need at least 2 hits (RAG_MIN_HITS)
        assert result is None
    
    def test_web_fallback_metrics(self, mock_rag_system):
        """Test que las métricas de fallback se registran correctamente"""
        with patch.object(metrics, 'record_rag_fallback') as mock_record_fallback, \
             patch('app.search_router.requests.get') as mock_requests:
            
            # Mock web search response
            mock_response = Mock()
            mock_response.json.return_value = {
                'AbstractText': 'Web search result',
                'AbstractURL': 'https://example.com'
            }
            mock_requests.return_value = mock_response
            
            # Force RAG to return None (no hits)
            mock_rag_system.rag_router.return_value = None
            
            search_router = SearchRouter()
            search_router.rag_system = mock_rag_system
            
            result = search_router.search("test query")
            
            assert result['source_type'] == 'web'
            mock_record_fallback.assert_called_once()

class TestThresholdConfiguration:
    """Test threshold configuration effects"""
    
    def test_high_threshold_forces_fallback(self, mock_rag_system):
        """Test que un threshold alto (0.9) fuerza fallback"""
        # Temporarily change threshold
        original_threshold = mock_rag_system.collection.query.return_value
        
        with patch('app.rag.settings.RAG_SCORE_THRESHOLD', 0.9):
            # Even with decent similarity, should fallback
            mock_rag_system.collection.query.return_value = {
                'documents': [['Document 1', 'Document 2']],
                'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}, 
                              {'source': 'test.pdf', 'chunk_index': 1}]],
                'distances': [[0.3, 0.4]]  # Decent similarity but below 0.9 threshold
            }
            
            result = mock_rag_system.rag_router("test query")
            
            # Should return None because similarities (0.7, 0.6) < 0.9 threshold
            assert result is None
    
    def test_low_threshold_allows_hits(self, mock_rag_system):
        """Test que un threshold bajo permite más hits"""
        with patch('app.rag.settings.RAG_SCORE_THRESHOLD', 0.1):
            mock_rag_system.collection.query.return_value = {
                'documents': [['Document 1', 'Document 2']],
                'metadatas': [[{'source': 'test.pdf', 'chunk_index': 0}, 
                              {'source': 'test.pdf', 'chunk_index': 1}]],
                'distances': [[0.5, 0.6]]  # Lower similarity but above 0.1 threshold
            }
            
            result = mock_rag_system.rag_router("test query")
            
            # Should return result because similarities (0.5, 0.4) > 0.1 threshold
            assert result is not None
            assert result['source_type'] == 'rag'

class TestIngestion:
    """Test document ingestion"""
    
    def test_pdf_ingestion(self, mock_ingestor):
        """Test ingestion of PDF files"""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4 mock pdf content"
        
        with patch.object(mock_ingestor, 'extract_text_from_pdf', return_value="Mock PDF text content"), \
             patch.object(mock_ingestor, 'chunk_text', return_value=["Chunk 1", "Chunk 2"]), \
             patch.object(mock_ingestor, 'generate_embeddings', return_value=[[0.1, 0.2], [0.3, 0.4]]):
            
            result = mock_ingestor.ingest_file("/tmp/test.pdf", "test_source")
            
            assert result['status'] == 'success'
            assert result['chunks_created'] == 2
            assert result['source'] == 'test_source'
            
            # Verify collection.add was called
            mock_ingestor.collection.add.assert_called_once()
    
    def test_csv_ingestion(self, mock_ingestor):
        """Test ingestion of CSV files"""
        with patch.object(mock_ingestor, 'extract_text_from_csv', return_value="CSV data content"), \
             patch.object(mock_ingestor, 'chunk_text', return_value=["CSV chunk 1"]), \
             patch.object(mock_ingestor, 'generate_embeddings', return_value=[[0.5, 0.6]]):
            
            result = mock_ingestor.ingest_file("/tmp/test.csv", "csv_source")
            
            assert result['status'] == 'success'
            assert result['chunks_created'] == 1
            assert result['source'] == 'csv_source'

class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    def test_search_endpoint_rag_response(self):
        """Test search endpoint with RAG response"""
        with patch('app.routers.search.search_router') as mock_router:
            mock_router.search.return_value = {
                'answer': 'RAG response',
                'source_type': 'rag',
                'references': []
            }
            
            response = client.get("/api/v1/search?q=test query")
            
            assert response.status_code == 200
            data = response.json()
            assert data['source_type'] == 'rag'
            assert 'answer' in data
    
    def test_search_endpoint_web_fallback(self):
        """Test search endpoint with web fallback"""
        with patch('app.routers.search.search_router') as mock_router:
            mock_router.search.return_value = {
                'answer': 'Web search response',
                'source_type': 'web',
                'references': []
            }
            
            response = client.get("/api/v1/search?q=unrelated query")
            
            assert response.status_code == 200
            data = response.json()
            assert data['source_type'] == 'web'
    
    def test_ingest_endpoint_requires_auth(self):
        """Test that ingest endpoint requires authentication"""
        # Create a mock file
        file_content = b"Test document content"
        files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
        
        response = client.post("/api/v1/ingest", files=files)
        
        # Should return 401 or 403 without proper auth
        assert response.status_code in [401, 403]
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        # Should return Prometheus format
        assert "text/plain" in response.headers.get("content-type", "")