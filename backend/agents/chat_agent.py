from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from services.gmail_service import get_gmail_service
from .llm import llm
# Import your tools
from agents.tools import fetch_emails, classify_email, summarize_email, generate_todo

# Collect tools
tools = [fetch_emails, classify_email, summarize_email, generate_todo]

# Memory for chat context
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize agent
chat_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

def run_chat(query: str) -> str:
    """Run the chatbot with a query and return response."""
    result = chat_agent.invoke(query)
    return result["output"]
