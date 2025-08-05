from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets

class SecurityConfig(BaseSettings):
    """Configuración específica de seguridad"""
    
    # Configuración de encriptación
    master_password: str = "default_admin_key_2024"
    use_encrypted_keys: bool = True
    
    # Configuración de API Keys
    api_keys: List[str] = []
    require_api_key: bool = False
    
    # Configuración de rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests por ventana
    rate_limit_window: int = 3600   # ventana en segundos (1 hora)
    
    # Configuración de CORS
    allowed_origins: str = "*"
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True
    
    # Configuración de headers de seguridad
    security_headers_enabled: bool = True
    
    # Configuración de sesiones
    session_secret_key: Optional[str] = None
    session_max_age: int = 86400  # 24 horas
    
    # Configuración de validación
    max_prompt_length: int = 1000
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".txt", ".pdf", ".docx", ".md"]
    
    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Generar session_secret_key si no está configurada
        if not self.session_secret_key:
            self.session_secret_key = secrets.token_urlsafe(32)
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Lista de orígenes permitidos para CORS"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def is_api_key_valid(self, api_key: str) -> bool:
        """Valida una API key"""
        if not self.require_api_key:
            return True
        
        if not self.api_keys:
            return True  # Si no hay keys configuradas, permitir acceso
        
        return api_key in self.api_keys
    
    def get_security_headers(self) -> dict:
        """Obtiene headers de seguridad recomendados"""
        if not self.security_headers_enabled:
            return {}
        
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
    
    def validate_file_upload(self, filename: str, file_size: int) -> tuple[bool, str]:
        """Valida un archivo subido"""
        # Validar tamaño
        if file_size > self.max_file_size:
            return False, f"Archivo demasiado grande. Máximo: {self.max_file_size / (1024*1024):.1f}MB"
        
        # Validar extensión
        file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if file_ext not in self.allowed_file_types:
            return False, f"Tipo de archivo no permitido. Permitidos: {', '.join(self.allowed_file_types)}"
        
        return True, "Archivo válido"
    
    def validate_prompt_length(self, prompt: str) -> tuple[bool, str]:
        """Valida la longitud de un prompt"""
        if len(prompt) > self.max_prompt_length:
            return False, f"Prompt demasiado largo. Máximo: {self.max_prompt_length} caracteres"
        
        return True, "Prompt válido"