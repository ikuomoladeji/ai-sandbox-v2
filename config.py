"""
TPRM System Configuration
Centralized configuration management with environment variable support
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration for TPRM system"""

    # Ollama Configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL_DEFAULT = os.getenv("OLLAMA_MODEL", "llama3:latest")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # Available Models
    AVAILABLE_MODELS = [
        "llama3:latest",
        "mistral:latest",
        "qwen3-coder:30b",
    ]

    # Directory Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    HISTORY_DIR = BASE_DIR / "history"
    OUTPUTS_DIR = BASE_DIR / "outputs"
    LOGS_DIR = BASE_DIR / "logs"

    # File Paths
    VENDOR_DB_PATH = DATA_DIR / "vendors.json"

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "tprm_system.log"

    # Application Settings
    APP_NAME = "AI-Powered TPRM System"
    VERSION = "2.0.0"

    # Risk Scoring Configuration
    RISK_THRESHOLD_LOW = float(os.getenv("RISK_THRESHOLD_LOW", "4.0"))
    RISK_THRESHOLD_MEDIUM = float(os.getenv("RISK_THRESHOLD_MEDIUM", "3.0"))

    # Output Settings
    DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "excel")
    DEFAULT_AUDIENCE = os.getenv("DEFAULT_AUDIENCE", "internal")

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.HISTORY_DIR.mkdir(exist_ok=True)
        cls.OUTPUTS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []

        if not cls.OLLAMA_URL:
            errors.append("OLLAMA_URL is not configured")

        if cls.RISK_THRESHOLD_LOW <= cls.RISK_THRESHOLD_MEDIUM:
            errors.append("RISK_THRESHOLD_LOW must be greater than RISK_THRESHOLD_MEDIUM")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

# Initialize configuration on import
Config.ensure_directories()
