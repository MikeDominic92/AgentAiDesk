# Help Desk Support Agent

This project implements a specialized help desk support agent using DeepSeek's API for handling technical support tickets from Tier 1 to Tier 3 level issues.

## Features

- Ticket analysis and categorization
- Automated response generation for various technical issues
- Support for multiple technical domains:
  - Cloud platforms (AWS, Azure, GCP)
  - Networking and Security
  - System Administration
  - Database Management
  - DevOps practices

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your DeepSeek API credentials:
```
DEEPSEEK_API_KEY=your_api_key_here
```

3. Run the application:
```bash
python agent.py
```

## Usage

The agent exposes a REST API endpoint at `http://localhost:8000/analyze_ticket`. You can send POST requests with ticket information:

```json
{
    "title": "Cannot access AWS EC2 instance",
    "description": "Unable to SSH into EC2 instance after security group update",
    "category": "cloud",
    "priority": "high",
    "tier_level": 2
}
```

## Integration

To integrate DeepSeek's API, you'll need to:

1. Sign up for a DeepSeek API account
2. Obtain your API key
3. Update the `analyze_ticket` function in `agent.py` with the actual API implementation

## Customization

You can extend the knowledge base categories in `agent.py` by updating the `CATEGORIES` dictionary with additional technical domains and keywords.
