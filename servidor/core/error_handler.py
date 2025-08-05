import logging
import traceback
from typing import Dict, Any, Optional, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncio

logger = logging.getLogger(__name__)

class ApplicationError(Exception):
    """Excepción base para errores de la aplicación"""
    def __init__(self, message: str, error_code: str = "APP_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ApplicationError):
    """Error de validación de datos"""
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field

class ExternalServiceError(ApplicationError):
    """Error en servicios externos (APIs, etc.) - Azure removed"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{service}: {message}", "EXTERNAL_SERVICE_ERROR", details)
        self.service = service

class RAGError(ApplicationError):
    """Error en el sistema RAG"""
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RAG_ERROR", details)
        self.operation = operation

class ConfigurationError(ApplicationError):
    """Error de configuración"""
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)
        self.config_key = config_key

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    @staticmethod
    def format_error_response(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> Dict[str, Any]:
        """Formatea una respuesta de error estándar"""
        response = {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response
    
    @staticmethod
    def log_error(
        error: Exception,
        request: Optional[Request] = None,
        extra_context: Optional[Dict[str, Any]] = None
    ):
        """Registra un error con contexto adicional"""
        context = {
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if request:
            context.update({
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            })
        
        if extra_context:
            context.update(extra_context)
        
        if isinstance(error, ApplicationError):
            context["error_code"] = error.error_code
            context["error_details"] = error.details
        
        # Log con nivel apropiado según el tipo de error
        if isinstance(error, (ValidationError, HTTPException)):
            logger.warning(f"Error de validación: {error}", extra=context)
        elif isinstance(error, ExternalServiceError):
            logger.error(f"Error en servicio externo: {error}", extra=context)
        elif isinstance(error, ConfigurationError):
            logger.critical(f"Error de configuración: {error}", extra=context)
        else:
            logger.error(f"Error no manejado: {error}", extra=context, exc_info=True)

# Manejadores de excepciones para FastAPI

async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    """Manejador para errores de aplicación personalizados"""
    ErrorHandler.log_error(exc, request)
    
    status_code = 400 if isinstance(exc, ValidationError) else 500
    if isinstance(exc, ExternalServiceError):
        status_code = 503  # Service Unavailable
    elif isinstance(exc, ConfigurationError):
        status_code = 500  # Internal Server Error
    
    response = ErrorHandler.format_error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=status_code
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador para excepciones HTTP estándar"""
    ErrorHandler.log_error(exc, request)
    
    response = ErrorHandler.format_error_response(
        error_code="HTTP_ERROR",
        message=exc.detail,
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Manejador para errores de validación de Pydantic"""
    ErrorHandler.log_error(exc, request)
    
    # Formatear errores de validación de manera más amigable
    validation_errors = []
    for error in exc.errors():
        validation_errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    response = ErrorHandler.format_error_response(
        error_code="VALIDATION_ERROR",
        message="Error de validación en los datos enviados",
        details={"validation_errors": validation_errors},
        status_code=422
    )
    
    return JSONResponse(
        status_code=422,
        content=response
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador para excepciones no capturadas"""
    ErrorHandler.log_error(exc, request)
    
    # En producción, no exponer detalles internos
    response = ErrorHandler.format_error_response(
        error_code="INTERNAL_ERROR",
        message="Error interno del servidor",
        status_code=500
    )
    
    return JSONResponse(
        status_code=500,
        content=response
    )

# Decorador para manejo de errores en funciones
def handle_errors(operation_name: str = "unknown"):
    """Decorador para manejo automático de errores en funciones"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ApplicationError:
                raise  # Re-lanzar errores de aplicación
            except Exception as e:
                logger.error(f"Error en operación '{operation_name}': {e}", exc_info=True)
                raise ApplicationError(
                    f"Error en {operation_name}",
                    "OPERATION_ERROR",
                    {"operation": operation_name, "original_error": str(e)}
                )
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ApplicationError:
                raise  # Re-lanzar errores de aplicación
            except Exception as e:
                logger.error(f"Error en operación '{operation_name}': {e}", exc_info=True)
                raise ApplicationError(
                    f"Error en {operation_name}",
                    "OPERATION_ERROR",
                    {"operation": operation_name, "original_error": str(e)}
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Función para registrar todos los manejadores en FastAPI
def register_error_handlers(app):
    """Registra todos los manejadores de errores en la aplicación FastAPI"""
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)