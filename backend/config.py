from dotenv import load_dotenv
import os

load_dotenv()  # read .env

# Gmail
#GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
#GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
