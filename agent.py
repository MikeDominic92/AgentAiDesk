import os
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from gcp_knowledge_base import GCPKnowledgeBase, initialize_gcp_knowledge_base
import logging
from google.cloud import logging as cloud_logging
from starlette.status import HTTP_403_FORBIDDEN
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Help Desk Agent API",
             description="AI-powered help desk support system with knowledge base integration",
             version="1.0.0")

# Initialize GCP services
project_id = os.getenv("GCP_PROJECT_ID")
kb = GCPKnowledgeBase(project_id)

# Setup Cloud Logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# API Key security
API_KEY = os.getenv("API_KEY", "sk-7c38538a7465446ba6a0bfe9da9d3565")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is required"
        )
    # Extract token from 'Bearer <token>'
    token = api_key_header.replace('Bearer ', '') if api_key_header.startswith('Bearer ') else api_key_header
    if token != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )
    return token

# Mount static files
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/chat")
async def chat():
    return FileResponse("frontend/chat.html")

class ChatMessage(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    knowledge_base_articles: List[Dict] = []

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    chat_message: ChatMessage,
    api_key: APIKey = Security(get_api_key)
):
    """
    Chat endpoint for direct communication with the AI agent
    """
    try:
        # Log incoming message
        logger.info(f"Received chat message: {chat_message.message}")
        
        # First, search the knowledge base
        kb_results = await kb.search_articles(chat_message.message, chat_message.language)
        logger.info(f"Found {len(kb_results)} relevant articles")
        
        # Prepare system message with knowledge base context
        system_message = "You are an expert IT support engineer. "
        if kb_results:
            system_message += "Here are some relevant articles from our knowledge base:\n\n"
            for article in kb_results[:2]:  # Include top 2 most relevant articles
                system_message += f"Article: {article['title']}\n"
                system_message += f"Content: {article['content']}\n\n"
        
        system_message += "Please provide a helpful response based on this information and your expertise."

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("DeepSeek API key not found")
            raise HTTPException(status_code=500, detail="DeepSeek API key not found")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": chat_message.message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            logger.info("Sending request to DeepSeek API...")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
        except requests.exceptions.RequestException as e:
            error_msg = "DeepSeek API is currently unavailable. Our service is experiencing temporary issues. Please try again later."
            logger.error(f"DeepSeek API connection error: {str(e)}")
            raise HTTPException(status_code=503, detail=error_msg)
            
        logger.info(f"Response status: {response.status_code}")
        if response.status_code != 200:
            error_detail = f"DeepSeek API error: {response.text}"
            logger.error(error_detail)
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
        response_data = response.json()
        logger.info(f"DeepSeek API response: {json.dumps(response_data)}")
        
        if "choices" not in response_data or not response_data["choices"]:
            logger.error("Invalid response format from DeepSeek API")
            raise HTTPException(status_code=500, detail="Invalid response format from DeepSeek API")
            
        assistant_response = response_data["choices"][0]["message"]["content"]
        logger.info(f"Generated response: {assistant_response}")
        
        return {
            "response": assistant_response,
            "knowledge_base_articles": kb_results[:2]  # Return top 2 relevant articles
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse API response: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/kb/articles")
async def get_kb_articles(
    language: str = Query("en", description="Language code (e.g., en, es, fr)"),
    api_key: APIKey = Security(get_api_key)
):
    """Get all knowledge base articles"""
    try:
        articles = await kb.search_articles("", language)
        return {"articles": articles}
    except Exception as e:
        logger.error(f"Error getting articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kb/categories")
async def get_kb_categories(api_key: APIKey = Security(get_api_key)):
    """Get all knowledge base categories"""
    try:
        categories = await kb.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test GCP services
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            raise ValueError("GCP_PROJECT_ID not set")
        
        return {"status": "healthy", "project_id": project_id}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize the knowledge base on startup"""
    try:
        await initialize_gcp_knowledge_base(kb)
        logger.info("Knowledge base initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing knowledge base: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
