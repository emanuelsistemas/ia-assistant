from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    client = None
else:
    try:
        client = OpenAI(api_key=openai_api_key)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}")
        client = None

@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    if not client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI client not initialized. Please check server logs."
        )

    try:
        print(f"Received message: {request.message}")
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Você é um assistente conciso e direto. 
                Mantenha suas respostas curtas e objetivas, focando nos pontos principais.
                Use linguagem simples e evite explicações muito longas ou técnicas.
                
                Formate suas respostas usando Markdown para melhor legibilidade:
                - Use ## para títulos secundários
                - Use * ou - para listas
                - Use **texto** para destaque
                - Use `código` para termos técnicos
                - Use > para citações ou notas importantes
                - Separe seções com linhas em branco
                """}, 
                {"role": "user", "content": request.message}
            ],
            max_tokens=300
        )
        
        response = completion.choices[0].message.content
        print(f"Generated response: {response}")
        
        return ChatResponse(response=response)
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    if client:
        return {"status": "healthy", "openai_client": "initialized"}
    return {"status": "degraded", "openai_client": "not initialized"}

print("Backend started successfully")
