import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class KnowledgeBase:
    def __init__(self, file_path: str = "knowledge_base.json"):
        self.file_path = file_path
        self.kb: Dict = self._load_kb()

    def _load_kb(self) -> Dict:
        """Load the knowledge base from file or create a new one"""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {
            "articles": [],
            "categories": [
                "Password",
                "Network",
                "Hardware",
                "Software",
                "Email",
                "Security",
                "VPN",
                "Printer",
                "General"
            ]
        }

    def _save_kb(self) -> None:
        """Save the knowledge base to file"""
        with open(self.file_path, 'w') as f:
            json.dump(self.kb, f, indent=2)

    def add_article(self, title: str, content: str, category: str, tags: List[str]) -> Dict:
        """Add a new article to the knowledge base"""
        article = {
            "id": len(self.kb["articles"]) + 1,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.kb["articles"].append(article)
        self._save_kb()
        return article

    def search_articles(self, query: str) -> List[Dict]:
        """Search articles by title, content, or tags"""
        query = query.lower()
        results = []
        
        for article in self.kb["articles"]:
            # Check title
            if query in article["title"].lower():
                results.append(article)
                continue
                
            # Check content
            if query in article["content"].lower():
                results.append(article)
                continue
                
            # Check tags
            if any(query in tag.lower() for tag in article["tags"]):
                results.append(article)
                continue
        
        return results

    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """Get an article by its ID"""
        for article in self.kb["articles"]:
            if article["id"] == article_id:
                return article
        return None

    def update_article(self, article_id: int, title: str = None, content: str = None, 
                      category: str = None, tags: List[str] = None) -> Optional[Dict]:
        """Update an existing article"""
        article = self.get_article_by_id(article_id)
        if not article:
            return None

        if title:
            article["title"] = title
        if content:
            article["content"] = content
        if category:
            article["category"] = category
        if tags:
            article["tags"] = tags
            
        article["updated_at"] = datetime.now().isoformat()
        self._save_kb()
        return article

    def delete_article(self, article_id: int) -> bool:
        """Delete an article by its ID"""
        for i, article in enumerate(self.kb["articles"]):
            if article["id"] == article_id:
                self.kb["articles"].pop(i)
                self._save_kb()
                return True
        return False

    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return self.kb["categories"]

    def add_category(self, category: str) -> bool:
        """Add a new category"""
        if category not in self.kb["categories"]:
            self.kb["categories"].append(category)
            self._save_kb()
            return True
        return False

# Initialize with some common IT support solutions
def initialize_knowledge_base():
    kb = KnowledgeBase()
    
    # Add some initial articles if the knowledge base is empty
    if not kb.kb["articles"]:
        kb.add_article(
            "Password Reset Guide",
            """1. Visit the password reset portal at https://reset.company.com
2. Enter your username or email
3. Click 'Reset Password'
4. Check your email for reset instructions
5. Follow the link and create a new password
6. Make sure to use a strong password with at least 8 characters""",
            "Password",
            ["password", "reset", "security"]
        )
        
        kb.add_article(
            "VPN Connection Guide",
            """1. Download the VPN client from the company portal
2. Install the client and restart your computer
3. Launch the VPN client
4. Enter your username and password
5. Select the appropriate server
6. Click 'Connect'
7. Wait for the connection to be established""",
            "VPN",
            ["vpn", "network", "remote", "connection"]
        )
        
        kb.add_article(
            "Slow Computer Troubleshooting",
            """1. Check CPU and memory usage in Task Manager
2. Close unnecessary programs and browser tabs
3. Run disk cleanup to free up space
4. Check for and install Windows updates
5. Run a virus scan
6. Disable startup programs you don't need
7. Consider upgrading RAM or switching to SSD""",
            "Hardware",
            ["performance", "slow", "computer", "troubleshooting"]
        )
        
        kb.add_article(
            "Email Access Issues",
            """1. Verify internet connection
2. Check if you can access other websites
3. Clear browser cache and cookies
4. Try accessing email in a different browser
5. Check if email server is down
6. Verify your password is correct
7. Contact IT support if issues persist""",
            "Email",
            ["email", "outlook", "access", "login"]
        )

    return kb
