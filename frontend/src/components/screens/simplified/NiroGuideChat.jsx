import React, { useState, useEffect, useRef } from 'react';
import { trackEvent } from './utils';

// Helper function for guide responses - moved outside component
function getGuideResponse(text) {
  // Simple keyword matching for V1
  if (text.includes('career') || text.includes('job') || text.includes('work') || text.includes('promotion')) {
    return {
      text: "It sounds like you're dealing with career matters. Our Career & Work experts can help with job changes, promotions, timing decisions, and more. Would you like to explore the Career topic?",
      topic: 'career'
    };
  }
  if (text.includes('love') || text.includes('relationship') || text.includes('partner') || text.includes('dating')) {
    return {
      text: "Relationship matters can be complex. Our Love & Relationships experts specialize in compatibility, communication, and finding clarity. Want to check out the Love topic?",
      topic: 'love'
    };
  }
  if (text.includes('money') || text.includes('finance') || text.includes('debt') || text.includes('investment')) {
    return {
      text: "Financial decisions need careful guidance. Our Money & Finance experts can help with investments, debt, and timing for financial moves. Shall I show you the Money topic?",
      topic: 'money'
    };
  }
  if (text.includes('health') || text.includes('stress') || text.includes('anxiety') || text.includes('wellness')) {
    return {
      text: "Your wellbeing is important. Our Health & Wellbeing experts combine holistic and astrological insights for your health journey. Would you like to explore the Health topic?",
      topic: 'health'
    };
  }
  if (text.includes('marriage') || text.includes('family') || text.includes('spouse')) {
    return {
      text: "Family matters need understanding. Our Marriage & Family experts can help navigate compatibility, communication, and family dynamics. Want to see the Marriage topic?",
      topic: 'marriage'
    };
  }
  if (text.includes('child') || text.includes('education') || text.includes('kids')) {
    return {
      text: "Children's futures matter deeply. Our Children & Education experts can guide you on education choices and child development. Shall I show you this topic?",
      topic: 'children'
    };
  }
  if (text.includes('business') || text.includes('startup') || text.includes('entrepreneur')) {
    return {
      text: "Business decisions need clarity. Our Business & Entrepreneurship experts can help with timing, partnerships, and growth strategies. Would you like to explore this topic?",
      topic: 'business'
    };
  }
  
  return {
    text: "I'd love to help you find the right guidance. Could you tell me more about what area of life you're seeking clarity in? Career, relationships, finances, health, or something else?",
    topic: null
  };
}

/**
 * NiroGuideChat - Persistent guide chat overlay
 * Helps users navigate topics and packs (NOT expert chat)
 */
export default function NiroGuideChat({ token, isOpen, onClose, onNavigate }) {
  const [messages, setMessages] = useState([
    {
      id: 'init_1',
      role: 'assistant',
      content: "Hi! I'm Niro, your guide. I can help you find the right topic and pack for your situation. What's on your mind?",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [msgCounter, setMsgCounter] = useState(1);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      trackEvent('guide_chat_opened', { source_screen: 'overlay' }, token);
    }
  }, [isOpen, token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const quickReplies = [
    { label: 'Career guidance', topic: 'career' },
    { label: 'Relationship help', topic: 'love' },
    { label: 'Financial clarity', topic: 'money' },
    { label: 'Health concerns', topic: 'health' },
  ];

  const handleSend = () => {
    if (!input.trim() || loading) return;
    
    const currentInput = input;
    const newUserMsgId = `user_${msgCounter}`;
    const newAssistantMsgId = `assistant_${msgCounter + 1}`;
    
    // Add user message
    setMessages(prev => [...prev, {
      id: newUserMsgId,
      role: 'user',
      content: currentInput,
    }]);
    
    setInput('');
    setLoading(true);
    setMsgCounter(prev => prev + 2);
    
    // Generate response after delay
    setTimeout(() => {
      const response = getGuideResponse(currentInput.toLowerCase());
      setMessages(prev => [...prev, {
        id: newAssistantMsgId,
        role: 'assistant',
        content: response.text,
        suggestedTopic: response.topic,
      }]);
      setLoading(false);
    }, 500);
  };

  const handleQuickReply = (topic) => {
    const quickLabel = quickReplies.find(q => q.topic === topic)?.label || topic;
    const userMsgId = `quick_user_${msgCounter}`;
    const assistantMsgId = `quick_assistant_${msgCounter + 1}`;
    
    setMessages(prev => [...prev, 
      {
        id: userMsgId,
        role: 'user',
        content: quickLabel,
      },
      {
        id: assistantMsgId,
        role: 'assistant',
        content: `Great choice! Let me take you to the ${topic} topic where you can see our experts and choose the right pack for you.`,
        suggestedTopic: topic,
      }
    ]);
    setMsgCounter(prev => prev + 2);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center sm:justify-center">
      <div className="bg-white w-full sm:w-96 h-[80vh] sm:h-[600px] sm:rounded-2xl flex flex-col shadow-2xl">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-700 text-white px-4 py-4 sm:rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center mr-3">
              <span className="text-xl">💬</span>
            </div>
            <div>
              <h3 className="font-semibold">Niro Guide</h3>
              <p className="text-slate-300 text-xs">Here to help you choose</p>
            </div>
          </div>
          <button onClick={onClose} className="text-white/80 hover:text-white text-2xl">
            ×
          </button>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-emerald-500 text-white' 
                  : 'bg-slate-100 text-slate-800'
              }`}>
                <p className="text-sm">{msg.content}</p>
                
                {msg.suggestedTopic && (
                  <button
                    onClick={() => {
                      onClose();
                      onNavigate('topic', { topicId: msg.suggestedTopic });
                    }}
                    className="mt-2 bg-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-medium w-full hover:bg-emerald-600 transition-all"
                  >
                    Go to {msg.suggestedTopic.charAt(0).toUpperCase() + msg.suggestedTopic.slice(1)} →
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 rounded-2xl px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Quick Replies */}
        {messages.length < 3 && (
          <div className="px-4 py-2 border-t border-slate-100">
            <p className="text-slate-500 text-xs mb-2">Quick topics:</p>
            <div className="flex flex-wrap gap-2">
              {quickReplies.map((qr) => (
                <button
                  key={qr.topic}
                  onClick={() => handleQuickReply(qr.topic)}
                  className="bg-slate-100 text-slate-700 px-3 py-1.5 rounded-full text-sm hover:bg-slate-200 transition-all"
                >
                  {qr.label}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Input */}
        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              className="flex-1 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-emerald-300"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="bg-emerald-500 text-white p-3 rounded-xl hover:bg-emerald-600 transition-all disabled:opacity-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
