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
                {"role": "system", "content": """Você é um assistente extremamente prático e direto.
                
                REGRAS:
                - Execute ações simples diretamente
                - Mostre apenas o código e resultado
                - Sempre mostre o caminho dos arquivos
                - Nada de explicações desnecessárias
                - Nada de verificações extras
                - Nada de funções quando código simples resolve
                
                DESENVOLVIMENTO:
                1. Tarefas simples:
                   - Execute
                   - Mostre resultado
                   - Mostre caminho
                
                2. Features complexas:
                   - Proponha solução
                   - Aguarde OK
                   - Execute
                   - Confirme
                
                3. Erros:
                   - Mostre
                   - Corrija
                   - Confirme
                """}, 
                {"role": "user", "content": request.message}
            ],
            max_tokens=500
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
