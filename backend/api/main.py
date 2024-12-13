from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from core.agent import AIAgent

app = FastAPI()
agent = AIAgent()

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Processa com o agente em modo stream
            async for chunk in agent.process_stream(
                data['message'],
                data.get('context', {})
            ):
                await websocket.send_json({
                    "message": chunk,
                    "type": "assistant",
                    "chunk": True
                })
            
            # Marca o fim do stream
            await websocket.send_json({
                "type": "assistant",
                "chunk": False,
                "end": True
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    try:
        # Para requisições HTTP, usamos streaming response
        async def generate_response():
            async for chunk in agent.process_stream(
                message.message,
                message.context
            ):
                yield chunk
        
        return StreamingResponse(generate_response(), media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    return {"tools": await agent.list_tools()}

@app.post("/tool/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any]):
    try:
        result = await agent.execute_tool(tool_name, **params)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
