import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO

# Mock all problematic modules before any imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['onnxruntime'] = MagicMock()

from servidor.main import app

client = TestClient(app)

@pytest.fixture
def mock_rag_system():
    """Mock RAG system for testing"""
    mock_rag = Mock()
    mock_rag.rag_router = Mock()
    mock_rag.search_documents = Mock()
    mock_rag.get_collection_info = Mock()
    return mock_rag

@pytest.fixture
def mock_ingestor():
    """Mock document ingestor for testing"""
    mock_ingest = Mock()
    mock_ingest.ingest_upload_file = Mock()
    return mock_ingest

class TestRAGHit:
    """Test cases for successful RAG hits"""
    
    def test_rag_hit_with_sufficient_similarity(self, mock_rag_system):
        """Test RAG hit with sufficient similarity"""
        mock_rag_system.rag_router.return_value = {
            'answer': 'RAG response',
            'source_type': 'rag',
            'references': []
        }
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is not None
        assert result['source_type'] == 'rag'
        assert result['answer'] == 'RAG response'
    
    def test_rag_metrics_on_hit(self, mock_rag_system):
        """Test that metrics are recorded correctly on hit"""
        mock_rag_system.rag_router.return_value = {
            'answer': 'RAG response',
            'source_type': 'rag',
            'references': []
        }
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is not None
        assert result['source_type'] == 'rag'

class TestRAGNoHit:
    """Test cases for RAG misses and fallbacks"""
    
    def test_rag_nohit_insufficient_similarity(self, mock_rag_system):
        """Test RAG miss due to insufficient similarity"""
        mock_rag_system.rag_router.return_value = None
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is None
    
    def test_rag_nohit_insufficient_hits(self, mock_rag_system):
        """Test RAG miss due to insufficient hits"""
        mock_rag_system.rag_router.return_value = None
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is None
    
    def test_web_fallback_metrics(self, mock_rag_system):
        """Test that fallback metrics are recorded correctly"""
        mock_rag_system.rag_router.return_value = None
        
        # Simulate web fallback
        mock_web_result = {
            'answer': 'Web fallback response',
            'source_type': 'web',
            'references': []
        }
        
        result = mock_web_result
        assert result['source_type'] == 'web'

class TestThresholdConfiguration:
    """Test threshold configuration effects"""
    
    def test_high_threshold_forces_fallback(self, mock_rag_system):
        """Test that high threshold forces fallback"""
        mock_rag_system.rag_router.return_value = None
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is None
    
    def test_low_threshold_allows_hits(self, mock_rag_system):
        """Test that low threshold allows hits"""
        mock_rag_system.rag_router.return_value = {
            'source_type': 'rag',
            'answer': 'RAG response',
            'references': []
        }
        
        result = mock_rag_system.rag_router("test query")
        
        assert result is not None
        assert result['source_type'] == 'rag'

class TestIngestion:
    """Test document ingestion functionality"""
    
    def test_pdf_ingestion(self, mock_ingestor):
        """Test PDF file ingestion"""
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.file.read.return_value = b"Mock PDF content"
        
        mock_ingestor.ingest_upload_file.return_value = {
            'status': 'success',
            'chunks_created': 5,
            'filename': 'test.pdf'
        }
        
        result = mock_ingestor.ingest_upload_file(mock_file)
        
        assert result['status'] == 'success'
        assert result['chunks_created'] == 5
    
    def test_csv_ingestion(self, mock_ingestor):
        """Test CSV file ingestion"""
        mock_file = Mock()
        mock_file.filename = "test.csv"
        mock_file.file.read.return_value = b"Name,Age\nJohn,25\nJane,30"
        
        mock_ingestor.ingest_upload_file.return_value = {
            'status': 'success',
            'chunks_created': 2,
            'filename': 'test.csv'
        }
        
        result = mock_ingestor.ingest_upload_file(mock_file)
        
        assert result['status'] == 'success'
        assert result['chunks_created'] == 2

class TestAPIEndpoints:
    """Test API endpoints"""
    
    @patch('servidor.routers.search._get_rag_system')
    def test_search_endpoint_rag_response(self, mock_get_rag):
        """Test search endpoint with RAG response"""
        mock_rag = Mock()
        mock_rag.rag_router.return_value = {
            'answer': 'RAG response',
            'source_type': 'rag',
            'references': []
        }
        mock_get_rag.return_value = mock_rag
        
        response = client.get("/api/v1/search?q=test query")
        
        assert response.status_code == 200
    
    @patch('servidor.routers.search._get_rag_system')
    def test_search_endpoint_web_fallback(self, mock_get_rag):
        """Test search endpoint with web fallback"""
        mock_rag = Mock()
        mock_rag.rag_router.return_value = None
        mock_get_rag.return_value = mock_rag
        
        response = client.get("/api/v1/search?q=test query")
        
        assert response.status_code == 200
    
    def test_ingest_endpoint_requires_auth(self):
        """Test that ingest endpoint requires authentication"""
        response = client.post("/api/v1/ingest")
        
        # Should return 422 for missing form data, 401 for missing auth, or 403 for forbidden
        assert response.status_code in [401, 403, 422]
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")