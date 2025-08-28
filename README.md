# 🌊 WaveMail – AI-Powered Email Assistant Agent

**Surf through the email tides!**

## 🚀 Project Overview

WaveMail is an intelligent email assistant that helps users navigate their inbox efficiently by combining deterministic pipelines with LLM-driven agentic functionality. It integrates with Gmail to process messages and provides actionable insights through four core features:

- **Notifications Tile** – highlights important or urgent emails with AI-generated summaries
- **To-Do List Tile** – automatically extracts tasks and action items from emails
- **Interactive Chat Interface** – enables natural language queries over email data
- **Automated Email Sorting** – moves junk, spam, or low-priority emails to appropriate folders

## 🛠 Key Features

### 🔹 Notifications Tile
- Fetches recent emails from Gmail
- Classifies emails using rule-based filters (keywords like "urgent," "deadline," "meeting") with LLM fallback
- Generates concise summaries for important emails using Groq API

### 🔹 To-Do List Tile
- Extracts actionable items from email content
- Converts requests like "Please send the report by Friday" into tasks such as "Send the report"
- Updates dynamically as new emails arrive

### 🔹 Automated Email Sorting
- Detects and categorizes emails (Promotions, Work, Personal, etc.)
- Uses rule-based filters and LLM scoring for ambiguous cases
- Automatically moves emails to appropriate folders

### 🔹 Chat Interface
- LangChain-powered agent for natural language email queries
- Supports queries like "Summarize the last 5 emails" or "What are my action items from Bob?"
- Dynamically selects appropriate tools based on user intent

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Gmail API credentials (see `guides/gmail_api_guide.md`)
- Groq API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wavemail
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup environment variables
   cp ../guides/.env.example .env
   # Edit .env file with your API keys and routes
   
   # Run the server
   uvicorn main:app --reload
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   # Simply open index.html with Live Server extension in VS Code
   # Or serve on localhost (e.g., http://localhost:5500)
   ```

4. **Gmail API Setup:**
   - Follow the detailed guide in `guides/gmail_api_guide.md` to obtain Gmail API credentials
   - Add the credentials to your `.env` file

## 🔗 System Architecture

![WaveMail Architecture Diagram](WaveMail%20-%20Architecture%20diagram.png)

### Data Architecture
WaveMail employs a **primarily SQL-based architecture** for email querying and modification, providing structured, reliable data operations. While a **hybrid approach combining both RAG-based (semantic search) and SQL-based (structured queries)** would offer superior capabilities for complex email retrieval and contextual understanding, the current implementation focuses on SQL due to:

- **Time constraints** in the development cycle
- **Security concerns** around vector embeddings and external dependencies
- **Technical complexity** of RAG implementation and embedding management
- **Reliability requirements** for production-ready email operations

Future iterations will consider implementing hybrid retrieval for enhanced semantic search capabilities.

### Deterministic Pipeline
```
Fetch emails → Classify importance → Generate summaries → Extract tasks → Sort emails
```
Ensures predictable, reliable results for UI components.

### Agentic Architecture
- LLM agent decides which tools to invoke based on user queries
- Tools are LangChain `@tool` wrappers for email operations
- Demonstrates modern tool-calling and agentic behavior

## 🛡 Security & Privacy

### Data Protection
- **Test Environment:** Uses pre-authorized test Gmail account for development, preventing access to personal email data
- **No Persistent Storage:** Raw email content is never stored in databases, logs, or local files
- **Secure Credentials:** API keys and sensitive information stored exclusively in environment variables
- **Minimal LLM Exposure:** Only essential email metadata and content sent to external LLM services
- **Token Management:** Gmail API tokens are handled securely with proper refresh mechanisms

### Privacy Considerations
- **Ephemeral Processing:** Email data exists only during active processing sessions
- **Local Processing:** Where possible, classification and filtering use local rule-based systems
- **API Rate Limiting:** Implements proper rate limiting to prevent excessive API calls
- **Error Handling:** Sensitive information is never logged in error messages or debugging output

## 🏗 Development Phases

### Phase 1: Foundation & Email Integration
- **Project Setup:** Initialized FastAPI backend with React frontend infrastructure
- **Gmail API Integration:** Configured OAuth2 authentication and email fetching capabilities
- **Environment Configuration:** Implemented secure `.env` support for API keys and sensitive configuration
- **Basic Tools:** Created core `fetch_emails` tool for retrieving email metadata and content

### Phase 2: Intelligence Layer - Notifications
- **Classification Pipeline:** Developed hybrid rule-based + LLM classification for email importance
- **Summarization Engine:** Integrated Groq API for generating concise email summaries
- **Deterministic Processing:** Built reliable pipeline ensuring consistent notification results
- **Security Implementation:** Established data handling protocols for sensitive email content

### Phase 3: Task Management - To-Do Extraction
- **Action Item Detection:** Built NLP-powered system to extract actionable tasks from email content
- **Spam Filtering:** Implemented marketing/newsletter detection to improve task relevance
- **Dynamic Updates:** Created real-time task list updates as new emails arrive
- **Context Preservation:** Maintained task-to-email relationships for user reference

### Phase 4: User Interface Integration
- **Frontend Connectivity:** Connected React components to FastAPI endpoints
- **Real-time Updates:** Implemented live data fetching with proper error handling
- **User Experience:** Added loading states, error messages, and responsive design elements
- **API Optimization:** Streamlined backend responses for efficient frontend consumption

### Phase 5: Conversational AI - Chat Agent
- **LangChain Integration:** Developed sophisticated chat agent using LangChain framework
- **Multi-tool Orchestration:** Enabled dynamic tool selection based on user query intent
- **Natural Language Processing:** Implemented context-aware query understanding and response generation
- **Tool Chaining:** Created seamless integration between different email processing tools

### Phase 6: Email Organization - Automated Sorting
- **Category Classification:** Built intelligent email categorization (Work, Personal, Promotions, etc.)
- **Automated Actions:** Implemented automatic email movement to appropriate folders
- **Dual Interface:** Exposed sorting both as pipeline endpoint and chat agent tool
- **Rule Optimization:** Fine-tuned classification rules for improved accuracy

### Phase 7: Advanced Retrieval (Prototype)
- **Hybrid Search Architecture:** Experimented with SQL + RAG routing system
- **Database Design:** Created SQLite schema for structured email metadata storage
- **Semantic Search:** Integrated FAISS + sentence-transformers for vector-based retrieval
- **Integration Challenges:** Encountered tool chaining complexities with chat agent
- **Future Planning:** Archived as experimental branch for future development

## 📁 Project Structure

```
WM3/
├── backend/
│   ├── __pycache__/
│   ├── agents/
│   │   ├── __pycache__/
│   │   ├── chat_agent.py
│   │   ├── llm.py
│   │   ├── pipelines.py
│   │   └── tools.py
│   ├── services/
│   │   ├── __pycache__/
│   │   ├── credentials.json
│   │   ├── gmail_service.py
│   │   └── token.json
│   ├── venv/
│   ├── .env
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── vanilla.html
├── guides/
│   ├── .env.example
│   ├── gmail_api_guide.md
│   └── read_emails.py
├── .gitignore
├── README.md
├── WaveMail - Architecture diagram.png
└── WaveMail - demo video.mp4
```

## 🔧 Technology Stack

- **Backend:** FastAPI, LangChain, Groq API
- **Frontend:** HTML/CSS/JavaScript (vanilla)
- **Email Integration:** Gmail API
- **LLM Processing:** Groq for summarization and classification
- **Agent Framework:** LangChain tools and agents