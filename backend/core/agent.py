from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from .llm import LLMProcessor
from .tools import ToolManager

class AIAgent:
    def __init__(self):
        self.system_prompt = """
# AI DEVELOPMENT ASSISTANT SYSTEM PROMPT

[CORE IDENTITY AND PURPOSE]
You are a specialized AI development assistant focused on building applications.
Your primary purpose is to help transform ideas into functional applications through code.

[COMMUNICATION PROTOCOL]
1. ALWAYS analyze user requests within <thinking></thinking> tags before taking action
2. NEVER make assumptions about user requirements without clarification
3. ALWAYS confirm significant changes before implementation
4. Keep responses concise and focused on the current task

[DEVELOPMENT METHODOLOGY]
- Examine existing codebase before making changes
- Identify dependencies and potential impacts
- Plan changes in small, testable increments
- Consider security implications

[TECHNICAL CAPABILITIES]
- Frontend: React, TypeScript, Tailwind
- Backend: FastAPI, Python
- AI Integration: Various LLM APIs
- Development Tools and Best Practices

[CODING STANDARDS]
Follow established conventions for:
- React/TypeScript
- Python/FastAPI
- API Design
- Security Practices
"""
        self.conversations = []
        self.context = {}
        self.llm = LLMProcessor()
        self.tools = ToolManager()
        
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Adiciona a mensagem ao histórico
        self.conversations.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': message,
            'context': context or {}
        })
        
        # Processa com LLM
        response = await self.llm.process_message(
            message,
            conversation_history=self.get_recent_context(),
            system_prompt=self.system_prompt
        )
        
        # Adiciona a resposta ao histórico
        self.conversations[-1]['response'] = response
        
        return response
    
    async def process_stream(self, message: str, context: Optional[Dict[str, Any]] = None):
        # Adiciona a mensagem ao histórico
        self.conversations.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': message,
            'context': context or {}
        })
        
        # Processa com LLM em modo stream
        async for chunk in self.llm.process_stream(
            message,
            conversation_history=self.get_recent_context(),
            system_prompt=self.system_prompt
        ):
            yield chunk
    
    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.conversations[-limit:] if self.conversations else []
    
    def save_state(self, filepath: str = 'memory/state.json'):
        with open(filepath, 'w') as f:
            json.dump({
                'conversations': self.conversations,
                'context': self.context
            }, f)
    
    def load_state(self, filepath: str = 'memory/state.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.conversations = data.get('conversations', [])
                self.context = data.get('context', {})
        except FileNotFoundError:
            pass  # Estado inicial vazio
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Executa uma ferramenta específica"""
        return await self.tools.execute_tool(tool_name, **kwargs)
    
    async def list_tools(self) -> List[str]:
        """Lista todas as ferramentas disponíveis"""
        return await self.tools.list_available_tools()
