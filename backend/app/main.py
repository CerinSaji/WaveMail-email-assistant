from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from .config import settings

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

# Test database endpoint
@app.get("/api/test-db")
async def test_database():
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        result = supabase.table('emails').select('*').limit(5).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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