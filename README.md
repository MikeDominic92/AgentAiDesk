# AgentAiDesk - AI-Powered Help Desk Agent

## Overview
AgentAiDesk is an intelligent help desk support system built with FastAPI and deployed on Google Cloud Platform. It provides automated responses to user queries using AI, with support for multiple languages and a knowledge base integration.

## Live Deployment
- **API Endpoint**: https://help-desk-agent-962364780285.us-central1.run.app
- **Region**: us-central1
- **Platform**: Google Cloud Run

## Features
- AI-powered chat responses
- Multi-language support
- Knowledge base integration with Google Cloud Firestore
- File storage using Google Cloud Storage
- Authentication using API keys
- Health monitoring
- Scalable deployment on Cloud Run

## API Endpoints

### 1. Chat Endpoint
```http
POST /chat
Content-Type: application/json
X-API-Key: your-api-key

{
    "message": "Your question here",
    "language": "en"
}
```

### 2. Knowledge Base Endpoints
```http
GET /kb/articles?language=en
GET /kb/categories
```

### 3. Health Check
```http
GET /health
```

## Environment Variables
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `STORAGE_BUCKET`: Cloud Storage bucket name
- `API_KEY`: API key for authentication
- `DEEPSEEK_API_KEY`: DeepSeek API key for AI responses

## Tech Stack
- **Backend Framework**: FastAPI
- **Python Version**: 3.9
- **Database**: Google Cloud Firestore
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run
- **Container Registry**: Google Artifact Registry
- **Logging**: Google Cloud Logging

## Project Structure
```
help-desk-agent/
├── agent.py                # Main FastAPI application
├── gcp_knowledge_base.py   # Knowledge base implementation
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── service.yaml          # Cloud Run service configuration
├── cloudbuild.yaml       # Cloud Build configuration
└── test_endpoint.py      # API testing script
```

## GCP Services Used
- Cloud Run
- Cloud Firestore
- Cloud Storage
- Cloud Logging
- Cloud Build
- Artifact Registry
- Secret Manager
- IAM & Admin

## Deployment Configuration
The application is deployed using Cloud Run with the following specifications:
- Memory: 1Gi
- CPU: 1
- Scaling: 0-10 instances
- Authentication: Unauthenticated (API key required in headers)
- Service Account: agentaidesk-app@agentaidesk-2025.iam.gserviceaccount.com

## Local Development
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Run the application:
   ```bash
   uvicorn agent:app --host 0.0.0.0 --port 8080
   ```

## Testing
Run the test script to verify API functionality:
```bash
python test_endpoint.py
```

## Deployment Steps
1. Build and push the container:
   ```bash
   gcloud builds submit
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run services replace service.yaml --region us-central1 --platform managed
   ```

## Monitoring and Logging
- View logs in Google Cloud Console under Cloud Logging
- Monitor service health using the /health endpoint
- Set up Cloud Monitoring for metrics and alerts

## Security
- API key authentication required for all endpoints except /health
- Service account with minimal required permissions
- Secrets managed through environment variables
- CORS configuration for allowed origins

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
