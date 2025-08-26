# 🌊 WaveMail – AI-Powered Email Assistant Agent

**Tagline:** Surf through the email tides!

## 🚀 Project Overview

WaveMail is an intelligent email assistant designed to help users navigate their inbox efficiently, combining deterministic pipelines with LLM-driven agentic functionality. It integrates with Gmail to process messages and provides actionable insights through:

- **Notifications Tile** – highlights important or urgent emails
- **To-Do List Tile** – automatically extracts tasks or action items from emails
- **Interactive Chat Interface** – allows natural language queries over emails
- **Automated Email Sorting** – moves junk, spam, or low-priority emails to the trash/junk folder

WaveMail demonstrates the use of LangChain tools, Groq API for LLM processing, and hybrid rule-based + LLM reasoning for email management.

## 🛠 Features

### 🔹 Notifications Tile

- **Fetch Emails:** Retrieves recent emails from a pre-authorized Gmail test account
- **Classify Emails:** Uses rule-based filters (keywords like "urgent," "deadline," "meeting") and optional LLM scoring for nuanced prioritization
- **Summarize Emails:** Groq-powered LLM generates concise summaries for important emails
- **Deterministic Pipeline:** Each step executes sequentially for predictable, reliable notifications

**Example:**

| From | Subject | Summary |
|------|---------|---------|
| Alice alice@example.com | Project Deadline | Reminder: Submit Q4 report by Friday. |

### 🔹 To-Do List Tile

- Automatically extracts actionable items from email content
- Converts requests like "Please send the report by Friday" into tasks such as "Send the report"
- Keeps the list updated dynamically as new emails arrive

### 🔹 Automated Email Sorting

**Move to Junk/Trash:** Detects marketing emails, spam, or low-priority messages using:
- Rule-based filters (spam keywords, sender domains)
- Optional LLM scoring for ambiguous cases

**Dynamic Execution:** Automatically moves identified emails to appropriate folders, keeping the inbox clean and focused.

### 🔹 Chat Interface

LangChain Agent enables natural language interaction:

**Example queries:**
- "Summarize the last 5 emails."
- "What are the action items from my email with Bob?"
- "Which emails require urgent attention?"

**Tool-based workflow:**
```
fetch_emails → classify_email → summarize_email / extract_todo_items → move_to_trash/junk
```

The agent dynamically decides which tools to call based on the user's query.

## 🔗 System Functionality

### Deterministic Pipeline (Notifications, To-Do, and Sorting)

```
Fetch emails → Filter for importance → Summarize → Extract tasks → Move junk/trash
```

Ensures repeatable, predictable results for UI tiles and email organization.

### Agentic LLM Queries (Chat Interface)

- LLM decides which tools to invoke for answering user queries
- Tools are LangChain `@tool` wrappers: fetch, summarize, classify, extract tasks, move emails
- Demonstrates modern agentic architecture and tool-calling behavior

## 🔍 Demonstration of Functionality

### Notifications Tile
Highlights important emails with concise summaries.

### To-Do Tile
Extracts actionable items and updates in real-time.

### Automated Sorting
Moves low-priority, spam, or marketing emails to trash/junk automatically.

### Chat Interface
- LLM agent interprets queries, calls tools dynamically, and returns natural language results
- Supports summaries, task extraction, importance classification, and email sorting queries

## 📈 Project Highlights

- **Hybrid Architecture:** Combines rule-based logic with LLM reasoning for reliability and nuance
- **LangChain Tool Usage:** Core email operations are wrapped as LangChain tools to demonstrate agentic capabilities
- **Pipeline vs Agent:** Distinguishes between deterministic pipelines (notifications, sorting, to-dos) and agentic tool orchestration (chat queries)
- **Security-Focused:** Minimal exposure of sensitive email content, secure API keys, and safe logging practices
- **Extensible Design:** Can integrate additional LLMs, other email providers, or front-end frameworks

## 🛡 Security & Privacy Considerations

### Test Environment
- **Test Gmail Account:** WaveMail uses a pre-authorized test Gmail account for prototype purposes
- **No Raw Email Storage:** No raw email content is stored in any database or log

### Data Protection
- **API Keys & Secrets:** Stored securely in environment variables (`.env`) and not exposed in code
- **Ephemeral Tokens:** Used where possible to minimize exposure
- **Logs:** Avoid recording full email bodies

### Sensitive Data Handling
- **Minimal LLM Exposure:** Only essential email content is sent to LLMs for summarization, task extraction, or importance scoring
- **Hybrid Filtering:** Sensitive emails are handled primarily via rule-based logic, minimizing unnecessary exposure to LLM processing