#!/usr/bin/env python3
"""
Script to help set up Google Cloud credentials for BigQuery.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.append(str(Path(__file__).parent))

def setup_credentials_instructions():
    """Print instructions for setting up Google Cloud credentials."""
    print("Google Cloud Credentials Setup for BigQuery Analytics")
    print("=" * 55)
    print()
    
    print("There are several ways to authenticate with Google Cloud:")
    print()
    
    print("Option 1: Service Account Key File (Recommended for development)")
    print("  1. Go to Google Cloud Console > IAM & Admin > Service Accounts")
    print("  2. Create a new service account or select an existing one")
    print("  3. Grant the service account the 'BigQuery Data Editor' role")
    print("  4. Create a key and download the JSON file")
    print("  5. Set the path in your .env file:")
    print("     GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json")
    print()
    
    print("Option 2: Application Default Credentials (ADC)")
    print("  1. Install and initialize the Google Cloud SDK:")
    print("     https://cloud.google.com/sdk/docs/install")
    print("  2. Run: gcloud auth application-default login")
    print("  3. Authenticate with your Google account")
    print("  4. No need to set GOOGLE_APPLICATION_CREDENTIALS")
    print()
    
    print("Option 3: Environment Variables")
    print("  Set these environment variables instead of using a key file:")
    print("    GOOGLE_CLOUD_PROJECT=your-project-id")
    print("    BIGQUERY_DATASET_ID=learning_analytics")
    print()
    
    print("After setting up credentials, update your .env file accordingly.")

if __name__ == "__main__":
    setup_credentials_instructions()