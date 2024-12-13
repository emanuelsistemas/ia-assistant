import { useState } from "react";
import { ChatInput } from "@/components/ChatInput";
import { ChatMessage } from "@/components/ChatMessage";

interface Message {
  text: string;
  isBot: boolean;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    try {
      setIsLoading(true);
      // Adiciona a mensagem do usuário
      setMessages(prev => [...prev, { text: message, isBot: false }]);

      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error("Falha ao enviar mensagem");
      }

      // Processa a resposta em streaming
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let botResponse = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          botResponse += chunk;
          
          // Atualiza a mensagem do bot em tempo real
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            
            if (lastMessage && lastMessage.isBot) {
              lastMessage.text = botResponse;
              return newMessages;
            } else {
              return [...newMessages, { text: botResponse, isBot: true }];
            }
          });
        }
      }
    } catch (error) {
      console.error("Erro:", error);
      setMessages(prev => [...prev, { text: "Desculpe, ocorreu um erro ao processar sua mensagem.", isBot: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl h-screen flex flex-col">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            message={msg.text}
            isBot={msg.isBot}
          />
        ))}
      </div>
      <div className="sticky bottom-0 bg-background p-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  );
}
