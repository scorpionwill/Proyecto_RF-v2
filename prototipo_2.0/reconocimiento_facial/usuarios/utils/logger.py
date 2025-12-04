"""
Logging utilities for the face recognition system.
Provides consistent, formatted logging across the application.
"""
from typing import Optional
from .. import config


class Logger:
    """Centralized logger for face recognition operations."""
    
    @staticmethod
    def info(message: str, emoji: str = "ℹ️"):
        """Log info message."""
        if config.LOG_EMOJI_ENABLED:
            print(f"{emoji} {message}")
        else:
            print(f"[INFO] {message}")
    
    @staticmethod
    def success(message: str):
        """Log success message."""
        Logger.info(message, "✅")
    
    @staticmethod
    def warning(message: str):
        """Log warning message."""
        Logger.info(message, "⚠️")
    
    @staticmethod
    def error(message: str):
        """Log error message."""
        Logger.info(message, "❌")
    
    @staticmethod
    def debug(message: str):
        """Log debug message."""
        Logger.info(message, "🔍")
    
    @staticmethod
    def camera(message: str):
        """Log camera-related message."""
        Logger.info(message, "📸")
    
    @staticmethod
    def network(message: str):
        """Log network-related message."""
        Logger.info(message, "🔌")
    
    @staticmethod
    def recognition(message: str):
        """Log recognition-related message."""
        Logger.info(message, "👤")
    
    @staticmethod
    def matching(message: str):
        """Log matching-related message."""
        if config.LOG_VERBOSE_MATCHING:
            Logger.info(message, "🔍")
    
    @staticmethod
    def storage(message: str):
        """Log storage-related message."""
        Logger.info(message, "💾")


# Global logger instance
logger = Logger()
