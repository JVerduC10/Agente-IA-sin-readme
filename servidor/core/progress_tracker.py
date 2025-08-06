"""Sistema unificado de tracking de progreso con visualización mejorada."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class ProgressStatus(Enum):
    """Estados posibles del progreso."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class ProgressInfo:
    """Información detallada del progreso."""
    session_id: str
    status: ProgressStatus
    current: int = 0
    total: int = 0
    message: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def percentage(self) -> float:
        """Calcula el porcentaje completado."""
        if self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Tiempo transcurrido desde el inicio."""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Tiempo estimado restante."""
        if not self.start_time or self.current == 0 or self.total == 0:
            return None
        
        elapsed = self.elapsed_time
        if not elapsed:
            return None
            
        rate = self.current / elapsed.total_seconds()
        if rate <= 0:
            return None
            
        remaining_items = self.total - self.current
        remaining_seconds = remaining_items / rate
        return timedelta(seconds=remaining_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para API."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "current": self.current,
            "total": self.total,
            "percentage": self.percentage,
            "message": self.message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "elapsed_time": str(self.elapsed_time) if self.elapsed_time else None,
            "estimated_remaining": str(self.estimated_remaining) if self.estimated_remaining else None,
            "error": self.error,
            "metadata": self.metadata
        }


class ProgressTracker:
    """Tracker de progreso unificado con soporte para CLI y Web."""
    
    def __init__(self, session_id: str, total: int, description: str = "", use_tqdm: bool = True):
        self.session_id = session_id
        self.progress_info = ProgressInfo(
            session_id=session_id,
            status=ProgressStatus.PENDING,
            total=total,
            message=description
        )
        
        self.use_tqdm = use_tqdm and TQDM_AVAILABLE
        self.tqdm_bar: Optional[tqdm] = None
        self.callbacks: List[Callable[[ProgressInfo], None]] = []
        
        # Storage global para acceso desde API
        if not hasattr(ProgressTracker, '_global_progress'):
            ProgressTracker._global_progress = {}
        ProgressTracker._global_progress[session_id] = self.progress_info
    
    def add_callback(self, callback: Callable[[ProgressInfo], None]):
        """Añade callback para notificaciones de progreso."""
        self.callbacks.append(callback)
    
    def start(self):
        """Inicia el tracking de progreso."""
        self.progress_info.status = ProgressStatus.RUNNING
        self.progress_info.start_time = datetime.now()
        
        if self.use_tqdm:
            self.tqdm_bar = tqdm(
                total=self.progress_info.total,
                desc=self.progress_info.message,
                unit="item",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )
        
        self._notify_callbacks()
    
    def update(self, increment: int = 1, message: str = None, **metadata):
        """Actualiza el progreso."""
        self.progress_info.current += increment
        if message:
            self.progress_info.message = message
        if metadata:
            self.progress_info.metadata.update(metadata)
        
        if self.tqdm_bar:
            self.tqdm_bar.update(increment)
            if message:
                self.tqdm_bar.set_description(message)
        
        self._notify_callbacks()
    
    def set_progress(self, current: int, message: str = None, **metadata):
        """Establece el progreso absoluto."""
        old_current = self.progress_info.current
        self.progress_info.current = current
        if message:
            self.progress_info.message = message
        if metadata:
            self.progress_info.metadata.update(metadata)
        
        if self.tqdm_bar:
            increment = current - old_current
            self.tqdm_bar.update(increment)
            if message:
                self.tqdm_bar.set_description(message)
        
        self._notify_callbacks()
    
    def complete(self, message: str = "Completado"):
        """Marca como completado."""
        self.progress_info.status = ProgressStatus.COMPLETED
        self.progress_info.current = self.progress_info.total
        self.progress_info.message = message
        self.progress_info.end_time = datetime.now()
        
        if self.tqdm_bar:
            self.tqdm_bar.n = self.progress_info.total
            self.tqdm_bar.set_description(message)
            self.tqdm_bar.close()
        
        self._notify_callbacks()
    
    def error(self, error_message: str):
        """Marca como error."""
        self.progress_info.status = ProgressStatus.ERROR
        self.progress_info.error = error_message
        self.progress_info.message = f"Error: {error_message}"
        self.progress_info.end_time = datetime.now()
        
        if self.tqdm_bar:
            self.tqdm_bar.set_description(f"Error: {error_message}")
            self.tqdm_bar.close()
        
        self._notify_callbacks()
    
    def _notify_callbacks(self):
        """Notifica a todos los callbacks registrados."""
        for callback in self.callbacks:
            try:
                callback(self.progress_info)
            except Exception as e:
                print(f"Error en callback de progreso: {e}")
    
    @classmethod
    def get_progress(cls, session_id: str) -> Optional[ProgressInfo]:
        """Obtiene información de progreso por session_id."""
        if not hasattr(cls, '_global_progress'):
            return None
        return cls._global_progress.get(session_id)
    
    @classmethod
    def list_active_sessions(cls) -> List[str]:
        """Lista todas las sesiones activas."""
        if not hasattr(cls, '_global_progress'):
            return []
        return [
            session_id for session_id, info in cls._global_progress.items()
            if info.status in [ProgressStatus.PENDING, ProgressStatus.RUNNING]
        ]
    
    @classmethod
    def cleanup_completed(cls, max_age_hours: int = 24):
        """Limpia sesiones completadas antiguas."""
        if not hasattr(cls, '_global_progress'):
            return
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = []
        
        for session_id, info in cls._global_progress.items():
            if (info.status in [ProgressStatus.COMPLETED, ProgressStatus.ERROR, ProgressStatus.CANCELLED] 
                and info.end_time and info.end_time < cutoff_time):
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del cls._global_progress[session_id]


# Funciones de conveniencia para uso rápido
def create_progress_tracker(session_id: str, total: int, description: str = "", use_tqdm: bool = True) -> ProgressTracker:
    """Crea un nuevo tracker de progreso."""
    return ProgressTracker(session_id, total, description, use_tqdm)


def get_session_progress(session_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el progreso de una sesión como diccionario."""
    info = ProgressTracker.get_progress(session_id)
    return info.to_dict() if info else None