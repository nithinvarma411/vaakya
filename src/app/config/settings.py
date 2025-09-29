"""
Comprehensive Configuration Settings for Vaakya Voice Assistant

This module contains all configuration constants that were previously hardcoded
throughout the application. It provides a centralized location for managing
application settings.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, ClassVar, Dict, List


class AudioSettings:
    """Audio processing and transcription settings."""

    # Audio format settings
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    SAMPLE_WIDTH: int = 2

    # File format settings
    TEMP_AUDIO_SUFFIX: str = ".wav"
    SUPPORTED_FORMATS: ClassVar[List[str]] = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]

    # Transcription settings
    DEFAULT_BEAM_SIZE: int = 5
    DEFAULT_LANGUAGE: str = "auto"
    TRANSCRIPTION_TIMEOUT: float = 120.0  # 2 minutes


class ModelSettings:
    """AI Model configuration settings."""

    # Default model settings
    DEFAULT_MODEL_NAME: str = "qwen2.5-1.5b-instruct"
    DEFAULT_DEVICE: str = "cpu"
    DEFAULT_COMPUTE_TYPE: str = "int8"

    # Context and processing settings
    MAX_CONTEXT_SIZE: int = 8192  # Increased for better conversation handling

    # Whisper model settings
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    # Model download settings
    MODELS_DIR_NAME: str = "models"
    MODEL_INFO: ClassVar[Dict[str, Dict[str, Any]]] = {
        "qwen2.5-1.5b-instruct": {
            "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "size_mb": 950,
        }
    }


class APISettings:
    """API server configuration settings."""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    TITLE: str = "Speech Transcription API"
    VERSION: str = "1.0.0"

    # CORS settings
    CORS_ORIGINS: ClassVar[List[str]] = ["*"]  # In production, specify exact origins
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: ClassVar[List[str]] = ["*"]
    CORS_HEADERS: ClassVar[List[str]] = ["*"]

    # Timeout settings
    REQUEST_TIMEOUT: float = 300.0  # 5 minutes
    TRANSCRIPTION_TIMEOUT: float = 120.0  # 2 minutes


class AppOperationsSettings:
    """Application operations configuration."""

    # App discovery and launching
    MAX_APPS_LIMIT: int = 50
    FUZZY_THRESHOLD: int = 40  # Lower threshold for better cross-platform compatibility
    COMMAND_TIMEOUT: int = 10

    # Platform-specific settings
    SEARCH_TIMEOUT: float = 5.0
    APP_LAUNCH_TIMEOUT: float = 15.0

    # Linux executable filtering
    SKIP_EXECUTABLES: ClassVar[List[str]] = [
        "systemd",
        "dbus",
        "update",
        "install",
        "config",
    ]

    # Fuzzy search scoring constants
    SHORT_APP_NAME_THRESHOLD: int = 6
    MIN_WORD_LENGTH_FOR_PARTIAL_MATCH: int = 3
    FUZZY_MATCH_THRESHOLD: int = 70
    BONUS_APP_NAME_LENGTH: int = 15
    PENALTY_APP_NAME_LENGTH: int = 30


class WebOperationsSettings:
    """Web search operations configuration."""

    # Search result formatting
    SNIPPET_LENGTH: int = 200
    QUICK_ANSWER_LENGTH: int = 300

    # Search limits
    DEFAULT_MAX_RESULTS: int = 5
    MAX_SEARCH_RESULTS: int = 20

    # Search timeouts
    SEARCH_TIMEOUT: float = 10.0
    REQUEST_TIMEOUT: float = 30.0


class FileOperationsSettings:
    """File operations configuration."""

    # File operation settings
    DEFAULT_ENCODING: str = "utf-8"
    BACKUP_ENABLED: bool = False

    # Size limits
    MAX_FILE_SIZE_MB: int = 100
    MAX_DIRECTORY_DEPTH: int = 10

    # Temporary file settings
    TEMP_DIR_PREFIX: str = "vaakya_"
    AUTO_CLEANUP: bool = True


class SecuritySettings:
    """Security and safety configuration."""

    # File access restrictions
    ALLOWED_FILE_EXTENSIONS: ClassVar[List[str]] = [
        ".txt",
        ".md",
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg",
    ]

    # Path restrictions
    RESTRICTED_PATHS: ClassVar[List[str]] = [
        "/etc",
        "/sys",
        "/proc",
        "/dev",
        "/root",
        "C:\\Windows\\System32",
        "C:\\Program Files",
    ]

    # Command restrictions
    ALLOWED_COMMANDS: ClassVar[List[str]] = [
        "open",
        "start",
        "launch",
        "calculator",
        "notepad",
        "browser",
    ]


class LoggingSettings:
    """Logging configuration."""

    # Log levels
    DEFAULT_LOG_LEVEL: str = "INFO"
    FILE_LOG_LEVEL: str = "DEBUG"

    # Log formatting
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Log file settings
    LOG_DIR: str = "logs"
    MAX_LOG_SIZE_MB: int = 10
    BACKUP_COUNT: int = 5


class DevelopmentSettings:
    """Development and debugging settings."""

    # Environment detection
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    DEVELOPMENT: bool = os.getenv("ENVIRONMENT", "production") == "development"

    # Testing settings
    TEST_DATA_DIR: str = "test_data"
    MOCK_EXTERNAL_SERVICES: bool = False

    # Performance settings
    ENABLE_PROFILING: bool = False
    CACHE_ENABLED: bool = True


class Settings:
    """Main settings class that aggregates all configuration."""

    def __init__(self) -> None:
        # Initialize all setting categories
        self.audio = AudioSettings()
        self.model = ModelSettings()
        self.api = APISettings()
        self.app_operations = AppOperationsSettings()
        self.web_operations = WebOperationsSettings()
        self.file_operations = FileOperationsSettings()
        self.security = SecuritySettings()
        self.logging = LoggingSettings()
        self.development = DevelopmentSettings()

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent.parent

    @property
    def models_dir(self) -> Path:
        """Get the models directory."""
        return self.project_root / self.model.MODELS_DIR_NAME

    @property
    def logs_dir(self) -> Path:
        """Get the logs directory."""
        return self.project_root / self.logging.LOG_DIR

    def get_temp_dir(self) -> Path:
        """Get or create temporary directory."""
        temp_dir = Path(tempfile.gettempdir()) / "vaakya_"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir


# Global settings instance
settings = Settings()

# Backward compatibility - keep the old interface working
DEFAULT_BEAM_SIZE = settings.audio.DEFAULT_BEAM_SIZE
DEFAULT_LANGUAGE = settings.audio.DEFAULT_LANGUAGE
AUDIO_SAMPLE_RATE = settings.audio.SAMPLE_RATE
AUDIO_CHANNELS = settings.audio.CHANNELS
AUDIO_SAMPLE_WIDTH = settings.audio.SAMPLE_WIDTH
