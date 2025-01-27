import os
from typing import Dict, List
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(title="AgentAiDesk", description="AI-powered Help Desk Support System")

class TicketRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    tier_level: int

class TicketResponse(BaseModel):
    solution: str
    steps: List[str]
    resources: List[str]

# Knowledge base categories
CATEGORIES = {
    "networking": ["VPN", "DNS", "TCP/IP", "Routing", "Firewall"],
    "cloud": ["AWS", "Azure", "GCP", "Kubernetes", "Docker"],
    "security": ["Authentication", "Authorization", "Encryption", "Compliance"],
    "system": ["Windows", "Linux", "MacOS", "Hardware", "Software"],
    "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
}

def get_deepseek_response(prompt: str) -> Dict:
    """
    Get response from DeepSeek API
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DeepSeek API key not found")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert IT support engineer specializing in technical support across all tiers (1-3) including cloud platforms, networking, security, and system administration."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

def analyze_ticket(ticket: TicketRequest) -> Dict:
    """
    Analyze the ticket using DeepSeek API to generate appropriate response
    """
    context = f"""
    Analyze and provide a solution for the following IT support ticket:

    Ticket Information:
    Title: {ticket.title}
    Description: {ticket.description}
    Category: {ticket.category}
    Priority: {ticket.priority}
    Tier Level: {ticket.tier_level}

    Please provide:
    1. A detailed solution
    2. Step-by-step instructions
    3. Relevant documentation or resource links

    Format the response as a JSON object with the following structure:
    {{
        "solution": "detailed explanation",
        "steps": ["step1", "step2", ...],
        "resources": ["resource1", "resource2", ...]
    }}
    """
    
    response = get_deepseek_response(context)
    
    try:
        # Parse the response as a dictionary
        import json
        parsed_response = json.loads(response)
        return parsed_response
    except json.JSONDecodeError:
        # Fallback response if JSON parsing fails
        return {
            "solution": response,
            "steps": ["Please contact support for detailed steps"],
            "resources": ["Documentation pending"]
        }

@app.post("/analyze_ticket", response_model=TicketResponse)
async def handle_ticket(ticket: TicketRequest):
    try:
        response = analyze_ticket(ticket)
        return TicketResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
