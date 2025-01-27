import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"API Key: {api_key}")

url = "https://api.deepseek.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ]
}

try:
    print("\nSending request...")
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
