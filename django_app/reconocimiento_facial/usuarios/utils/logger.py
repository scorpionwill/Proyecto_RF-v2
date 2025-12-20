"""
-----------------------------------------------------------------------------
Archivo: logger.py
Descripcion: Utilidades de logging centralizado para el sistema.
             Proporciona metodos para registrar mensajes informativos,
             de exito, advertencia, error, y mensajes especificos para
             camara, red, reconocimiento y almacenamiento.
Fecha de creacion: 05 de Diciembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
from typing import Optional
from .. import config


class Logger:
    """Logger centralizado para operaciones de reconocimiento facial."""
    
    @staticmethod
    def info(message: str, emoji: str = "ℹ️"):
        """Registra mensaje informativo."""
        if config.LOG_EMOJI_ENABLED:
            print(f"{emoji} {message}")
        else:
            print(f"[INFO] {message}")
    
    @staticmethod
    def success(message: str):
        """Registra mensaje de éxito."""
        Logger.info(message, "✅")
    
    @staticmethod
    def warning(message: str):
        """Registra mensaje de advertencia."""
        Logger.info(message, "⚠️")
    
    @staticmethod
    def error(message: str):
        """Registra mensaje de error."""
        Logger.info(message, "❌")
    
    @staticmethod
    def debug(message: str):
        """Registra mensaje de depuración."""
        Logger.info(message, "🔍")
    
    @staticmethod
    def camera(message: str):
        """Registra mensaje relacionado con cámara."""
        Logger.info(message, "📸")
    
    @staticmethod
    def network(message: str):
        """Registra mensaje relacionado con red."""
        Logger.info(message, "🔌")
    
    @staticmethod
    def recognition(message: str):
        """Registra mensaje relacionado con reconocimiento."""
        Logger.info(message, "👤")
    
    @staticmethod
    def matching(message: str):
        """Registra mensaje relacionado con matching."""
        if config.LOG_VERBOSE_MATCHING:
            Logger.info(message, "🔍")
    
    @staticmethod
    def storage(message: str):
        """Registra mensaje relacionado con almacenamiento."""
        Logger.info(message, "💾")


# Instancia global del logger
logger = Logger()
