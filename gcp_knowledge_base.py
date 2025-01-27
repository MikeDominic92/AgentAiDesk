from typing import List, Dict, Optional
from datetime import datetime
from google.cloud import firestore, storage, translate_v2 as translate
import json
import logging
from google.cloud import logging as cloud_logging

class GCPKnowledgeBase:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.db = firestore.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        self.translate_client = translate.Client()
        
        # Setup Cloud Logging
        logging_client = cloud_logging.Client()
        logging_client.setup_logging()
        self.logger = logging.getLogger(__name__)

    def _create_bucket_if_not_exists(self, bucket_name: str):
        """Create a new bucket if it doesn't exist"""
        try:
            bucket = self.storage_client.get_bucket(bucket_name)
        except Exception:
            bucket = self.storage_client.create_bucket(bucket_name)
        return bucket

    async def add_article(self, title: str, content: str, category: str, tags: List[str]) -> Dict:
        """Add a new article to Firestore"""
        try:
            doc_ref = self.db.collection('articles').document()
            article = {
                "id": doc_ref.id,
                "title": title,
                "content": content,
                "category": category,
                "tags": tags,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            doc_ref.set(article)
            self.logger.info(f"Added new article: {title}")
            return article
        except Exception as e:
            self.logger.error(f"Error adding article: {str(e)}")
            raise

    async def search_articles(self, query: str, language: str = 'en') -> List[Dict]:
        """Search articles with language support"""
        try:
            # Translate query if not in English
            if language != 'en':
                translation = self.translate_client.translate(
                    query,
                    target_language='en',
                    source_language=language
                )
                query = translation['translatedText']

            results = []
            # Search in title
            title_docs = self.db.collection('articles').where('title', '>=', query).where(
                'title', '<=', query + '\uf8ff').stream()
            
            # Search in content
            content_docs = self.db.collection('articles').where('content', '>=', query).where(
                'content', '<=', query + '\uf8ff').stream()
            
            # Search in tags
            tag_docs = self.db.collection('articles').where('tags', 'array_contains', query).stream()
            
            # Combine results
            seen_ids = set()
            for doc in [*title_docs, *content_docs, *tag_docs]:
                if doc.id not in seen_ids:
                    article = doc.to_dict()
                    
                    # Translate content if needed
                    if language != 'en':
                        article['title'] = self.translate_client.translate(
                            article['title'],
                            target_language=language,
                            source_language='en'
                        )['translatedText']
                        
                        article['content'] = self.translate_client.translate(
                            article['content'],
                            target_language=language,
                            source_language='en'
                        )['translatedText']
                    
                    results.append(article)
                    seen_ids.add(doc.id)
            
            self.logger.info(f"Search query: {query}, Results: {len(results)}")
            return results
        except Exception as e:
            self.logger.error(f"Error searching articles: {str(e)}")
            raise

    async def get_article_by_id(self, article_id: str, language: str = 'en') -> Optional[Dict]:
        """Get an article by ID with language support"""
        try:
            doc_ref = self.db.collection('articles').document(article_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            article = doc.to_dict()
            
            # Translate if needed
            if language != 'en':
                article['title'] = self.translate_client.translate(
                    article['title'],
                    target_language=language,
                    source_language='en'
                )['translatedText']
                
                article['content'] = self.translate_client.translate(
                    article['content'],
                    target_language=language,
                    source_language='en'
                )['translatedText']
            
            return article
        except Exception as e:
            self.logger.error(f"Error getting article: {str(e)}")
            raise

    async def update_article(self, article_id: str, title: str = None, content: str = None,
                           category: str = None, tags: List[str] = None) -> Optional[Dict]:
        """Update an existing article"""
        try:
            doc_ref = self.db.collection('articles').document(article_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            update_data = {}
            if title:
                update_data['title'] = title
            if content:
                update_data['content'] = content
            if category:
                update_data['category'] = category
            if tags:
                update_data['tags'] = tags
            
            update_data['updated_at'] = datetime.now()
            
            doc_ref.update(update_data)
            self.logger.info(f"Updated article: {article_id}")
            
            return doc_ref.get().to_dict()
        except Exception as e:
            self.logger.error(f"Error updating article: {str(e)}")
            raise

    async def delete_article(self, article_id: str) -> bool:
        """Delete an article"""
        try:
            doc_ref = self.db.collection('articles').document(article_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            doc_ref.delete()
            self.logger.info(f"Deleted article: {article_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting article: {str(e)}")
            raise

    async def get_categories(self) -> List[str]:
        """Get all categories"""
        try:
            categories_ref = self.db.collection('categories').document('list')
            doc = categories_ref.get()
            
            if not doc.exists:
                return []
                
            return doc.to_dict().get('categories', [])
        except Exception as e:
            self.logger.error(f"Error getting categories: {str(e)}")
            raise

    async def add_category(self, category: str) -> bool:
        """Add a new category"""
        try:
            categories_ref = self.db.collection('categories').document('list')
            doc = categories_ref.get()
            
            if not doc.exists:
                categories_ref.set({'categories': [category]})
            else:
                current_categories = doc.to_dict().get('categories', [])
                if category not in current_categories:
                    current_categories.append(category)
                    categories_ref.update({'categories': current_categories})
                else:
                    return False
            
            self.logger.info(f"Added new category: {category}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding category: {str(e)}")
            raise

# Initialize with common IT support solutions
async def initialize_gcp_knowledge_base(kb: GCPKnowledgeBase):
    """Initialize the knowledge base with sample articles"""
    try:
        # Check if articles exist
        articles = await kb.search_articles("")
        if not articles:
            # Add initial categories
            categories = [
                "Password", "Network", "Hardware", "Software",
                "Email", "Security", "VPN", "Printer", "General"
            ]
            for category in categories:
                await kb.add_category(category)

            # Add sample articles
            await kb.add_article(
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

            await kb.add_article(
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

            await kb.add_article(
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

            await kb.add_article(
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
            
            kb.logger.info("Initialized knowledge base with sample articles")
    except Exception as e:
        kb.logger.error(f"Error initializing knowledge base: {str(e)}")
        raise
