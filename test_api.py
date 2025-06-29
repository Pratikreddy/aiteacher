import requests
import json

# Test the teacher endpoint
test_data = {
    "input": {
        "topic": "Data Structures",
        "student_history": "Good at programming basics",
        "education_level": "Undergraduate Year 2",
        "department": "Computer Science",
        "teacher_instructions": "",
        "previous_responses": [
            {
                "question": "What is a linked list?",
                "answer": "A data structure with nodes",
                "score": 70
            }
        ]
    }
}

response = requests.post("http://localhost:8000/teacher/invoke", json=test_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Response:", json.dumps(response.json(), indent=2))
else:
    print("Error:", response.text)