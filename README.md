# 🌊 WaveMail!

## Project Overview

WaveMail is an AI-powered email assistant agent with agentic architecture that demonstrates modern LLM orchestration patterns. Built as part of a GenAI automation project, it uses LangChain orchestration, Azure OpenAI models, and a hybrid RAG + SQL approach to provide intelligent email management capabilities.

The system automatically processes emails, extracts actionable tasks, identifies important communications, and provides a conversational interface for natural language email queries.

## Features

- **🤖 Agentic Email Processing**: LangChain-powered agent with custom tool calling
- **📧 Smart Email Integration**: Secure connection to pre-authorized test accounts (Gmail/Outlook)
- **🔔 Intelligent Notifications**: Hybrid rule-based + LLM classification for important emails
- **✅ Automated Task Extraction**: LLM-powered action item detection with deadlines
- **💬 Conversational Interface**: Natural language queries for email management
- **🗃️ Email Management**: Automated sorting, trash/junk filtering
- **🔍 Semantic Search**: Vector-based email search using RAG architecture
- **🔒 Security-First**: Token encryption, content filtering, and privacy safeguards

## Architecture + Diagrams

### System Architecture
```
React Frontend (3000) <-> FastAPI Backend (8000) <-> Supabase PostgreSQL
                                |
                        LangChain Agent
                                |
                    [SQLTool] [RAGTool] [EmailFetchTool]
                    [ImportanceTool] [TaskExtractionTool]
                    [EmailManagementTool]
                                |
                        Azure OpenAI (GPT-4)
```

### Agentic Tool Architecture
```
User Query → Agent Router → Tool Selection → Tool Execution → Response Generation

Available Tools:
├── SQLTool (metadata queries)
├── RAGTool (semantic search)  
├── EmailFetchTool (API integration)
├── ImportanceTool (classification)
├── TaskExtractionTool (NLP processing)
└── EmailManagementTool (actions)
```

### Tech Stack
- **Backend**: FastAPI v0.104.1, Python 3.x, LangChain
- **Frontend**: React (latest), Tailwind CSS, Axios
- **Database**: Supabase PostgreSQL with pgvector for embeddings
- **AI**: Azure OpenAI (GPT-4 + text-embedding-ada-002)
- **Security**: cryptography library for token encryption

### Data Flow
```
Email APIs → Agent Processing → Vector Embeddings → Supabase
                ↓
Dashboard Tiles ← Chat Interface ← Task Extraction
```

## Setup Instructions

### Day 1 Deliverables Setup

#### Prerequisites
- Python 3.x
- Node.js and npm
- Git
- Supabase account

#### Backend Setup
1. Clone the repository and navigate to backend:
   ```bash
   git clone [repository-url]
   cd wavemail/backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and Azure OpenAI credentials
   ```

5. Initialize the database:
   ```sql
   -- Run in Supabase SQL editor
   CREATE TABLE emails (
       id SERIAL PRIMARY KEY,
       sender VARCHAR(255),
       subject TEXT,
       received_date TIMESTAMP DEFAULT NOW(),
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

#### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

#### Verify Setup
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Status: `GET http://localhost:8000/`
- Database Test: `GET http://localhost:8000/api/test-db`

## Security Considerations

### Authentication & Authorization
- **OAuth2 Integration**: Pre-authorized test accounts for email access
- **Token Encryption**: All authentication tokens encrypted at rest using cryptography library
- **Ephemeral Tokens**: Minimal token lifetime where possible

### Data Protection
- **Content Filtering**: Sensitive information removed before LLM processing
- **No Raw Email Logging**: Email content never stored in application logs
- **Input Validation**: Comprehensive validation on all user inputs and API endpoints
- **Encrypted Storage**: All sensitive data encrypted in Supabase

### API Security
- **CORS Configuration**: Properly configured cross-origin resource sharing
- **Rate Limiting**: Protection against API abuse (planned for Days 2-6)
- **Secure Headers**: Content Security Policy and security headers
- **Input Sanitization**: XSS protection and SQL injection prevention

### Privacy Safeguards
- **PII Filtering**: Personal information filtered before AI processing  
- **Minimal Data Retention**: Clear sensitive data after processing
- **Access Controls**: Secure API endpoints with proper authentication
- **Audit Logging**: Security events logged without sensitive content

### Risk Assessment
- **Medium Risk**: Email content processing through external AI APIs
- **Mitigation**: Content filtering, encryption, and secure API practices
- **Low Risk**: Local database storage with encryption
- **Compliance**: Designed for enterprise security standards
