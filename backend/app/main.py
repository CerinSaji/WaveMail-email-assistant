# backend/main.py
"""
Updated FastAPI main application with Day 2 agent functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
load_dotenv() # Load .env file


# Import existing modules (assuming these exist from Day 1)
try:
    from app.database.connection import test_database_connection
except ImportError:
    # Fallback if database module doesn't exist yet
    async def test_database_connection():
        return {"status": "database module not found"}

# Import new agent routes
from app.routers.agent_routes import router as agent_router


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌊 WaveMail starting up...")
    
    # Verify environment variables
    required_vars = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Warning: Missing environment variables: {missing_vars}")
    else:
        print("✅ Environment variables loaded")
    
    # Test agent initialization
    try:
        from app.tools.wavemail_agent import get_agent
        agent = get_agent()
        health = await agent.health_check()
        
        if health["status"] == "healthy":
            print("🤖 WaveMail agent initialized successfully")
        else:
            print(f"⚠️ Agent health check failed: {health}")
            
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
    
    yield
    
    # Shutdown
    print("🌊 WaveMail shutting down...")

# Create FastAPI app
app = FastAPI(
    title="WaveMail API",
    description="AI-powered email assistant with agentic architecture",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include agent routes
app.include_router(agent_router)

# Existing Day 1 endpoints
@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "message": "WaveMail API is running",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Agentic email processing",
            "LangChain tool calling", 
            "Groq LLM integration",
            "Smart notifications",
            "Task extraction",
            "Conversational interface"
        ]
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "WaveMail API",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/test")
async def test_api():
    """Test API connectivity"""
    return {
        "status": "success",
        "message": "API is working correctly",
        "backend_port": 8000
    }

@app.get("/api/test-db")
async def test_db():
    """Test database connectivity"""
    try:
        result = await test_database_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# New Day 2 status endpoint
@app.get("/api/status")
async def get_api_status():
    """
    Comprehensive API status including agent health
    """
    try:
        # Test database
        db_status = "unknown"
        try:
            db_result = await test_database_connection()
            db_status = "healthy" if db_result.get("status") == "connected" else "unhealthy"
        except:
            db_status = "unhealthy"
        
        # Test agent
        agent_status = "unknown"
        try:
            from app.tools.wavemail_agent import get_agent
            agent = get_agent()
            health = await agent.health_check()
            agent_status = health["status"]
        except:
            agent_status = "unhealthy"
        
        return {
            "api_status": "healthy",
            "database_status": db_status,
            "agent_status": agent_status,
            "groq_api_configured": bool(os.getenv("GROQ_API_KEY")),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0"
        }
        
    except Exception as e:
        return {
            "api_status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )