from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from .llm import llm

# Import your tools
from agents.tools import (
    fetch_emails_by_number,
    fetch_email_by_query,
    sort_and_move_emails,
    classify_email,
    generate_todo,
    fetch_emails_by_sender
)

# Make sure tools have clear docstrings and examples so the agent knows when to use them
tools = [
    fetch_emails_by_number,
    fetch_email_by_query,
    sort_and_move_emails,
    classify_email,
    generate_todo,
    fetch_emails_by_sender
]

# Memory for chat context
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Initialize agent with reasoning and multi-step capability
chat_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5, # allows the agent to call multiple tools in one query
    return_direct=True
)

def run_chat(query: str) -> str:
    """
    Run the chatbot with reasoning using multiple tools as required. Keep chat history to send output back to the LLM for context.
    Keep the action_input as a natural language query.
    If the answer requires multiple steps, call one tool at a time. Do not nest tool calls.
    Do not use json or any other formatting in the input when calling the tools. VERY IMPORTANT.
    Features:
    - Uses ReAct reasoning: Thought → Action → Observation → Next Thought
    - Calls one tool at a time, and then the next based on observations
    - Send output of tool to next tool if needed
    - Maintains chat history for context
    - Returns a string response
    - If the agent cannot answer, it returns: "I am unable to perform this action."
    """
    try:
        result = chat_agent.invoke(query)

        # Ensure output is a string for memory storage
        if isinstance(result, dict) and "output" in result:
            output_text = result["output"]
            if not isinstance(output_text, str):
                output_text = str(output_text)
            return output_text
        else:
            return str(result)
    except Exception as e:
        print("Error running chat agent:", e)
        return "I am unable to perform this action."