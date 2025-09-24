# scripts/test_tutor_endpoints.py
"""
Test script for tutor endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_tutors():
    """Test the list tutors endpoint."""
    print("Testing list tutors endpoint...")
    response = requests.get(f"{BASE_URL}/tutor/")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        tutors = response.json()
        print(f"Found {len(tutors)} tutors:")
        for tutor in tutors:
            print(f"  - {tutor['name']} ({tutor['character_style']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_tutor():
    """Test the get tutor endpoint."""
    print("Testing get tutor endpoint...")
    tutor_id = "friendly_alice"
    response = requests.get(f"{BASE_URL}/tutor/{tutor_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        tutor = response.json()
        print(f"Tutor: {tutor['name']} ({tutor['character_style']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_select_tutor():
    """Test the select tutor endpoint."""
    print("Testing select tutor endpoint...")
    payload = {
        "user_id": "user123",
        "character_style": "friendly",
        "humor_level": "medium"
    }
    
    response = requests.post(
        f"{BASE_URL}/tutor/select",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Selected Tutor: {result['tutor']['name']}")
        print(f"Message: {result['message']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_user_tutor():
    """Test the get user tutor endpoint."""
    print("Testing get user tutor endpoint...")
    user_id = "user123"
    response = requests.get(f"{BASE_URL}/tutor/user/{user_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        tutor = response.json()
        print(f"User's Tutor: {tutor['name']} ({tutor['character_style']})")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("Testing Tutor Endpoints\n")
    
    try:
        test_list_tutors()
        test_get_tutor()
        test_select_tutor()
        test_get_user_tutor()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the service is running.")
    except Exception as e:
        print(f"Error: {e}")
