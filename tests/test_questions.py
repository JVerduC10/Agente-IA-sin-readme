"""Tests para el sistema de preguntas automáticas."""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import os

from servidor.models.questions import (
    Question,
    QuestionCategory,
    QuestionCreateRequest,
    QuestionTrigger,
    QuestionUpdateRequest
)
from servidor.services.question_manager import QuestionManager


@pytest.fixture
def temp_storage():
    """Fixture para crear almacenamiento temporal."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def question_manager_instance(temp_storage):
    """Fixture para crear una instancia de QuestionManager con almacenamiento temporal."""
    # Reset singleton
    QuestionManager._instance = None
    QuestionManager._initialized = False
    
    manager = QuestionManager(storage_path=temp_storage)
    return manager


class TestQuestionModel:
    """Tests para los modelos de preguntas."""
    
    def test_question_creation(self):
        """Test creación básica de pregunta."""
        question = Question(
            id="test-1",
            text="¿Cómo estás?",
            category=QuestionCategory.GENERAL,
            priority=5
        )
        
        assert question.id == "test-1"
        assert question.text == "¿Cómo estás?"
        assert question.category == QuestionCategory.GENERAL
        assert question.priority == 5
        assert question.is_active is True
        assert isinstance(question.created_at, datetime)
    
    def test_question_create_request(self):
        """Test modelo de solicitud de creación."""
        request = QuestionCreateRequest(
            text="¿Necesitas ayuda?",
            category=QuestionCategory.TECHNICAL,
            priority=8,
            triggers=["ayuda", "problema"],
            trigger_type=QuestionTrigger.KEYWORD
        )
        
        assert request.text == "¿Necesitas ayuda?"
        assert request.category == QuestionCategory.TECHNICAL
        assert request.priority == 8
        assert "ayuda" in request.triggers
        assert request.trigger_type == QuestionTrigger.KEYWORD


class TestQuestionManager:
    """Tests para el gestor de preguntas."""
    
    def test_manager_initialization(self, question_manager_instance):
        """Test inicialización del gestor."""
        manager = question_manager_instance
        
        assert manager is not None
        assert isinstance(manager.questions, dict)
        assert len(manager.questions) > 0  # Debe tener preguntas por defecto
    
    def test_create_question(self, question_manager_instance):
        """Test creación de pregunta."""
        manager = question_manager_instance
        
        request = QuestionCreateRequest(
            text="¿Qué opinas sobre esto?",
            category=QuestionCategory.EXPLORATION,
            priority=7
        )
        
        question = manager.create_question(request)
        
        assert question.text == "¿Qué opinas sobre esto?"
        assert question.category == QuestionCategory.EXPLORATION
        assert question.priority == 7
        assert question.id in manager.questions
    
    def test_get_question(self, question_manager_instance):
        """Test obtener pregunta por ID."""
        manager = question_manager_instance
        
        # Crear una pregunta
        request = QuestionCreateRequest(text="Test question")
        created_question = manager.create_question(request)
        
        # Obtener la pregunta
        retrieved_question = manager.get_question(created_question.id)
        
        assert retrieved_question is not None
        assert retrieved_question.id == created_question.id
        assert retrieved_question.text == "Test question"
    
    def test_get_all_questions(self, question_manager_instance):
        """Test obtener todas las preguntas."""
        manager = question_manager_instance
        
        # Obtener preguntas activas
        active_questions = manager.get_all_questions(active_only=True)
        assert len(active_questions) > 0
        assert all(q.is_active for q in active_questions)
        
        # Obtener por categoría
        general_questions = manager.get_all_questions(
            category=QuestionCategory.GENERAL,
            active_only=True
        )
        assert all(q.category == QuestionCategory.GENERAL for q in general_questions)
    
    def test_update_question(self, question_manager_instance):
        """Test actualizar pregunta."""
        manager = question_manager_instance
        
        # Crear pregunta
        request = QuestionCreateRequest(text="Original text")
        question = manager.create_question(request)
        
        # Actualizar pregunta
        update_request = QuestionUpdateRequest(
            text="Updated text",
            priority=9
        )
        updated_question = manager.update_question(question.id, update_request)
        
        assert updated_question is not None
        assert updated_question.text == "Updated text"
        assert updated_question.priority == 9
    
    def test_delete_question(self, question_manager_instance):
        """Test eliminar pregunta."""
        manager = question_manager_instance
        
        # Crear pregunta
        request = QuestionCreateRequest(text="To be deleted")
        question = manager.create_question(request)
        question_id = question.id
        
        # Verificar que existe
        assert manager.get_question(question_id) is not None
        
        # Eliminar pregunta
        success = manager.delete_question(question_id)
        assert success is True
        
        # Verificar que no existe
        assert manager.get_question(question_id) is None
    
    def test_activate_question(self, question_manager_instance):
        """Test activar pregunta."""
        manager = question_manager_instance
        
        # Crear pregunta
        request = QuestionCreateRequest(text="Test activation")
        question = manager.create_question(request)
        
        initial_usage = question.usage_count
        initial_last_used = question.last_used
        
        # Activar pregunta
        success = manager.activate_question(question.id)
        assert success is True
        
        # Verificar estadísticas actualizadas
        updated_question = manager.get_question(question.id)
        assert updated_question.usage_count == initial_usage + 1
        assert updated_question.last_used != initial_last_used
    
    def test_get_relevant_questions(self, question_manager_instance):
        """Test obtener preguntas relevantes."""
        manager = question_manager_instance
        
        # Crear pregunta con keywords específicos
        request = QuestionCreateRequest(
            text="¿Necesitas más detalles?",
            context_keywords=["detalles", "información", "explicar"]
        )
        manager.create_question(request)
        
        # Buscar preguntas relevantes
        context = "Me gustaría obtener más detalles sobre este tema"
        relevant_questions = manager.get_relevant_questions(context, limit=3)
        
        assert len(relevant_questions) > 0
        # Verificar que al menos una pregunta contiene keywords relevantes
        found_relevant = any(
            any(keyword in context.lower() for keyword in q.context_keywords)
            for q in relevant_questions
        )
        assert found_relevant
    
    def test_evaluate_context(self, question_manager_instance):
        """Test evaluación de contexto."""
        manager = question_manager_instance
        
        chat_history = [
            "Hola, necesito ayuda con un problema",
            "¿Podrías explicar más detalles sobre esto?"
        ]
        
        suggestion = manager.evaluate_context(chat_history, message_count=2)
        
        assert suggestion is not None
        assert isinstance(suggestion.questions, list)
        assert isinstance(suggestion.confidence, float)
        assert 0.0 <= suggestion.confidence <= 1.0
    
    def test_get_statistics(self, question_manager_instance):
        """Test obtener estadísticas."""
        manager = question_manager_instance
        
        stats = manager.get_statistics()
        
        assert "total_questions" in stats
        assert "active_questions" in stats
        assert "total_responses" in stats
        assert "category_distribution" in stats
        assert "most_used_questions" in stats
        
        assert isinstance(stats["total_questions"], int)
        assert isinstance(stats["active_questions"], int)
        assert isinstance(stats["category_distribution"], dict)
        assert isinstance(stats["most_used_questions"], list)
    
    def test_persistence(self, temp_storage):
        """Test persistencia de datos."""
        # Reset singleton
        QuestionManager._instance = None
        QuestionManager._initialized = False
        
        # Crear primer manager y agregar pregunta
        manager1 = QuestionManager(storage_path=temp_storage)
        request = QuestionCreateRequest(text="Persistent question")
        question = manager1.create_question(request)
        question_id = question.id
        
        # Reset singleton
        QuestionManager._instance = None
        QuestionManager._initialized = False
        
        # Crear segundo manager y verificar persistencia
        manager2 = QuestionManager(storage_path=temp_storage)
        retrieved_question = manager2.get_question(question_id)
        
        assert retrieved_question is not None
        assert retrieved_question.text == "Persistent question"
        assert retrieved_question.id == question_id


class TestQuestionCategories:
    """Tests para categorías de preguntas."""
    
    def test_all_categories_available(self):
        """Test que todas las categorías están disponibles."""
        expected_categories = {
            "general", "technical", "followup", 
            "clarification", "exploration", "summary"
        }
        
        actual_categories = {category.value for category in QuestionCategory}
        
        assert actual_categories == expected_categories
    
    def test_question_trigger_types(self):
        """Test tipos de triggers disponibles."""
        expected_triggers = {
            "keyword", "message_count", "rag_context", 
            "web_search", "manual", "time_based"
        }
        
        actual_triggers = {trigger.value for trigger in QuestionTrigger}
        
        assert actual_triggers == expected_triggers