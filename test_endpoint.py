import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chat():
    url = "https://help-desk-agent-962364780285.us-central1.run.app/chat"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": os.getenv("API_KEY")
    }
    data = {
        "message": "What services do you offer?",
        "language": "en"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_chat()
