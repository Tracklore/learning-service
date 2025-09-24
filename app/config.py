# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# In development, you can use .env.development by setting ENV_FILE=.env.development
env_file = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file)

class Settings:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model settings
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro-latest")
    
    # API Configuration
    GEMINI_API_TIMEOUT = int(os.getenv("GEMINI_API_TIMEOUT", "30"))
    
    # Safety settings
    GEMINI_SAFETY_THRESHOLD = os.getenv("GEMINI_SAFETY_THRESHOLD", "BLOCK_MEDIUM_AND_ABOVE")
    
    # BigQuery settings
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "learning_analytics")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

settings = Settings()