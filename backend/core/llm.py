from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import get_settings

class LLMProcessor:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.system_prompt = """
        You are an AI assistant specialized in helping users with their tasks.
        You should be helpful, concise, and clear in your responses.
        When dealing with code, provide explanations along with the code.
        """
    
    async def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Processa uma mensagem usando o LLM configurado"""
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt}
        ]
        
        # Adiciona histórico se disponível
        if conversation_history:
            for msg in conversation_history:
                if 'user_input' in msg:
                    messages.append({"role": "user", "content": msg['user_input']})
                if 'response' in msg:
                    messages.append({"role": "assistant", "content": msg['response']})
        
        # Adiciona a mensagem atual
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    async def process_stream(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ):
        """Processa uma mensagem em modo stream"""
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt}
        ]
        
        if conversation_history:
            for msg in conversation_history:
                if 'user_input' in msg:
                    messages.append({"role": "user", "content": msg['user_input']})
                if 'response' in msg:
                    messages.append({"role": "assistant", "content": msg['response']})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error processing message: {str(e)}"
