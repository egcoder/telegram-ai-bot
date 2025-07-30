"""Configuration management for Telegram AI Bot"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    ADMIN_USER_ID: str = os.getenv('ADMIN_USER_ID', '')
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    
    # AI Model Settings
    WHISPER_MODEL: str = os.getenv('WHISPER_MODEL', 'whisper-1')
    GPT_MODEL: str = os.getenv('GPT_MODEL', 'gpt-4')
    CLAUDE_MODEL: str = os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / 'data'
    LOGS_DIR: Path = BASE_DIR / 'logs'
    CONFIG_DIR: Path = BASE_DIR / 'config'
    
    # User Management
    AUTHORIZED_USERS_FILE: Path = DATA_DIR / 'authorized_users.json'
    
    # Audio Processing
    MAX_AUDIO_DURATION: int = 600  # 10 minutes in seconds
    SUPPORTED_LANGUAGES: list = ['ar', 'en', 'fr']
    
    # Calendar Settings
    CALENDAR_EVENT_DURATION: int = 30  # minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = [
            cls.TELEGRAM_BOT_TOKEN,
            cls.OPENAI_API_KEY,
            cls.ADMIN_USER_ID
        ]
        
        missing = [var for var in required if not var]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        
        return True
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.DATA_DIR, cls.LOGS_DIR, cls.CONFIG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)