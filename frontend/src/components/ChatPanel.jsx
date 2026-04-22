import React, { useRef, useEffect, useState } from 'react';
import MessageBubble from './MessageBubble';
import { Send } from 'lucide-react';

export default function ChatPanel({ messages, isLoading, onSendMessage }) {
  const [inputValue, setInputValue] = useState("");
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue("");
    }
  };

  return (
    <div className="flex flex-col flex-grow h-full bg-terminal-bg">
      <div className="flex-grow overflow-y-auto p-4 flex flex-col pt-[80px]">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} role={msg.role} text={msg.text} result={msg.result} />
        ))}
        {isLoading && (
          <div className="flex flex-col items-start my-2">
            <div className="bg-bot-bubble px-4 py-2 rounded max-w-[80%] border border-panel-border text-warn flex items-center gap-2">
              <span className="animate-pulse font-bold tracking-widest">...</span> Analyzing...
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>
      
      <div className="p-4 bg-panel-bg border-t border-panel-border">
        <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto w-full">
          <input
            type="text"
            className="flex-grow bg-[#1a1a1a] border border-panel-border rounded px-4 py-3 text-text-primary focus:outline-none focus:border-text-muted transition-colors font-mono"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !inputValue.trim()}
            className="bg-[#1a1a1a] border border-panel-border text-text-primary px-6 rounded hover:bg-[#2a2a2a] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-bold uppercase tracking-wide"
          >
            Send <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
