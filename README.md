# 🌊 WaveMail - AI Email Assistant

An AI-powered email assistant built with agentic architecture using FastAPI, React, LangChain, and Supabase.

## 🚀 Features (Coming Soon)
- Smart email notifications
- Automatic task extraction
- Semantic email search
- Natural language chat interface
- Email importance classification

## 🛠️ Tech Stack
- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI + Python
- **AI/LLM**: LangChain + Azure OpenAI
- **Database**: Supabase (PostgreSQL + pgvector)
- **Email APIs**: Gmail/Outlook integration

## 📦 Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your credentials
uvicorn app.main:app --reload
