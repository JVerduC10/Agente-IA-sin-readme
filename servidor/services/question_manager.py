"""Gestor del sistema de preguntas automáticas.

Este módulo ha sido refactorizado para eliminar lógica heurística basada en keywords
y usar análisis semántico con LLM para generar preguntas contextualmente relevantes.
"""

import json
import uuid
import asyncio
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
from ..core.llm_service import LLMService


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
        self.conversation_contexts: Dict[str, Dict] = {}  # Rastreo de contextos por conversación
        self.llm_service = LLMService()  # Servicio LLM para análisis semántico
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
                "context_keywords": []  # Eliminado: ahora usa análisis semántico LLM
            },
            {
                "text": "¿Hay algún aspecto específico que te interese más?",
                "category": QuestionCategory.CLARIFICATION,
                "priority": 6,
                "trigger_type": QuestionTrigger.MESSAGE_COUNT,
                "context_keywords": []  # Eliminado: ahora usa análisis semántico LLM
            },
            {
                "text": "¿Te gustaría que busque información adicional sobre esto?",
                "category": QuestionCategory.FOLLOWUP,
                "priority": 8,
                "trigger_type": QuestionTrigger.WEB_SEARCH,
                "context_keywords": []  # Eliminado: ahora usa análisis semántico LLM
            },
            {
                "text": "¿Necesitas un resumen de lo que hemos discutido?",
                "category": QuestionCategory.SUMMARY,
                "priority": 5,
                "trigger_type": QuestionTrigger.MESSAGE_COUNT,
                "context_keywords": []  # Eliminado: ahora usa análisis semántico LLM
            },
            {
                "text": "¿Hay algún problema técnico específico que necesites resolver?",
                "category": QuestionCategory.TECHNICAL,
                "priority": 9,
                "trigger_type": QuestionTrigger.KEYWORD,
                "context_keywords": []  # Eliminado: ahora usa análisis semántico LLM
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
    
    async def get_relevant_questions(self, context: str, limit: int = 5) -> List[Question]:
        """Obtiene preguntas relevantes basadas en análisis semántico del contexto.
        
        Reemplaza la lógica heurística de keywords con análisis LLM para determinar
        la relevancia contextual de las preguntas.
        """
        try:
            # Usar análisis semántico LLM para obtener preguntas relevantes
            result = await self._get_relevant_questions_semantic(context, limit)
            return result
        except Exception as e:
            print(f"Error en análisis semántico de preguntas: {e}")
            return self._fallback_relevant_questions(context, limit)
    
    async def _get_relevant_questions_semantic(self, context: str, limit: int = 5) -> List[Question]:
        """Análisis semántico para obtener preguntas relevantes usando LLM."""
        active_questions = [q for q in self.questions.values() if q.is_active]
        
        if not active_questions:
            return []
        
        # Preparar datos de preguntas para el LLM
        questions_data = [
            {
                "id": q.id,
                "text": q.text,
                "category": q.category.value,
                "priority": q.priority
            }
            for q in active_questions
        ]
        
        # Usar LLM para análisis de relevancia contextual
        result = await self.llm_service.generate_contextual_questions(
            context=context,
            available_questions=questions_data,
            max_questions=limit
        )
        
        # Mapear IDs de vuelta a objetos Question
        relevant_questions = []
        for q_id in result.get('selected_question_ids', []):
            question = self.questions.get(q_id)
            if question:
                relevant_questions.append(question)
        
        return relevant_questions[:limit]
    
    def _fallback_relevant_questions(self, context: str, limit: int = 5) -> List[Question]:
        """Método de respaldo simplificado cuando falla el análisis LLM."""
        active_questions = [q for q in self.questions.values() if q.is_active]
        
        # Ordenar por prioridad como respaldo básico
        active_questions.sort(key=lambda x: x.priority, reverse=True)
        return active_questions[:limit]
    
    async def evaluate_context(self, chat_history: List[str], message_count: int = 0, conversation_id: str = "default") -> QuestionSuggestion:
        """Evalúa el contexto y determina si sugerir preguntas con iteraciones múltiples."""
        # Debug: evaluate_context called
        
        if not chat_history:
            # No chat history, returning empty suggestion
            return QuestionSuggestion()
        
        # Inicializar contexto de conversación si no existe
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = {
                "iteration_level": 1,
                "learning_path": [],
                "topics_covered": set(),
                "context_depth": "basic",
                "last_questions": []
            }
        
        conv_context = self.conversation_contexts[conversation_id]
        
        # Combinar el historial de chat en un contexto
        context = " ".join(chat_history[-5:])  # Últimos 5 mensajes para más contexto
        
        # Determinar fase de iteración basado en el número de mensajes del usuario únicamente
        # Fase 1: Descubrimiento (mensaje 1)
        # Fase 2: Exploración (mensajes 2-3)
        # Fase 3: Análisis Profundo (mensajes 4-5)
        # Fase 4: Aplicación (mensajes 6-7)
        # Fase 5: Maestría (mensajes 8+)
        user_message_count = len([msg for msg in chat_history if msg.strip()])
        if user_message_count <= 1:
            iteration_level = 1
        elif user_message_count <= 3:
            iteration_level = 2
        elif user_message_count <= 5:
            iteration_level = 3
        elif user_message_count <= 7:
            iteration_level = 4
        else:
            iteration_level = 5
        
        conv_context["iteration_level"] = iteration_level
        conv_context["user_message_count"] = user_message_count
        
        # Determinar profundidad del contexto basado en la iteración
        depth_levels = ["basic", "intermediate", "advanced", "expert", "specialized"]
        context_depth = depth_levels[min(iteration_level - 1, len(depth_levels) - 1)]
        conv_context["context_depth"] = context_depth
        
        # Obtener preguntas relevantes basadas en la iteración
        relevant_questions = await self._get_iterative_questions(context, iteration_level, conv_context)
        # Found relevant questions for current iteration
        
        # Determinar trigger reason
        trigger_reason = f"iteration_{iteration_level}_analysis"
        confidence = 0.6 + (iteration_level * 0.1)  # Aumentar confianza con iteraciones
        # Base confidence calculated
        
        # Usar análisis semántico LLM para determinar confianza contextual
        try:
            # Llamada asincrónica correcta al servicio LLM
            llm_resp = await self.llm_service.analyze_semantically(context)
            if llm_resp and llm_resp.success and llm_resp.data:
                semantic_confidence = llm_resp.data.get('confidence_boost', 0.0)
                confidence += min(semantic_confidence, 0.3)  # Máximo boost de 0.3
            else:
                print("Warning: semantic analysis failed or empty, using fallback confidence")
                confidence += 0.1
        except Exception as e:
            print(f"Error en análisis semántico de confianza: {e}")
            # Fallback: boost mínimo
            confidence += 0.1
        
        # Actualizar ruta de aprendizaje
        if relevant_questions:
            topics = await self._extract_topics_from_questions(relevant_questions)
            conv_context["learning_path"].extend(topics)
            conv_context["topics_covered"].update(topics)
            conv_context["last_questions"] = [q.text for q in relevant_questions]
        
        final_confidence = min(confidence, 1.0)
        # Final confidence and questions determined
        
        return QuestionSuggestion(
            questions=relevant_questions,
            context=context,
            trigger_reason=trigger_reason,
            confidence=final_confidence,
            iteration_level=iteration_level,
            max_iterations=5,
            context_depth=context_depth,
            learning_path=conv_context["learning_path"][-10:]  # Últimos 10 temas
        )
    
    async def _get_iterative_questions(self, context: str, iteration_level: int, conv_context: Dict) -> List[Question]:
        """Obtiene preguntas específicas para la fase de iteración actual con sistema de 5 fases elaborado."""
        context_lower = context.lower()
        
        # Filtrar preguntas ya utilizadas en esta conversación
        used_questions = set(conv_context.get("last_questions", []))
        
        if iteration_level == 1:
            # FASE 1: Descubrimiento y Establecimiento de Contexto
            # Objetivo: Entender la pregunta inicial y establecer conocimiento base
            questions = self._generate_phase_1_questions(context, used_questions)
        elif iteration_level == 2:
            # FASE 2: Exploración y Construcción de Fundamentos
            # Objetivo: Explorar amplitud del tema y construir entendimiento fundamental
            questions = await self._generate_phase_2_questions(context, used_questions, conv_context)
        elif iteration_level == 3:
            # FASE 3: Análisis Profundo y Complejidades
            # Objetivo: Profundizar en aspectos específicos, analizar complejidades
            questions = await self._generate_phase_3_questions(context, used_questions, conv_context)
        elif iteration_level == 4:
            # FASE 4: Aplicación y Síntesis
            # Objetivo: Aplicar conocimiento a escenarios reales, sintetizar aprendizajes
            questions = await self._generate_phase_4_questions(context, used_questions, conv_context)
        else:  # iteration_level == 5
            # FASE 5: Maestría y Exploración Futura
            # Objetivo: Lograr entendimiento de maestría, explorar temas avanzados
            questions = self._generate_phase_5_questions(context, used_questions, conv_context)
        
        # Limitar número de preguntas por fase (más preguntas en fases iniciales)
        max_questions = [4, 6, 6, 6, 2][iteration_level - 1]
        return questions[:max_questions]
    
    async def _extract_topics_from_questions(self, questions: List[Question]) -> List[str]:
        """Extrae temas principales usando análisis semántico LLM.
        
        Reemplaza la lógica heurística de stop words con análisis semántico.
        """
        try:
            # Combinar textos de preguntas para análisis
            question_texts = [q.text for q in questions]
            llm_resp = await self.llm_service.extract_keywords_intelligently(
                text=" ".join(question_texts),
                context="",
                purpose="topics_from_questions",
            )
            if llm_resp and llm_resp.success and llm_resp.data:
                return llm_resp.data.get('keywords', [])
            return []
        except Exception as e:
            print(f"Error en extracción semántica de temas: {e}")
            # Fallback simple: usar categorías de preguntas
            return [q.category.value for q in questions]
    
    def _generate_dynamic_questions(self, context: str, iteration_level: int) -> List[Question]:
        """Genera preguntas dinámicas basadas en el contexto cuando no hay preguntas predefinidas."""
        # Plantillas de preguntas dinámicas basadas en el nivel de iteración
        templates = {
            3: [
                "¿Podrías profundizar más en los aspectos técnicos?",
                "¿Qué ejemplos prácticos podrías proporcionar?",
                "¿Cuáles son las mejores prácticas en este tema?"
            ],
            4: [
                "¿Qué desafíos comunes se presentan en este área?",
                "¿Cómo se relaciona esto con otros conceptos?",
                "¿Qué herramientas o recursos recomendarías?"
            ],
            5: [
                "¿Podrías explicar casos de uso avanzados?",
                "¿Qué tendencias futuras ves en este campo?",
                "¿Cómo evaluarías el progreso en este aprendizaje?"
            ]
        }
        
        questions = []
        question_texts = templates.get(iteration_level, templates[5])
        
        for i, text in enumerate(question_texts):
            question = Question(
                id=f"dynamic_{iteration_level}_{i}",
                text=text,
                category=QuestionCategory.FOLLOWUP if iteration_level <= 4 else QuestionCategory.SUMMARY,
                priority=7 + iteration_level,
                is_active=True,
                trigger_type=QuestionTrigger.KEYWORD,
                context_keywords=[]  # Eliminado: ahora usa análisis semántico LLM
            )
            questions.append(question)
        
        return questions
    
    def _generate_phase_1_questions(self, context: str, used_questions: set) -> List[Question]:
        """FASE 1: Descubrimiento y Establecimiento de Contexto"""
        templates = [
            "¿Qué aspecto específico de este tema te interesa más?",
            "¿Cuál es tu experiencia previa con este tema?",
            "¿Qué te gustaría lograr o entender mejor?",
            "¿Hay algún contexto particular en el que planeas aplicar esto?"
        ]
        return self._create_dynamic_questions_from_templates(templates, 1, used_questions, QuestionCategory.EXPLORATION)
    
    async def _generate_phase_2_questions(self, context: str, used_questions: set, conv_context: Dict) -> List[Question]:
        """FASE 2: Exploración y Construcción de Fundamentos"""
        # Extraer temas específicos del contexto
        specific_topics = await self._extract_specific_topics(context, conv_context)
        
        if specific_topics:
            # Generar preguntas específicas basadas en los temas detectados
            templates = [
                 f"¿Podrías explicar los conceptos fundamentales de {specific_topics[0]}?",
                 f"¿Cuáles son los componentes principales de {specific_topics[0]} que debo entender?",
                 f"¿Qué ejemplos prácticos de {specific_topics[0]} me ayudarían a comprender mejor?",
                 f"¿Cómo se relaciona {specific_topics[0]} con otros conceptos similares?",
                 f"¿Cuáles son las bases teóricas de {specific_topics[0]} que debo conocer?",
                 f"¿Qué herramientas o recursos son esenciales para trabajar con {specific_topics[0]}?",
                 f"¿Cuáles son los prerrequisitos para entender {specific_topics[0]}?"
             ]
            # Aplanar la lista de templates
            flattened_templates = []
            for item in templates:
                if isinstance(item, list):
                    flattened_templates.extend(item)
                else:
                    flattened_templates.append(item)
            templates = flattened_templates
        else:
            # Plantillas genéricas si no se detectan temas específicos
             templates = [
                 "¿Te gustaría explorar los principios fundamentales de este tema?",
                 "¿Cómo se relaciona esto con tus conocimientos actuales?",
                 "¿Qué conceptos básicos deberíamos establecer primero?",
                 "¿Hay términos o conceptos que necesitas que clarifique?",
                 "¿Qué ejemplos prácticos te ayudarían a entender mejor?",
                 "¿Cuáles son las aplicaciones más comunes de este tema?"
             ]
        
        return self._create_dynamic_questions_from_templates(templates[:6], 2, used_questions, QuestionCategory.CLARIFICATION)
    
    async def _generate_phase_3_questions(self, context: str, used_questions: set, conv_context: Dict) -> List[Question]:
        """FASE 3: Análisis Profundo y Complejidades"""
        # Extraer temas específicos del contexto
        specific_topics = await self._extract_specific_topics(context, conv_context)
        
        if specific_topics:
            # Generar preguntas específicas y técnicas basadas en los temas detectados
             templates = [
                 f"¿Qué desafíos o complejidades podrían surgir al implementar {specific_topics[0]}?",
                 f"¿Te gustaría analizar diferentes enfoques o metodologías para {specific_topics[0]}?",
                 f"¿Qué aspectos técnicos específicos de {specific_topics[0]} deberíamos profundizar?",
                 f"¿Cómo compararías las ventajas y desventajas de diferentes opciones en {specific_topics[0]}?",
                 f"¿Cuáles son las mejores prácticas para optimizar {specific_topics[0]}?",
                 f"¿Qué errores comunes se deben evitar al trabajar con {specific_topics[0]}?",
                 f"¿Cómo se evalúa el rendimiento o eficiencia en {specific_topics[0]}?"
             ]
        else:
            # Plantillas genéricas si no se detectan temas específicos
             templates = [
                 "¿Qué desafíos o complejidades podrían surgir en la implementación?",
                 "¿Te gustaría analizar diferentes enfoques o metodologías?",
                 "¿Qué aspectos técnicos específicos deberíamos profundizar?",
                 "¿Cómo compararías las ventajas y desventajas de diferentes opciones?",
                 "¿Cuáles son las mejores prácticas en este campo?",
                 "¿Qué errores comunes se deben evitar?"
             ]
        
        return self._create_dynamic_questions_from_templates(templates[:6], 3, used_questions, QuestionCategory.TECHNICAL)
    
    async def _generate_phase_4_questions(self, context: str, used_questions: set, conv_context: Dict) -> List[Question]:
        """FASE 4: Aplicación y Síntesis"""
        # Extraer temas específicos del contexto
        specific_topics = await self._extract_specific_topics(context, conv_context)
        
        if specific_topics:
            # Generar preguntas específicas de aplicación basadas en los temas detectados
             templates = [
                 f"¿Cómo aplicarías {specific_topics[0]} en un proyecto real o situación práctica?",
                 f"¿Qué pasos concretos seguirías para implementar {specific_topics[0]}?",
                 f"¿Cómo integrarías {specific_topics[0]} con tus conocimientos o herramientas existentes?",
                 f"¿Qué recursos o herramientas adicionales serían útiles para trabajar con {specific_topics[0]}?",
                 f"¿Podrías crear un ejemplo práctico usando {specific_topics[0]}?",
                 f"¿Qué casos de uso reales son más comunes para {specific_topics[0]}?",
                 f"¿Cómo medirías el éxito al implementar {specific_topics[0]}?"
             ]
        else:
            # Plantillas genéricas si no se detectan temas específicos
             templates = [
                 "¿Cómo aplicarías esto en un proyecto real o situación práctica?",
                 "¿Qué pasos concretos seguirías para implementar lo que hemos discutido?",
                 "¿Cómo integrarías esto con tus conocimientos o herramientas existentes?",
                 "¿Qué recursos o herramientas adicionales podrían ser útiles?",
                 "¿Podrías crear un ejemplo práctico de implementación?",
                 "¿Qué casos de uso reales son más relevantes?"
             ]
        
        return self._create_dynamic_questions_from_templates(templates[:6], 4, used_questions, QuestionCategory.FOLLOWUP)
    
    def _generate_phase_5_questions(self, context: str, used_questions: set, conv_context: Dict) -> List[Question]:
        """FASE 5: Maestría y Exploración Futura"""
        templates = [
            "¿Qué técnicas avanzadas o casos de uso especializados te interesarían?",
            "¿Cómo explicarías este concepto a alguien que está empezando?",
            "¿Qué tendencias futuras o desarrollos ves en este campo?",
            "¿Qué otros temas relacionados te gustaría explorar a continuación?"
        ]
        return self._create_dynamic_questions_from_templates(templates, 5, used_questions, QuestionCategory.SUMMARY)
    
    async def _extract_specific_topics(self, context: str, conv_context: Dict) -> List[str]:
        """Extrae temas específicos usando análisis semántico LLM.
        
        Reemplaza la lógica heurística de keywords hardcodeados con análisis semántico.
        """
        try:
            # Incluir historial de conversación si está disponible
            full_context = context
            if 'chat_history' in conv_context:
                history_text = ' '.join(conv_context['chat_history'][-3:])  # Últimos 3 mensajes
                full_context = f"{history_text} {context}"
            
            llm_resp = await self.llm_service.extract_keywords_intelligently(
                text=full_context,
                context="",
                purpose="specific_topics"
            )
            if llm_resp and llm_resp.success and llm_resp.data:
                return llm_resp.data.get('keywords', [])
            return []
        except Exception as e:
            print(f"Error en extracción semántica de temas específicos: {e}")
            # Fallback: extraer palabras simples del contexto
            words = context.split()
            return [word for word in words if len(word) > 4][:3]
    
    def _create_dynamic_questions_from_templates(self, templates: List[str], phase: int, used_questions: set, category: QuestionCategory) -> List[Question]:
        """Crea preguntas dinámicas a partir de plantillas para una fase específica"""
        questions = []
        for i, template in enumerate(templates):
            if template not in used_questions:
                question = Question(
                    id=f"phase_{phase}_dynamic_{i}",
                    text=template,
                    category=category,
                    priority=5 + phase,
                    is_active=True,
                    trigger_type=QuestionTrigger.KEYWORD,
                    context_keywords=[]  # Eliminado: ahora usa análisis semántico LLM
                )
                questions.append(question)
        return questions
    
    def reset_conversation_context(self, conversation_id: str = "default") -> None:
        """Reinicia el contexto de una conversación específica."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
    
    def get_conversation_progress(self, conversation_id: str = "default") -> Dict:
        """Obtiene el progreso de aprendizaje de una conversación."""
        if conversation_id not in self.conversation_contexts:
            return {"iteration_level": 0, "topics_covered": [], "context_depth": "none"}
        
        conv_context = self.conversation_contexts[conversation_id]
        return {
            "iteration_level": conv_context["iteration_level"],
            "topics_covered": list(conv_context["topics_covered"]),
            "context_depth": conv_context["context_depth"],
            "learning_path": conv_context["learning_path"]
        }
    
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