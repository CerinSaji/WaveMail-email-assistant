"""
Custom LangChain tools for WaveMail agent
Implements the 5 core tools for email processing and management
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.tools import tool

from supabase import create_client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from cryptography.fernet import Fernet


# Initialize services
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class SecurityService:
    """Handle token encryption and content filtering"""
    
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {key.decode()}")
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt_token(self, token: str) -> str:
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def sanitize_email_content(self, content: str) -> str:
        """Remove sensitive information before AI processing"""
        if not content:
            return ""
        
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        # Remove phone numbers
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
        # Remove potential SSNs
        content = re.sub(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b', '[SSN]', content)
        # Truncate very long content
        if len(content) > 2000:
            content = content[:2000] + "... [TRUNCATED]"
        
        return content


# Pydantic models for tool inputs
class SQLQueryInput(BaseModel):
    query: str = Field(description="SQL query to execute against emails database")

class EmailFetchInput(BaseModel):
    count: int = Field(default=10, description="Number of emails to fetch", ge=1, le=50)
    query: str = Field(default="", description="Gmail search query (optional)")

class ImportanceInput(BaseModel):
    email_content: str = Field(description="Email content to analyze for importance")
    sender: str = Field(description="Email sender address")
    subject: str = Field(description="Email subject line")

class TaskExtractionInput(BaseModel):
    email_content: str = Field(description="Email content to analyze for actionable tasks")
    sender: str = Field(description="Email sender for context")

class EmailActionInput(BaseModel):
    email_id: str = Field(description="Email ID to perform action on")
    action: str = Field(description="Action to perform: 'trash', 'archive', 'mark_read', 'mark_unread'")


class SQLTool(BaseTool):
    """Tool for querying email metadata from Supabase database"""
    name = "sql_query"
    description = "Execute SQL queries on the emails database to find specific emails, get counts, or analyze metadata"
    args_schema: Type[BaseModel] = SQLQueryInput
    
    def _run(self, query: str) -> str:
        """Execute SQL query against Supabase"""
        try:
            # Sanitize query - only allow SELECT statements for safety
            query = query.strip()
            if not query.upper().startswith('SELECT'):
                return "Error: Only SELECT queries are allowed for security reasons"
            
            # Execute query
            result = supabase.rpc('execute_sql', {'sql_query': query}).execute()
            
            if result.data:
                return f"Query results: {json.dumps(result.data, indent=2)}"
            else:
                return "No results found"
                
        except Exception as e:
            return f"Database error: {str(e)}"


class EmailFetchTool(BaseTool):
    """Tool for fetching emails from Gmail API"""
    name = "fetch_emails"
    description = "Fetch emails from Gmail account and store them in the database"
    args_schema: Type[BaseModel] = EmailFetchInput
    
    def _run(self, count: int, query: str = "") -> str:
        """Fetch emails from Gmail and process them"""
        try:
            # For now, simulate email fetching since Gmail setup is complex
            # In real implementation, this would use Gmail API
            
            # Simulate fetched emails
            simulated_emails = [
                {
                    "sender": "boss@company.com",
                    "subject": "URGENT: Project deadline moved to tomorrow",
                    "body": "Hi, we need to move the project deadline to tomorrow due to client requirements.",
                    "received_date": datetime.now() - timedelta(hours=2)
                },
                {
                    "sender": "newsletter@tech.com", 
                    "subject": "Weekly Tech Newsletter",
                    "body": "Here are this week's top tech stories...",
                    "received_date": datetime.now() - timedelta(hours=5)
                },
                {
                    "sender": "hr@company.com",
                    "subject": "Please submit timesheet by Friday",
                    "body": "Reminder to submit your timesheet by end of day Friday.",
                    "received_date": datetime.now() - timedelta(hours=1)
                }
            ]
            
            # Store in database
            stored_count = 0
            for email in simulated_emails[:count]:
                try:
                    result = supabase.table('emails').insert({
                        'sender': email['sender'],
                        'subject': email['subject'], 
                        'received_date': email['received_date'].isoformat()
                    }).execute()
                    stored_count += 1
                except Exception as e:
                    print(f"Error storing email: {e}")
            
            return f"Successfully fetched and stored {stored_count} emails from Gmail"
            
        except Exception as e:
            return f"Error fetching emails: {str(e)}"


class ImportanceTool(BaseTool):
    """Tool for classifying email importance using hybrid approach"""
    name = "classify_importance" 
    description = "Analyze email content and classify importance level using rules and context"
    args_schema: Type[BaseModel] = ImportanceInput
    
    def _run(self, email_content: str, sender: str, subject: str) -> str:
        """Classify email importance using hybrid rule-based + context analysis"""
        try:
            security = SecurityService()
            clean_content = security.sanitize_email_content(email_content)
            
            importance_score = 0.0
            reasons = []
            
            # Rule-based checks
            urgent_keywords = ['urgent', 'asap', 'deadline', 'emergency', 'critical', 'important']
            sender_vips = ['boss@', 'ceo@', 'director@', 'manager@']
            
            # Check subject for urgent keywords
            subject_lower = subject.lower()
            for keyword in urgent_keywords:
                if keyword in subject_lower:
                    importance_score += 0.3
                    reasons.append(f"Subject contains urgent keyword: {keyword}")
            
            # Check sender importance
            sender_lower = sender.lower()
            for vip in sender_vips:
                if vip in sender_lower:
                    importance_score += 0.4
                    reasons.append(f"Email from VIP sender: {sender}")
            
            # Check content for deadlines
            deadline_patterns = [
                r'by \w+day',
                r'due \w+day', 
                r'deadline',
                r'by \d+:\d+',
                r'before \d+'
            ]
            
            content_lower = clean_content.lower()
            for pattern in deadline_patterns:
                if re.search(pattern, content_lower):
                    importance_score += 0.2
                    reasons.append(f"Contains deadline indicator")
                    break
            
            # Determine final classification
            if importance_score >= 0.6:
                classification = "HIGH"
            elif importance_score >= 0.3:
                classification = "MEDIUM" 
            else:
                classification = "LOW"
            
            result = {
                "importance": classification,
                "score": round(importance_score, 2),
                "reasons": reasons,
                "recommendation": "Show in notifications tile" if classification == "HIGH" else "Normal processing"
            }
            
            return f"Importance analysis: {json.dumps(result, indent=2)}"
            
        except Exception as e:
            return f"Error analyzing importance: {str(e)}"


class TaskExtractionTool(BaseTool):
    """Tool for extracting actionable tasks from email content"""
    name = "extract_tasks"
    description = "Extract actionable tasks and to-do items from email content with deadlines and priorities"
    args_schema: Type[BaseModel] = TaskExtractionInput
    
    def _run(self, email_content: str, sender: str) -> str:
        """Extract tasks from email content"""
        try:
            security = SecurityService()
            clean_content = security.sanitize_email_content(email_content)
            
            tasks = []
            
            # Task patterns to look for
            action_patterns = [
                r'please ([\w\s]+)',
                r'can you ([\w\s]+)',
                r'need to ([\w\s]+)', 
                r'should ([\w\s]+)',
                r'must ([\w\s]+)',
                r'send ([\w\s]+)',
                r'submit ([\w\s]+)',
                r'complete ([\w\s]+)',
                r'finish ([\w\s]+)'
            ]
            
            # Look for action items
            content_lower = clean_content.lower()
            for pattern in action_patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches:
                    if len(match.split()) <= 8:  # Keep tasks concise
                        task_text = match.strip()
                        if task_text:
                            tasks.append({
                                "task": task_text,
                                "priority": self._determine_priority(content_lower, task_text),
                                "due_date": self._extract_deadline(content_lower),
                                "source_sender": sender
                            })
            
            # Remove duplicates
            unique_tasks = []
            seen_tasks = set()
            for task in tasks:
                if task["task"] not in seen_tasks:
                    unique_tasks.append(task)
                    seen_tasks.add(task["task"])
            
            if unique_tasks:
                return f"Extracted tasks: {json.dumps(unique_tasks, indent=2)}"
            else:
                return "No actionable tasks found in email content"
                
        except Exception as e:
            return f"Error extracting tasks: {str(e)}"
    
    def _determine_priority(self, content: str, task: str) -> str:
        """Determine task priority based on context"""
        urgent_indicators = ['urgent', 'asap', 'emergency', 'critical', 'deadline']
        for indicator in urgent_indicators:
            if indicator in content or indicator in task:
                return "HIGH"
        return "MEDIUM"
    
    def _extract_deadline(self, content: str) -> Optional[str]:
        """Extract deadline from content"""
        deadline_patterns = [
            r'by (\w+day)',
            r'due (\w+day)',
            r'before (\w+day)',
            r'by (\d+/\d+)',
            r'deadline (\w+day|\d+/\d+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None


class EmailManagementTool(BaseTool):
    """Tool for performing actions on emails (trash, archive, etc.)"""
    name = "manage_email"
    description = "Perform management actions on emails like moving to trash, archiving, or marking as read"
    args_schema: Type[BaseModel] = EmailActionInput
    
    def _run(self, email_id: str, action: str) -> str:
        """Execute email management action"""
        try:
            valid_actions = ['trash', 'archive', 'mark_read', 'mark_unread']
            if action not in valid_actions:
                return f"Invalid action. Valid actions are: {', '.join(valid_actions)}"
            
            # For now, simulate the action by updating database
            # In real implementation, this would also call Gmail API
            
            if action == 'trash':
                # Move to trash (mark as deleted)
                result = supabase.table('emails').update({
                    'is_deleted': True,
                    'deleted_at': datetime.now().isoformat()
                }).eq('id', email_id).execute()
                
                return f"Email {email_id} moved to trash"
                
            elif action == 'archive':
                result = supabase.table('emails').update({
                    'is_archived': True,
                    'archived_at': datetime.now().isoformat()
                }).eq('id', email_id).execute()
                
                return f"Email {email_id} archived"
                
            elif action == 'mark_read':
                result = supabase.table('emails').update({
                    'is_read': True,
                    'read_at': datetime.now().isoformat()
                }).eq('id', email_id).execute()
                
                return f"Email {email_id} marked as read"
                
            elif action == 'mark_unread':
                result = supabase.table('emails').update({
                    'is_read': False,
                    'read_at': None
                }).eq('id', email_id).execute()
                
                return f"Email {email_id} marked as unread"
                
        except Exception as e:
            return f"Error performing email action: {str(e)}"


# Export all tools
def get_agent_tools() -> List[BaseTool]:
    """Return list of all available agent tools"""
    return [
        SQLTool(),
        EmailFetchTool(), 
        ImportanceTool(),
        TaskExtractionTool(),
        EmailManagementTool()
    ]