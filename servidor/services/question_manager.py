"""Gestor del sistema de preguntas automáticas."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.questions import (
    Question,
    QuestionCategory,
    QuestionCreateRequest,
    QuestionResponse,
    QuestionSuggestion,
    QuestionTrigger,
    QuestionUpdateRequest
)


class QuestionManager:
    """Gestor centralizado del sistema de preguntas."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, storage_path: str = "data/questions.json"):
        """Implementación singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, storage_path: str = "data/questions.json"):
        """Inicializa el gestor de preguntas."""
        if self._initialized:
            return
            
        self.storage_path = Path(storage_path)
        self.questions: Dict[str, Question] = {}
        self.responses: List[QuestionResponse] = []
        self._ensure_storage_directory()
        self.load_questions()
        self._initialized = True
    
    def _ensure_storage_directory(self) -> None:
        """Asegura que el directorio de almacenamiento existe."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_questions(self) -> None:
        """Carga las preguntas desde el almacenamiento."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Cargar preguntas
                questions_data = data.get('questions', {})
                for q_id, q_data in questions_data.items():
                    # Convertir datetime strings de vuelta a datetime objects
                    if 'created_at' in q_data:
                        q_data['created_at'] = datetime.fromisoformat(q_data['created_at'])
                    if 'last_used' in q_data and q_data['last_used']:
                        q_data['last_used'] = datetime.fromisoformat(q_data['last_used'])
                    
                    self.questions[q_id] = Question(**q_data)
                
                # Cargar respuestas
                responses_data = data.get('responses', [])
                for r_data in responses_data:
                    if 'timestamp' in r_data:
                        r_data['timestamp'] = datetime.fromisoformat(r_data['timestamp'])
                    self.responses.append(QuestionResponse(**r_data))
                    
            else:
                # Crear preguntas por defecto
                self._create_default_questions()
                self.save_questions()
                
        except Exception as e:
            print(f"Error cargando preguntas: {e}")
            self._create_default_questions()
    
    def _create_default_questions(self) -> None:
        """Crea preguntas por defecto del sistema."""
        default_questions = [
            {
                "text": "¿Podrías explicar más sobre este tema?",
                "category": QuestionCategory.EXPLORATION,
                "priority": 7,
                "trigger_type": QuestionTrigger.RAG_CONTEXT,
                "context_keywords": ["explicar", "detalles", "información"]
            },
            {
                "text": "¿Hay algún aspecto específico que te interese más?",
                "category": QuestionCategory.CLARIFICATION,
                "priority": 6,
                "trigger_type": QuestionTrigger.MESSAGE_COUNT,
                "context_keywords": ["específico", "interés", "enfoque"]
            },
            {
                "text": "¿Te gustaría que busque información adicional sobre esto?",
                "category": QuestionCategory.FOLLOWUP,
                "priority": 8,
                "trigger_type": QuestionTrigger.WEB_SEARCH,
                "context_keywords": ["buscar", "información", "adicional"]
            },
            {
                "text": "¿Necesitas un resumen de lo que hemos discutido?",
                "category": QuestionCategory.SUMMARY,
                "priority": 5,
                "trigger_type": QuestionTrigger.MESSAGE_COUNT,
                "context_keywords": ["resumen", "discutido", "conversación"]
            },
            {
                "text": "¿Hay algún problema técnico específico que necesites resolver?",
                "category": QuestionCategory.TECHNICAL,
                "priority": 9,
                "trigger_type": QuestionTrigger.KEYWORD,
                "context_keywords": ["error", "problema", "técnico", "código", "bug"]
            }
        ]
        
        for q_data in default_questions:
            question = self.create_question(QuestionCreateRequest(**q_data))
    
    def save_questions(self) -> None:
        """Guarda las preguntas en el almacenamiento."""
        try:
            data = {
                "questions": {},
                "responses": []
            }
            
            # Serializar preguntas
            for q_id, question in self.questions.items():
                data["questions"][q_id] = question.dict()
            
            # Serializar respuestas
            for response in self.responses:
                data["responses"].append(response.dict())
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"Error guardando preguntas: {e}")
    
    def create_question(self, request: QuestionCreateRequest) -> Question:
        """Crea una nueva pregunta."""
        question_id = str(uuid.uuid4())
        question = Question(
            id=question_id,
            text=request.text,
            category=request.category,
            priority=request.priority,
            triggers=request.triggers,
            trigger_type=request.trigger_type,
            context_keywords=request.context_keywords,
            metadata=request.metadata
        )
        
        self.questions[question_id] = question
        self.save_questions()
        return question
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """Obtiene una pregunta por ID."""
        return self.questions.get(question_id)
    
    def get_all_questions(self, category: Optional[QuestionCategory] = None, 
                         active_only: bool = True) -> List[Question]:
        """Obtiene todas las preguntas con filtros opcionales."""
        questions = list(self.questions.values())
        
        if active_only:
            questions = [q for q in questions if q.is_active]
        
        if category:
            questions = [q for q in questions if q.category == category]
        
        # Ordenar por prioridad (mayor primero) y luego por fecha de creación
        questions.sort(key=lambda q: (-q.priority, q.created_at))
        return questions
    
    def update_question(self, question_id: str, request: QuestionUpdateRequest) -> Optional[Question]:
        """Actualiza una pregunta existente."""
        question = self.questions.get(question_id)
        if not question:
            return None
        
        # Actualizar campos no nulos
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        self.save_questions()
        return question
    
    def delete_question(self, question_id: str) -> bool:
        """Elimina una pregunta."""
        if question_id in self.questions:
            del self.questions[question_id]
            self.save_questions()
            return True
        return False
    
    def activate_question(self, question_id: str) -> bool:
        """Activa una pregunta y actualiza estadísticas de uso."""
        question = self.questions.get(question_id)
        if not question:
            return False
        
        question.usage_count += 1
        question.last_used = datetime.now()
        self.save_questions()
        return True
    
    def get_relevant_questions(self, context: str, limit: int = 5) -> List[Question]:
        """Obtiene preguntas relevantes basadas en el contexto."""
        context_lower = context.lower()
        relevant_questions = []
        
        for question in self.questions.values():
            if not question.is_active:
                continue
            
            # Calcular relevancia basada en keywords de contexto
            relevance_score = 0
            for keyword in question.context_keywords:
                if keyword.lower() in context_lower:
                    relevance_score += 1
            
            # Agregar bonus por prioridad
            relevance_score += question.priority * 0.1
            
            if relevance_score > 0:
                relevant_questions.append((question, relevance_score))
        
        # Ordenar por relevancia y tomar los primeros
        relevant_questions.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in relevant_questions[:limit]]
    
    def evaluate_context(self, chat_history: List[str], message_count: int = 0) -> QuestionSuggestion:
        """Evalúa el contexto y determina si sugerir preguntas."""
        if not chat_history:
            return QuestionSuggestion()
        
        # Combinar el historial de chat en un contexto
        context = " ".join(chat_history[-3:])  # Últimos 3 mensajes
        
        # Obtener preguntas relevantes
        relevant_questions = self.get_relevant_questions(context)
        
        # Determinar trigger reason
        trigger_reason = "context_analysis"
        confidence = 0.5
        
        # Aumentar confianza si hay keywords específicos
        context_lower = context.lower()
        if any(keyword in context_lower for keyword in ["explicar", "detalles", "más información"]):
            confidence += 0.2
        
        # Trigger por número de mensajes
        if message_count > 0 and message_count % 3 == 0:
            trigger_reason = "message_count_trigger"
            confidence += 0.1
        
        return QuestionSuggestion(
            questions=relevant_questions,
            context=context,
            trigger_reason=trigger_reason,
            confidence=min(confidence, 1.0)
        )
    
    def add_response(self, response: QuestionResponse) -> None:
        """Añade una respuesta a una pregunta."""
        self.responses.append(response)
        self.save_questions()
    
    def get_question_responses(self, question_id: str) -> List[QuestionResponse]:
        """Obtiene todas las respuestas para una pregunta específica."""
        return [r for r in self.responses if r.question_id == question_id]
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del sistema de preguntas."""
        total_questions = len(self.questions)
        active_questions = len([q for q in self.questions.values() if q.is_active])
        total_responses = len(self.responses)
        
        # Estadísticas por categoría
        category_stats = {}
        for question in self.questions.values():
            category = question.category.value
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        # Preguntas más usadas
        most_used = sorted(
            self.questions.values(),
            key=lambda q: q.usage_count,
            reverse=True
        )[:5]
        
        return {
            "total_questions": total_questions,
            "active_questions": active_questions,
            "total_responses": total_responses,
            "category_distribution": category_stats,
            "most_used_questions": [
                {"id": q.id, "text": q.text, "usage_count": q.usage_count}
                for q in most_used
            ]
        }


# Instancia global del gestor
question_manager = QuestionManager()