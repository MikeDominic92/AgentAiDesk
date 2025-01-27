import requests
import json
import time
from typing import List, Dict

def send_question(question: str) -> Dict:
    """Send a question to the agent and return the response"""
    url = "http://localhost:8000/chat"
    response = requests.post(url, json={"message": question})
    return response.json()

def print_qa(question: str, response: Dict):
    """Print the Q&A interaction in a formatted way"""
    print("\n" + "="*100)
    print("QUESTION:")
    print("-"*100)
    print(question)
    print("\nRESPONSE:")
    print("-"*100)
    print(response['response'].strip())
    print("="*100 + "\n")
    time.sleep(3)  # Add a small delay between questions

# List of test questions covering different domains
questions = [
    # Test 1: Cloud Computing
    "How do I optimize costs for my AWS EC2 instances?",
    
    # Test 2: Security
    "What steps should I take after detecting a potential security breach?",
    
    # Test 3: Database
    "Our MySQL database is running slow. How can we improve its performance?",
    
    # Test 4: System Administration
    "How do I troubleshoot high CPU usage on a Linux server?",
    
    # Test 5: DevOps
    "Explain how to set up monitoring for a Kubernetes cluster"
]

def main():
    print("\nStarting AI Help Desk Agent Testing Session")
    print("="*100)
    print(f"Total questions to test: {len(questions)}")
    print("="*100 + "\n")
    
    for i, question in enumerate(questions, 1):
        print(f"\nProcessing Question {i}/{len(questions)}...")
        try:
            response = send_question(question)
            print_qa(question, response)
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            continue

if __name__ == "__main__":
    main()
