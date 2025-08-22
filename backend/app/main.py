from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
import httpx
import json

# Create FastAPI app
app = FastAPI(
    title="WaveMail API", 
    description="AI Email Assistant Backend",
    version="1.0.0"
)

# Allow React app to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React runs on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoint
@app.get("/")
async def root():
    return {"message": "WaveMail API is running! 🌊"}

@app.get("/api/test")  
async def test():
    return {"status": "success", "message": "Backend connected!"}

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Alternative database test using direct HTTP calls
@app.get("/api/test-db")
async def test_database():
    try:
        # Check if credentials are set
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {
                "status": "error", 
                "message": "Supabase credentials not found. Check your .env file"
            }
        
        # Direct HTTP call to Supabase REST API
        async with httpx.AsyncClient() as client:
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            # Test connection by selecting from emails table
            url = f"{settings.SUPABASE_URL}/rest/v1/emails?select=*&limit=5"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success", 
                    "message": "Database connected via REST API!",
                    "data": data,
                    "count": len(data)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Database connection failed. Status: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database connection failed: {str(e)}"
        }

# Debug config endpoint
@app.get("/api/debug-config")
async def debug_config():
    return {
        "supabase_url_set": bool(settings.SUPABASE_URL),
        "supabase_key_set": bool(settings.SUPABASE_KEY),
        "supabase_url_preview": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else "Not set",
        "supabase_key_preview": settings.SUPABASE_KEY[:20] + "..." if settings.SUPABASE_KEY else "Not set"
    }