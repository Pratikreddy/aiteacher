import requests
import json

# Test the second question generation with previous responses
test_data = {
    "input": {
        "topic": "Data Structures",
        "student_history": "Good at programming basics",
        "education_level": "UG Year 2",
        "department": "Computer Science and Engineering",
        "teacher_instructions": "",
        "previous_responses": [
            {
                "question": "What is a linked list?",
                "answer": "A linked list is a linear data structure where elements are stored in nodes",
                "score": 75
            }
        ]
    }
}

print("Testing second question generation...")
print("Request payload:")
print(json.dumps(test_data, indent=2))

# Test debug endpoint first
print("\n1. Testing debug endpoint...")
response = requests.post("http://localhost:8000/debug/teacher", json=test_data)
print(f"Debug Status: {response.status_code}")
print(f"Debug Response: {json.dumps(response.json(), indent=2)}")

# Test actual endpoint
print("\n2. Testing actual teacher endpoint...")
response = requests.post("http://localhost:8000/teacher/invoke", json=test_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Response:", json.dumps(response.json(), indent=2))
else:
    print("Error:", response.text)