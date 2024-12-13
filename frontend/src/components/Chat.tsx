import { useState, useEffect, useRef } from 'react';

interface Message {
  content: string;
  type: 'user' | 'assistant';
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const connectWebSocket = () => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/chat');
    
    wsRef.current.onopen = () => {
      setIsConnected(true);
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        content: data.message,
        type: 'assistant'
      }]);
    };
    
    wsRef.current.onclose = () => {
      setIsConnected(false);
      setTimeout(connectWebSocket, 5000);
    };
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, {
      content: input,
      type: 'user'
    }]);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message: input,
        context: {}
      }));
    }

    setInput('');
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="p-4 bg-gray-800 text-white">
        Status: {isConnected ? 'Conectado' : 'Reconectando...'}
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg ${
              msg.type === 'user' 
                ? 'bg-blue-500 text-white ml-auto' 
                : 'bg-gray-200 mr-auto'
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>
      
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            className="flex-1 p-2 border rounded"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Digite sua mensagem..."
          />
          <button 
            className="px-4 py-2 bg-blue-500 text-white rounded"
            onClick={sendMessage}
            disabled={!isConnected}
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}
