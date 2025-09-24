#!/usr/bin/env python3
"""
Script to list available Gemini models.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Set the environment to use the development file
os.environ["ENV_FILE"] = ".env.development"

import google.generativeai as genai
from app.config import settings

def list_models():
    """List available Gemini models."""
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY is not set")
        return
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    print("Available models:")
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(f"- {model.name}")

if __name__ == "__main__":
    list_models()