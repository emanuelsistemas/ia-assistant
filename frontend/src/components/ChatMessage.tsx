import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: string;
  isBot?: boolean;
}

export function ChatMessage({ message, isBot = false }: ChatMessageProps) {
  return (
    <div
      className={cn(
        "p-4 rounded-lg max-w-[80%]",
        isBot ? "bg-secondary ml-2" : "bg-primary text-primary-foreground mr-2 ml-auto"
      )}
    >
      <p className="whitespace-pre-wrap break-words">{message}</p>
    </div>
  );
}
