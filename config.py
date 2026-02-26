import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') or 'Your_API_Key'  # Replace with new key soon!
    MODEL_NAME = 'gemini-2.0-flash' #change model accordingly to your need
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
