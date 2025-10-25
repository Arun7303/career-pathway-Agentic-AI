import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or 'AIzaSyCNUHTC85Rs5eryzP5hlFC3bcU0DTejm5s'  # Replace with new key soon!
    MODEL_NAME = 'gemini-2.0-flash'
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}