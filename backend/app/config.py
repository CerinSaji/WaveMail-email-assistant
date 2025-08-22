import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # We'll add database settings later
    APP_NAME: str = "WaveMail"
    DEBUG: bool = True
    
    # Supabase (we'll fill these in Step 5)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Create settings instance
settings = Settings()