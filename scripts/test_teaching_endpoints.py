# scripts/test_teaching_endpoints.py
\"\"\"
Test script for teaching endpoints.
\"\"\"

import requests
import json

BASE_URL = \"http://localhost:8000\"

def test_start_teaching_session():
    \"\"\"Test the start teaching session endpoint.\"\"\"
    print(\"Testing start teaching session endpoint...\")
    payload = {
        \"user_id\": \"user123\",
        \"subject\": \"Python Programming\",
        \"topic\": \"Variables and Data Types\",
        \"user_level\": \"newbie\"
    }
    
    response = requests.post(
        f\"{BASE_URL}/teaching/session/start\",
        headers={\"Content-Type\": \"application/json\"},
        data=json.dumps(payload)
    )
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        session_data = response.json()
        print(f\"Session ID: {session_data['session_id']}\")
        print(f\"Subject: {session_data['subject']}\")
        print(f\"Topic: {session_data['topic']}\")
        print(f\"Current Step: {session_data['current_step']}\")
        print(f\"Total Steps: {session_data['total_steps']}\")
        print(\"First Lesson Step:\")
        print(f\"  Title: {session_data['lesson_step']['title']}\")
        print(f\"  Content: {session_data['lesson_step']['content'][:100]}...\")
        return session_data['session_id']
    else:
        print(f\"Error: {response.text}\")
    print()
    return None

def test_deliver_lesson_step(session_id):
    \"\"\"Test the deliver lesson step endpoint.\"\"\"
    print(\"Testing deliver lesson step endpoint...\")
    payload = {
        \"session_id\": session_id,
        \"step_number\": 2
    }
    
    response = requests.post(
        f\"{BASE_URL}/teaching/lesson/step\",
        headers={\"Content-Type\": \"application/json\"},
        data=json.dumps(payload)
    )
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        lesson_step = response.json()
        print(f\"Step Number: {lesson_step['step_number']}\")
        print(f\"Title: {lesson_step['title']}\")
        print(f\"Content: {lesson_step['content'][:100]}...\")
    else:
        print(f\"Error: {response.text}\")
    print()

def test_generate_question(session_id):
    \"\"\"Test the generate question endpoint.\"\"\"
    print(\"Testing generate question endpoint...\")
    payload = {
        \"session_id\": session_id,
        \"concept\": \"variables\",
        \"question_type\": \"multiple_choice\"
    }
    
    response = requests.post(
        f\"{BASE_URL}/teaching/question/generate\",
        headers={\"Content-Type\": \"application/json\"},
        data=json.dumps(payload)
    )
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        question = response.json()
        print(f\"Question Type: {question['question_type']}\")
        print(f\"Question: {question['question']}\")
        print(\"Options:\")
        for i, option in enumerate(question['options']):
            print(f\"  {i+1}. {option}\")
        print(f\"Correct Answer: {question['correct_answer']}\")
        print(f\"Explanation: {question['explanation']}\")
    else:
        print(f\"Error: {response.text}\")
    print()

def test_advance_to_next_step(session_id):
    \"\"\"Test the advance to next step endpoint.\"\"\"
    print(\"Testing advance to next step endpoint...\")
    payload = {
        \"session_id\": session_id
    }
    
    response = requests.post(
        f\"{BASE_URL}/teaching/session/advance\",
        headers={\"Content-Type\": \"application/json\"},
        data=json.dumps(payload)
    )
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        result = response.json()
        print(f\"Status: {result['status']}\")
        if result['status'] == 'continuing':
            print(f\"Current Step: {result['current_step']}\")
            print(f\"Total Steps: {result['total_steps']}\")
            print(\"Lesson Step:\")
            print(f\"  Title: {result['lesson_step']['title']}\")
            print(f\"  Content: {result['lesson_step']['content'][:100]}...\")
        elif result['status'] == 'completed':
            print(result['message'])
    else:
        print(f\"Error: {response.text}\")
    print()

def test_get_session_progress(session_id):
    \"\"\"Test the get session progress endpoint.\"\"\"
    print(\"Testing get session progress endpoint...\")
    response = requests.get(f\"{BASE_URL}/teaching/session/{session_id}/progress\")
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        progress = response.json()
        print(f\"Session ID: {progress['session_id']}\")
        print(f\"Subject: {progress['subject']}\")
        print(f\"Topic: {progress['topic']}\")
        print(f\"Current Step: {progress['current_step']}\")
        print(f\"Total Steps: {progress['total_steps']}\")
        print(f\"Completed Steps: {progress['completed_steps']}\")
        print(f\"Progress Percentage: {progress['progress_percentage']}%\")
    else:
        print(f\"Error: {response.text}\")
    print()

def test_end_session(session_id):
    \"\"\"Test the end session endpoint.\"\"\"
    print(\"Testing end session endpoint...\")
    response = requests.post(f\"{BASE_URL}/teaching/session/{session_id}/end\")
    
    print(f\"Status Code: {response.status_code}\")
    if response.status_code == 200:
        summary = response.json()
        print(f\"Session ID: {summary['session_id']}\")
        print(f\"Status: {summary['status']}\")
        print(f\"Subject: {summary['subject']}\")
        print(f\"Topic: {summary['topic']}\")
        print(\"Progress Summary:\")
        print(f\"  Current Step: {summary['progress_summary']['current_step']}\")
        print(f\"  Total Steps: {summary['progress_summary']['total_steps']}\")
        print(f\"  Progress Percentage: {summary['progress_summary']['progress_percentage']}%\")
    else:
        print(f\"Error: {response.text}\")
    print()

if __name__ == \"__main__\":
    print(\"Testing Teaching Endpoints\\n\")
    
    try:
        # Test start teaching session
        session_id = test_start_teaching_session()
        
        if session_id:
            # Test deliver lesson step
            test_deliver_lesson_step(session_id)
            
            # Test generate question
            test_generate_question(session_id)
            
            # Test advance to next step
            test_advance_to_next_step(session_id)
            
            # Test get session progress
            test_get_session_progress(session_id)
            
            # Test end session
            test_end_session(session_id)
            
    except requests.exceptions.ConnectionError:
        print(\"Error: Could not connect to the server. Make sure the service is running.\")
    except Exception as e:
        print(f\"Error: {e}\")