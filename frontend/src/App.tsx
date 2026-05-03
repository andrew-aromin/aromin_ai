import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useChat } from './hooks/useChat';

const App: React.FC = () => {
  const [input, setInput] = useState('');
  const { messages, sendMessage, isLoading } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#131314] text-[#e3e3e3]">
      <header className="p-4 border-b border-gray-800 flex items-center gap-2">
        <Sparkles className="text-blue-400" size={20} />
        <span className="font-semibold text-lg">Resume Intelligence</span>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto space-y-10 pt-10">
          {messages.length === 0 ? (
            <h1 className="text-4xl font-medium text-center text-gray-500 mt-20">
              How can I help you today?
            </h1>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex gap-5 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                <div
                  className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                      msg.role === 'user' ? 'bg-purple-600' : 'bg-blue-600'
                    }`}
                  >
                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className={`p-1 leading-relaxed prose prose-invert max-w-none`}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={scrollRef} />
        </div>
      </main>

      <footer className="p-6">
        <div className="max-w-3xl mx-auto relative group">
          <textarea
            className="w-full bg-[#1e1e1f] border border-transparent focus:border-gray-600 rounded-2xl py-4 pl-6 pr-14 text-lg outline-none resize-none min-h-[60px]"
            placeholder="Ask about my career..."
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            disabled={isLoading}
            onClick={handleSend}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-blue-400 disabled:text-gray-600 transition-colors"
          >
            {isLoading ? <Loader2 className="animate-spin" /> : <Send size={24} />}
          </button>
        </div>
      </footer>
    </div>
  );
};

export default App;
