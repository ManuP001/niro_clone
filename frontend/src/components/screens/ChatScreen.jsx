import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Send, Mic, Share2, Pause, Play } from 'lucide-react';
import { chatMessages, quickQuestions } from '../../data/mockData';
import { BACKEND_URL } from '../../config';

const ChatScreen = () => {
  const [messages, setMessages] = useState(chatMessages);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      message: input,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
    };
    
    setMessages([...messages, newMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        type: 'ai',
        message: 'Based on your birth chart analysis, I can see interesting planetary alignments affecting this area of your life. The current transit suggests a period of growth and transformation. Would you like me to elaborate on specific aspects?',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-100">
        <div className="flex items-center gap-3">
          <button className="text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">A</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">Agastyaa</p>
              <p className="text-[10px] text-green-500">Online</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="text-gray-500">
            <Pause className="w-5 h-5" />
          </button>
          <button className="text-gray-500">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Audio Player Bar */}
      <div className="bg-white px-4 py-2 flex items-center gap-3 border-b border-gray-100">
        <button className="w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center">
          <Pause className="w-3 h-3 text-white" />
        </button>
        <div className="flex-1 h-1 bg-gray-200 rounded-full">
          <div className="h-full w-1/3 bg-amber-500 rounded-full"></div>
        </div>
        <span className="text-xs text-gray-500">1:23</span>
        <button className="text-gray-400">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.type === 'user'
                  ? 'bg-amber-500 text-white rounded-br-md'
                  : 'bg-white text-gray-700 rounded-bl-md shadow-sm border border-gray-100'
              }`}
            >
              <p className="text-sm leading-relaxed">{msg.message}</p>
              <p className={`text-[10px] mt-1 ${msg.type === 'user' ? 'text-amber-100' : 'text-gray-400'}`}>
                {msg.timestamp}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-100">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions */}
      <div className="px-4 py-2 bg-white border-t border-gray-100">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {quickQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => setInput(q)}
              className="text-xs bg-amber-50 border border-amber-200 rounded-full px-3 py-1.5 text-amber-700 whitespace-nowrap hover:bg-amber-100 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="bg-white px-4 py-3 pb-6 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-100 rounded-full px-4 py-2 flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your question..."
              className="flex-1 bg-transparent text-sm outline-none text-gray-700 placeholder-gray-400"
            />
          </div>
          <button className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-500">
            <Mic className="w-5 h-5" />
          </button>
          <button
            onClick={handleSend}
            className="w-10 h-10 bg-amber-500 rounded-full flex items-center justify-center text-white shadow-lg shadow-amber-200"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
