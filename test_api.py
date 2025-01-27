import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"Using API Key: {api_key[:8]}...")

headers = {
    "Authorization": f"Bearer {api_key}",  # Back to Bearer format
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",  # Updated model name
    "messages": [
        {
            "role": "system",
            "content": "You are an expert IT support engineer."
        },
        {
            "role": "user",
            "content": "What is your role?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 4000,
    "stream": False
}

print("\nSending request to DeepSeek API...")
try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Text: {response.text}")
    
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            print("\nSuccess! Response content:")
            print(response_data["choices"][0]["message"]["content"])
        else:
            print("\nError: Invalid response format")
    else:
        print(f"\nError: API returned status code {response.status_code}")
        
except Exception as e:
    print(f"\nError occurred: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
