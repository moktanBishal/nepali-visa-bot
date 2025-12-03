import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Meta (WhatsApp) Configuration
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "complex_verify_token_123")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Redis Configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application Settings
    MAX_HISTORY_LENGTH = 10  # Number of exchanges to keep
    
    # Rate Limiting (30 messages per hour)
    RATE_LIMIT_REQUESTS = 30 
    RATE_LIMIT_WINDOW = 3600   # 1 hour in seconds