"""
Main WaveMail Agent implementation using LangChain and Groq
Implements agentic architecture with tool calling capabilities
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ..tools.agent_tools import get_agent_tools

from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_structured_chat_agent

class WaveMailAgent:
    def __init__(self):
        """Initialize the WaveMail agent with tools and memory"""
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=4096,
            groq_api_key=self.groq_api_key,
            model_kwargs={
                "top_p": 0.9,
                "frequency_penalty": 0.1
            }
        )
        
        # Get agent tools
        self.tools = get_agent_tools()
        
        # Create agent prompt
        self.prompt = self._create_agent_prompt()
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=2000
        )
        
        # Create structured chat agent
        try:
            self.agent = create_structured_chat_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            
            # Agent executor
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate",
                handle_parsing_errors=True
            )
        except Exception as e:
            print(f"Error initializing agent: {e}")
            self.agent_executor = None


    
    def _create_agent_prompt(self) -> ChatPromptTemplate:
        """Create the system prompt for the agent"""
        system_message = """You are WaveMail, an intelligent email assistant agent.

You have access to several tools to help manage emails and answer user questions:

1. **sql_query**: Query the emails database for metadata, counts, filtering
2. **fetch_emails**: Fetch new emails from Gmail and store them
3. **classify_importance**: Analyze emails to determine importance level
4. **extract_tasks**: Find actionable tasks and to-do items in emails
5. **manage_email**: Perform actions like trash, archive, mark read/unread

**Your capabilities:**
- Analyze and summarize emails intelligently
- Extract actionable tasks with priorities and deadlines
- Classify email importance for notifications
- Manage email organization (trash, archive, etc.)
- Answer questions about email content and metadata
- Provide insights about email patterns

**Guidelines:**
- Always use the most appropriate tool for each request
- Be helpful, concise, and accurate in your responses
- When extracting tasks, focus on clear, actionable items
- For importance classification, consider sender, subject, and content
- Explain your reasoning when making recommendations
- Handle errors gracefully and suggest alternatives

**Response Style:**
- Be conversational but professional
- Provide structured information when helpful
- Ask clarifying questions if user intent is unclear
- Offer proactive suggestions for email management

Remember: You're helping users manage their email efficiently while maintaining security and privacy."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("system", "{chat_history}"),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])

    
    async def process_query(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user query through the agent
        
        Args:
            query: User's natural language query
            user_context: Optional context about user/session
            
        Returns:
            Dict with response, tools_used, and metadata
        """
        try:
            start_time = datetime.now()
            
            # Prepare input with context
            agent_input = {
                "input": query
            }
            
            # Add user context if provided
            if user_context:
                context_str = f"User context: {user_context}"
                agent_input["input"] = f"{context_str}\n\nUser query: {query}"
            
            if self.agent_executor:
                # Use function calling agent
                response = await self.agent_executor.ainvoke(agent_input)
                agent_response = response["output"]
                
                # Extract metadata about tools used
                tools_used = self._extract_tools_used(response)
                
            else:
                # Fallback to direct LLM call
                response = await self.llm.ainvoke([HumanMessage(content=query)])
                agent_response = response.content
                tools_used = []
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "response": agent_response,
                "tools_used": tools_used,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"I encountered an error processing your request: {str(e)}",
                "error": str(e),
                "tools_used": [],
                "processing_time": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_tools_used(self, response: Dict) -> List[str]:
        """Extract which tools were used from agent response"""
        tools_used = []
        
        # This would need to be implemented based on LangChain's response format
        # For now, return empty list
        if "intermediate_steps" in response:
            for step in response["intermediate_steps"]:
                if hasattr(step, 'tool'):
                    tools_used.append(step.tool)
        
        return tools_used
    
    async def get_notifications(self) -> Dict[str, Any]:
        """Get important/urgent emails for notifications tile"""
        try:
            # Use SQL tool to get recent emails
            query = """
            SELECT id, sender, subject, received_date 
            FROM emails 
            WHERE received_date >= NOW() - INTERVAL '24 hours'
            ORDER BY received_date DESC
            LIMIT 20
            """
            
            response = await self.process_query(
                f"Get important emails from the last 24 hours using this query: {query}"
            )
            
            return {
                "success": True,
                "notifications": response.get("response", ""),
                "count": 0,  # Would extract from actual response
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "notifications": [],
                "count": 0
            }
    
    async def get_todos(self) -> Dict[str, Any]:
        """Extract actionable tasks for todo tile"""
        try:
            response = await self.process_query(
                "Find and extract all actionable tasks from recent emails. "
                "Include priorities, deadlines, and sender information."
            )
            
            return {
                "success": True,
                "todos": response.get("response", ""),
                "count": 0,  # Would extract from actual response  
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "todos": [],
                "count": 0
            }
    
    def reset_conversation(self):
        """Reset the agent's conversation memory"""
        if self.memory:
            self.memory.clear()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history"""
        if self.memory and hasattr(self.memory, 'chat_memory'):
            messages = []
            for message in self.memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    messages.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    messages.append({"role": "assistant", "content": message.content})
            return messages
        return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the agent and all tools are working properly"""
        try:
            # Test basic LLM connection
            test_response = await self.llm.ainvoke([
                HumanMessage(content="Say 'Agent is working' if you can respond")
            ])
            
            # Test agent executor if available
            agent_working = False
            if self.agent_executor:
                try:
                    test_agent_response = await self.agent_executor.ainvoke({
                        "input": "Test agent functionality"
                    })
                    agent_working = True
                except:
                    agent_working = False
            
            return {
                "status": "healthy",
                "llm_working": bool(test_response),
                "agent_working": agent_working,
                "tools_count": len(self.tools),
                "memory_initialized": self.memory is not None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Singleton instance for the application
_agent_instance: Optional[WaveMailAgent] = None

def get_agent() -> WaveMailAgent:
    """Get or create the WaveMail agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = WaveMailAgent()
    return _agent_instance

async def test_agent():
    """Test function for development"""
    agent = get_agent()
    
    # Test basic functionality
    health = await agent.health_check()
    print("Agent Health:", health)
    
    # Test query processing
    response = await agent.process_query("What emails do I have?")
    print("Agent Response:", response)


if __name__ == "__main__":
    # Run test
    asyncio.run(test_agent())