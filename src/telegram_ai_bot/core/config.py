"""Configuration management for Telegram AI Bot"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    @classmethod 
    def _get_env(cls, key: str, default: str = '') -> str:
        """Get environment variable with Railway compatibility"""
        # Reload dotenv for Railway compatibility
        load_dotenv(override=True)
        return os.getenv(key, default)
    
    @property
    def TELEGRAM_BOT_TOKEN(self) -> str:
        return self._get_env('TELEGRAM_BOT_TOKEN')
    
    @property  
    def ADMIN_USER_ID(self) -> str:
        return self._get_env('ADMIN_USER_ID')
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return self._get_env('OPENAI_API_KEY')
    
    @property
    def ANTHROPIC_API_KEY(self) -> Optional[str]:
        return self._get_env('ANTHROPIC_API_KEY') or None
    
    @property
    def WHISPER_MODEL(self) -> str:
        return self._get_env('WHISPER_MODEL', 'whisper-1')
    
    @property
    def GPT_MODEL(self) -> str:
        return self._get_env('GPT_MODEL', 'gpt-4')
    
    @property
    def CLAUDE_MODEL(self) -> str:
        return self._get_env('CLAUDE_MODEL', 'claude-3-opus-20240229')
    
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
    
    def validate(self) -> bool:
        """Validate required configuration"""
        required = [
            self.TELEGRAM_BOT_TOKEN,
            self.OPENAI_API_KEY,
            self.ADMIN_USER_ID
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