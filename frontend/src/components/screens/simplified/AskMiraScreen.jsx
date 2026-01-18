import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../../../config';
import { colors } from './theme';
import { trackEvent } from './utils';

/**
 * AskMiraScreen - Full screen Mira chat (V5)
 * Mira is the AI guide that helps users with topics, packs, experts, and FAQs
 * Updated with new teal color scheme and exact welcome message
 */
export default function AskMiraScreen({ token, initialMessage = '', onNavigate }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `mira_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const initialSent = useRef(false);

  // Initialize with exact welcome message from spec
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `Hi! I'm Mira, your personal AI Astrologer at Niro. ✨

I can help you with the following:

• Answer your questions based on your birth charts
• Find the right topic & experts for your situation
• Understand our packs and pricing
• Answer questions about how Niro works

What's on your mind today?`,
      timestamp: new Date().toISOString(),
    }]);
    
    trackEvent('mira_screen_opened', { flow_version: 'v5' }, token);
  }, [token]);

  // Handle initial message from Home screen
  useEffect(() => {
    if (initialMessage && !initialSent.current && messages.length > 0) {
      initialSent.current = true;
      setTimeout(() => {
        sendMessage(initialMessage);
      }, 500);
    }
  }, [initialMessage, messages.length]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const quickReplies = [
    { label: 'Help me choose a topic', intent: 'topic_help' },
    { label: 'How does Niro work?', intent: 'how_it_works' },
    { label: 'What are the pack options?', intent: 'pack_info' },
    { label: 'I have a career question', intent: 'career' },
  ];

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;
    
    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    trackEvent('mira_message_sent', { 
      message_length: text.length,
      flow_version: 'v5' 
    }, token);

    try {
      // Call the backend chat endpoint with guide mode
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          message: text,
          sessionId: sessionId,
          actionId: 'guide_mode', // Use guide mode for Mira
        }),
      });

      let miraResponse;
      
      if (response.ok) {
        const data = await response.json();
        miraResponse = data.reply?.rawText || data.reply?.summary || getLocalResponse(text);
      } else {
        // Fallback to local response if API fails
        miraResponse = getLocalResponse(text);
      }

      // Parse response for topic suggestions
      const suggestedTopic = detectTopicFromResponse(text, miraResponse);

      setMessages(prev => [...prev, {
        id: `mira_${Date.now()}`,
        role: 'assistant',
        content: miraResponse,
        suggestedTopic: suggestedTopic,
        timestamp: new Date().toISOString(),
      }]);
    } catch (err) {
      console.error('Mira chat error:', err);
      const fallbackResponse = getLocalResponse(text);
      const suggestedTopic = detectTopicFromResponse(text, fallbackResponse);
      
      setMessages(prev => [...prev, {
        id: `mira_${Date.now()}`,
        role: 'assistant',
        content: fallbackResponse,
        suggestedTopic: suggestedTopic,
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickReply = (reply) => {
    sendMessage(reply.label);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]" style={{ backgroundColor: colors.gold.cream }}>
      {/* Header */}
      <div 
        className="px-6 py-4 flex items-center"
        style={{ background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark} 100%)` }}
      >
        <div 
          className="w-12 h-12 rounded-full flex items-center justify-center mr-3"
          style={{ backgroundColor: 'rgba(255,255,255,0.15)' }}
        >
          <span className="text-2xl">✨</span>
        </div>
        <div>
          <h1 className="font-semibold text-lg" style={{ color: '#ffffff' }}>Mira</h1>
          <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>Your AI Astrologer</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className="max-w-[85%] rounded-2xl px-4 py-3"
              style={msg.role === 'user' 
                ? { backgroundColor: colors.teal.primary, color: '#ffffff' }
                : { backgroundColor: '#ffffff', color: colors.text.dark, border: `1px solid ${colors.ui.borderDark}` }
              }
            >
              {msg.role === 'assistant' && (
                <div className="flex items-center mb-2">
                  <span className="font-medium text-sm" style={{ color: colors.teal.primary }}>Mira</span>
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              
              {/* Topic Navigation Button */}
              {msg.suggestedTopic && (
                <button
                  onClick={() => onNavigate('topic', { topicId: msg.suggestedTopic })}
                  className="mt-3 px-4 py-2 rounded-xl text-sm font-medium w-full transition-all flex items-center justify-center active:scale-[0.98]"
                  style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
                >
                  <span className="mr-2">🔮</span>
                  Explore {msg.suggestedTopic.charAt(0).toUpperCase() + msg.suggestedTopic.slice(1).replace('_', ' ')}
                </button>
              )}
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div 
              className="rounded-2xl px-4 py-3"
              style={{ backgroundColor: '#ffffff', border: `1px solid ${colors.ui.borderDark}` }}
            >
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.teal.primary }} />
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.teal.primary, animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.teal.primary, animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Replies (show only at start) */}
      {messages.length <= 2 && !loading && (
        <div className="px-4 py-2 border-t" style={{ backgroundColor: '#ffffff', borderColor: colors.ui.borderDark }}>
          <p className="text-xs mb-2" style={{ color: colors.text.mutedDark }}>Quick questions:</p>
          <div className="flex flex-wrap gap-2">
            {quickReplies.map((qr, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickReply(qr)}
                className="px-3 py-1.5 rounded-full text-sm transition-all active:scale-[0.97]"
                style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}
              >
                {qr.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t" style={{ backgroundColor: '#ffffff', borderColor: colors.ui.borderDark }}>
        <div className="flex items-center space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Mira anything..."
            className="flex-1 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2"
            style={{ 
              border: `1px solid ${colors.ui.borderDark}`, 
              backgroundColor: colors.gold.cream,
              color: colors.text.dark,
              '--tw-ring-color': colors.teal.primary,
            }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="p-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.95]"
            style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

// Local response generator for when API is unavailable
function getLocalResponse(text) {
  const lowerText = text.toLowerCase();
  
  // Topic detection responses
  if (lowerText.includes('career') || lowerText.includes('job') || lowerText.includes('work') || lowerText.includes('promotion')) {
    return "I understand you have career-related questions! 💼\n\nOur Career & Work experts can help with:\n• Job changes and timing\n• Promotion guidance\n• Career switches\n• Work-life balance\n\nWould you like to explore our Career topic and see the expert options?";
  }
  
  if (lowerText.includes('love') || lowerText.includes('relationship') || lowerText.includes('partner') || lowerText.includes('dating')) {
    return "Relationship matters are close to the heart! 💕\n\nOur Love & Relationships experts specialize in:\n• Compatibility insights\n• Communication guidance\n• Finding clarity in love\n\nShall I show you the Love topic page?";
  }
  
  if (lowerText.includes('money') || lowerText.includes('finance') || lowerText.includes('debt') || lowerText.includes('investment')) {
    return "Financial clarity is important! 💰\n\nOur Money & Finance experts can help with:\n• Investment timing\n• Debt management\n• Financial planning\n\nWant to check out our Money topic?";
  }
  
  if (lowerText.includes('health') || lowerText.includes('stress') || lowerText.includes('anxiety') || lowerText.includes('wellness')) {
    return "Your wellbeing matters! 🏥\n\nOur Health & Wellbeing experts combine holistic insights for:\n• Stress management\n• Energy optimization\n• Overall wellness\n\nWould you like to explore the Health topic?";
  }
  
  if (lowerText.includes('marriage') || lowerText.includes('family') || lowerText.includes('spouse')) {
    return "Family matters need care! 💑\n\nOur Marriage & Family experts help with:\n• Communication\n• Compatibility\n• Family dynamics\n\nShall I take you to the Marriage topic?";
  }
  
  if (lowerText.includes('business') || lowerText.includes('startup') || lowerText.includes('entrepreneur')) {
    return "Entrepreneurship is exciting! 🚀\n\nOur Business experts can guide you on:\n• Startup timing\n• Partnership decisions\n• Growth strategies\n\nWant to explore the Business topic?";
  }
  
  // How it works
  if (lowerText.includes('how') && (lowerText.includes('work') || lowerText.includes('niro'))) {
    return "Great question! Here's how Niro works: 🌟\n\n1️⃣ **Choose a topic** - Pick the life area you need help with\n\n2️⃣ **Select a pack** - Starter, Plus, or Pro based on your needs\n\n3️⃣ **Unlock experts** - Get unlimited chat access to experts in that topic\n\n4️⃣ **Get guidance** - Chat anytime, get 24hr responses\n\nPlus and Pro packs also include video calls!\n\nWhat topic interests you?";
  }
  
  // Pack info
  if (lowerText.includes('pack') || lowerText.includes('price') || lowerText.includes('cost') || lowerText.includes('tier')) {
    return "Here are our pack options: 📦\n\n**Starter (₹2,999)**\n• 4 weeks access\n• 1 expert\n• Unlimited chat\n\n**Plus (₹4,999)** ⭐ Most Popular\n• 8 weeks access\n• 3 experts\n• 2 video calls/month\n• Free tools\n\n**Pro (₹7,999)**\n• 12 weeks access\n• Unlimited experts\n• 4 video calls/month\n• Priority support\n\nEach pack covers ONE topic. Which topic are you interested in?";
  }
  
  // Topic help
  if (lowerText.includes('choose') || lowerText.includes('which') || lowerText.includes('help me')) {
    return "I'd love to help you find the right topic! 🎯\n\nTell me more about what's on your mind:\n\n• Is it about work or career decisions?\n• Relationship or family matters?\n• Financial questions?\n• Health and wellness?\n• Something else?\n\nThe more you share, the better I can guide you!";
  }
  
  // Default response
  return "I'd love to help you! Could you tell me more about what's on your mind? 🤔\n\nI can help you:\n• Find the right topic and experts\n• Explain our packs and pricing\n• Answer questions about Niro\n\nJust share what you're looking for!";
}

// Detect topic from text for navigation suggestions
function detectTopicFromResponse(userText, response) {
  const lowerText = userText.toLowerCase();
  
  if (lowerText.includes('career') || lowerText.includes('job') || lowerText.includes('work') || lowerText.includes('promotion')) {
    return 'career_clarity';
  }
  if (lowerText.includes('love') || lowerText.includes('relationship') || lowerText.includes('partner') || lowerText.includes('dating')) {
    return 'dating_compatibility';
  }
  if (lowerText.includes('money') || lowerText.includes('finance') || lowerText.includes('debt') || lowerText.includes('investment')) {
    return 'growth_money';
  }
  if (lowerText.includes('health') || lowerText.includes('stress') || lowerText.includes('anxiety') || lowerText.includes('wellness')) {
    return 'healing_recovery';
  }
  if (lowerText.includes('marriage') || lowerText.includes('family') || lowerText.includes('spouse')) {
    return 'commitment_marriage';
  }
  if (lowerText.includes('business') || lowerText.includes('startup') || lowerText.includes('entrepreneur')) {
    return 'business_decision';
  }
  if (lowerText.includes('child') || lowerText.includes('education') || lowerText.includes('kids')) {
    return 'kids_future';
  }
  if (lowerText.includes('baby') || lowerText.includes('naming') || lowerText.includes('birth')) {
    return 'childbirth_naming';
  }
  if (lowerText.includes('fertility') || lowerText.includes('conceive')) {
    return 'fertility';
  }
  
  return null;
}
