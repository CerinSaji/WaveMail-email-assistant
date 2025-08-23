# backend/app/routers/agent_routes.py
"""
FastAPI routes for WaveMail agent functionality
Implements Day 2 endpoints for agent interaction and email management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from ..agent.wavemail_agent import get_agent

# Create router
router = APIRouter(prefix="/api", tags=["agent"])

# Request/Response models
class ChatQuery(BaseModel):
    query: str = Field(..., description="User's natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ChatResponse(BaseModel):
    success: bool
    response: str
    tools_used: List[str] = []
    processing_time: float
    timestamp: str

class EmailFetchRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=50, description="Number of emails to fetch")
    query: str = Field(default="", description="Gmail search query")

class NotificationResponse(BaseModel):
    success: bool
    notifications: List[Dict[str, Any]] = []
    count: int
    timestamp: str

class TodoResponse(BaseModel):
    success: bool
    todos: List[Dict[str, Any]] = []  
    count: int
    timestamp: str

class AgentHealthResponse(BaseModel):
    status: str
    llm_working: bool
    agent_working: bool
    tools_count: int
    memory_initialized: bool
    timestamp: str


@router.post("/chat/query", response_model=ChatResponse)
async def chat_with_agent(request: ChatQuery):
    """
    Send a natural language query to the WaveMail agent
    
    Example queries:
    - "Summarize my last 5 emails"
    - "What tasks do I have from my emails?"
    - "Show me all urgent emails"
    - "Move marketing emails to trash"
    """
    try:
        agent = get_agent()
        result = await agent.process_query(request.query, request.context)
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            tools_used=result.get("tools_used", []),
            processing_time=result.get("processing_time", 0),
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")


@router.post("/emails/fetch")
async def fetch_emails(request: EmailFetchRequest, background_tasks: BackgroundTasks):
    """
    Fetch emails from Gmail and process them through the agent
    This endpoint triggers the EmailFetchTool
    """
    try:
        agent = get_agent()
        
        # Use agent to fetch emails
        query = f"Fetch {request.count} emails from Gmail"
        if request.query:
            query += f" with search query: {request.query}"
        
        result = await agent.process_query(query)
        
        if result["success"]:
            # Schedule background processing for importance and tasks
            background_tasks.add_task(process_new_emails_background)
            
            return {
                "success": True,
                "message": result["response"],
                "processing_started": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch emails"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email fetch error: {str(e)}")


@router.get("/notifications", response_model=NotificationResponse)
async def get_notifications():
    """
    Get important/urgent emails for the notifications tile
    Uses ImportanceTool to identify high-priority emails
    """
    try:
        agent = get_agent()
        result = await agent.get_notifications()
        
        return NotificationResponse(
            success=result["success"],
            notifications=result.get("notifications", []),
            count=result.get("count", 0),
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notifications error: {str(e)}")


@router.get("/todos", response_model=TodoResponse)
async def get_todos():
    """
    Get extracted actionable tasks for the todo tile
    Uses TaskExtractionTool to find action items from emails
    """
    try:
        agent = get_agent()
        result = await agent.get_todos()
        
        return TodoResponse(
            success=result["success"],
            todos=result.get("todos", []),
            count=result.get("count", 0),
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Todos error: {str(e)}")


@router.get("/agent/status", response_model=AgentHealthResponse)
async def get_agent_status():
    """
    Check the health status of the WaveMail agent and all tools
    """
    try:
        agent = get_agent()
        health = await agent.health_check()
        
        return AgentHealthResponse(**health)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


@router.post("/agent/reset")
async def reset_agent_conversation():
    """
    Reset the agent's conversation memory
    Useful for starting fresh conversations
    """
    try:
        agent = get_agent()
        agent.reset_conversation()
        
        return {
            "success": True,
            "message": "Agent conversation memory has been reset",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")


@router.get("/agent/history")
async def get_conversation_history():
    """
    Get the current conversation history with the agent
    """
    try:
        agent = get_agent()
        history = agent.get_conversation_history()
        
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")


@router.post("/tools/classify-importance")
async def classify_email_importance(
    email_content: str,
    sender: str,
    subject: str
):
    """
    Directly call the ImportanceTool to classify an email's importance
    Useful for testing the classification logic
    """
    try:
        agent = get_agent()
        query = f"""
        Analyze the importance of this email:
        Sender: {sender}
        Subject: {subject}
        Content: {email_content}
        """
        
        result = await agent.process_query(query)
        
        return {
            "success": result["success"],
            "classification": result["response"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@router.post("/tools/extract-tasks")
async def extract_email_tasks(
    email_content: str,
    sender: str
):
    """
    Directly call the TaskExtractionTool to find actionable items
    Useful for testing task extraction logic
    """
    try:
        agent = get_agent()
        query = f"""
        Extract actionable tasks from this email:
        Sender: {sender}
        Content: {email_content}
        """
        
        result = await agent.process_query(query)
        
        return {
            "success": result["success"],
            "tasks": result["response"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task extraction error: {str(e)}")


@router.get("/test-groq")
async def test_groq_connection():
    """
    Test the Groq API connection and basic functionality
    """
    try:
        agent = get_agent()
        
        # Simple test query
        result = await agent.process_query("Say 'Groq API is working correctly' if you can respond")
        
        return {
            "success": result["success"],
            "groq_response": result["response"],
            "processing_time": result.get("processing_time", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq test error: {str(e)}")


# Background task functions
async def process_new_emails_background():
    """
    Background task to process newly fetched emails for importance and tasks
    """
    try:
        agent = get_agent()
        
        # Get recent unprocessed emails
        query = """
        SELECT id, sender, subject, body_content 
        FROM emails 
        WHERE importance_score IS NULL 
        ORDER BY received_date DESC 
        LIMIT 10
        """
        
        # Process each email for importance and tasks
        await agent.process_query(f"Process recent emails for importance and extract tasks: {query}")
        
    except Exception as e:
        print(f"Background processing error: {e}")


# Demo endpoints for testing
@router.get("/demo/sample-queries")
async def get_sample_queries():
    """
    Get sample queries to test the agent functionality
    Useful for demos and testing
    """
    sample_queries = [
        "What emails do I have today?",
        "Show me all urgent emails",
        "Summarize my last 5 emails", 
        "What tasks do I need to complete from my emails?",
        "Find emails from my boss",
        "Move all newsletter emails to trash",
        "What emails mention deadlines?",
        "Extract action items from recent emails",
        "Show me emails that need immediate attention",
        "Organize my inbox by importance"
    ]
    
    return {
        "success": True,
        "sample_queries": sample_queries,
        "count": len(sample_queries),
        "description": "These queries demonstrate the agent's capabilities"
    }


@router.post("/demo/populate-test-data")
async def populate_test_data():
    """
    Populate the database with test emails for demo purposes
    """
    try:
        agent = get_agent()
        
        # Use the EmailFetchTool to add simulated emails
        result = await agent.process_query("Fetch 10 sample emails for testing and demo purposes")
        
        return {
            "success": result["success"],
            "message": "Test data populated successfully",
            "details": result["response"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test data error: {str(e)}")