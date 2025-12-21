import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Send, Mic, ChevronDown, ChevronUp } from 'lucide-react';
import { BACKEND_URL } from '../../config';
import { useChatStore } from '../../context/ChatContext';

const WELCOME_MESSAGE = {
  id: 'welcome',
  type: 'ai',
  message: '🌟 Welcome to Niro.AI Chat!\nI am your Astro-powered guide to help you understand your astrological chart through conversation.\n\nPlease tell me your birth details (name, date, time, and place of birth) and what you\'d like to know!',
  timestamp: 'Welcome',
  isWelcome: true,
};

// Format AI response text for readability
const formatAIResponse = (text) => {
  if (!text) return '';

  // Strip accidental rawText: prefix
  let formatted = text.replace(/^rawText\s*:\s*/i, '').trim();

  // Normalize newlines and handle spacing
  formatted = formatted.replace(/\r\n/g, '\n');
  
  // Ensure proper spacing between paragraphs
  // Split on double newlines or explicit paragraph markers
  const paragraphs = formatted.split(/\n\n+/);
  
  // Join with double newlines for readability
  formatted = paragraphs
    .map(para => {
      // Process each paragraph
      let processed = para.trim();
      
      // Convert bullet points for proper display
      if (processed.includes('•')) {
        processed = processed.split('\n').map(line => {
          // Preserve bullet formatting
          if (line.trim().startsWith('•')) {
            return line.trim();
          }
          return line.trim();
        }).join('\n');
      }
      
      return processed;
    })
    .filter(para => para.length > 0)
    .join('\n\n');

  return formatted;
};

const WhyAnswerSection = ({ reasons = [], timingWindows = [], dataGaps = [] }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Filter empty data gaps - IMPROVEMENT #4: Only show if present
  const filteredGaps = Array.isArray(dataGaps) 
    ? dataGaps.filter(gap => gap && gap !== 'none' && gap.trim() !== '')
    : [];

  if (!reasons?.length && !timingWindows?.length && !filteredGaps?.length) {
    return null;
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%] sm:max-w-[80%] bg-emerald-50 border border-emerald-200 rounded-2xl rounded-bl-md overflow-hidden">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-4 py-2 flex items-center justify-between hover:bg-emerald-100 transition-colors active:bg-emerald-100"
        >
          <span className="text-sm font-medium text-emerald-700">Why this answer</span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-emerald-600" />
          ) : (
            <ChevronDown className="w-4 h-4 text-emerald-600" />
          )}
        </button>
        
        {isExpanded && (
          <div className="px-4 py-3 border-t border-emerald-200 space-y-3">
            {reasons?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-emerald-900 mb-2">Reasons</p>
                <ul className="space-y-1">
                  {reasons.map((reason, idx) => (
                    <li key={idx} className="text-xs text-emerald-800 leading-relaxed">
                      • {reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {timingWindows?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-emerald-900 mb-2">Timing Windows</p>
                <ul className="space-y-1">
                  {timingWindows.map((window, idx) => (
                    <li key={idx} className="text-xs text-emerald-800">
                      • {window.period}: {window.nature}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {filteredGaps?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-orange-700 mb-2">Data Gaps</p>
                <ul className="space-y-1">
                  {filteredGaps.map((gap, idx) => (
                    <li key={idx} className="text-xs text-orange-600">
                      • {gap}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const ChatScreen = ({ token, userId }) => {
  const { getMessages, setMessages, addMessage } = useChatStore();
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [welcomeLoaded, setWelcomeLoaded] = useState(false);
  const messagesEndRef = useRef(null);

  // Get messages from global store
  const messages = getMessages(userId) || [];

  // Load personalized welcome message on mount - IMPROVEMENT #1: Use kundli data
  useEffect(() => {
    const loadWelcome = async () => {
      try {
        // Check if welcome already in store
        if (messages.length > 0 && messages[0]?.isWelcome) {
          setWelcomeLoaded(true);
          return;
        }

        // Check if already shown in this session (to prevent duplicates)
        if (sessionStorage.getItem('niro_welcome_shown')) {
          setWelcomeLoaded(true);
          return;
        }

        // Fetch personalized welcome from backend
        if (token && userId) {
          const response = await fetch(`${BACKEND_URL}/api/profile/welcome`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            if (data.ok && data.welcome) {
              // Create personalized welcome message
              const welcomeMsg = data.welcome;
              // Use new "message" field if available (generated from kundli data)
              const messageText = welcomeMsg.message || 
                `${welcomeMsg.title}\n\n${welcomeMsg.subtitle}\n${welcomeMsg.bullets.map((b, i) => `${i + 1}. ${b}`).join('\n')}\n\n${welcomeMsg.prompt}`;
              
              const welcomeMessage = {
                id: 'welcome',
                type: 'ai',
                message: messageText,
                timestamp: 'Welcome',
                isWelcome: true,
              };
              // Store in global store for persistence
              setMessages(userId, [welcomeMessage]);
              sessionStorage.setItem('niro_welcome_shown', 'true');
              setWelcomeLoaded(true);
              return;
            }
          }
        }
      } catch (err) {
        console.error('Error loading welcome message:', err);
      }

      // Fallback: use generic welcome
      setMessages(userId, [WELCOME_MESSAGE]);
      sessionStorage.setItem('niro_welcome_shown', 'true');
      setWelcomeLoaded(true);
    };

    loadWelcome();
  }, [userId, token, messages.length]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = input.trim();
    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      message: userMessage,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
    };
    
    // Add user message to global store - IMPROVEMENT #2: Persist messages
    addMessage(userId, newMessage);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          sessionId: sessionId,
          message: userMessage,
          actionId: null,
          subjectData: null
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Store request ID for checklist access
      if (data.requestId) {
        localStorage.setItem('lastRequestId', data.requestId);
      }
      
      // IMPROVEMENT #3: Select best available message (summary > remedies > rawText)
      // and format for readability
      let selectedMessage = data.reply?.summary || data.reply?.remedies || data.reply?.rawText || 'Sorry, I could not process your request.';
      
      // Format the message for readability
      const formattedMessage = formatAIResponse(selectedMessage);
      
      const aiResponse = {
        id: messages.length + 2,
        type: 'ai',
        message: formattedMessage,  // Formatted, clean message - no rawText prefix
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
        reasons: data.reply?.reasons || [],
        remedies: data.reply?.remedies || [],
        timingWindows: data.reading_pack?.timing_windows || [],
        dataGaps: data.reading_pack?.data_gaps || [],
        requestId: data.requestId
      };
      // Add AI response to global store - IMPROVEMENT #2: Persist messages
      addMessage(userId, aiResponse);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorResponse = {
        id: messages.length + 2,
        type: 'ai',
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
      };
      // Add error message to global store - IMPROVEMENT #2: Persist messages
      addMessage(userId, errorResponse);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header - Fixed at top */}
      <div className="flex-shrink-0 bg-white px-4 py-4 flex items-center justify-between border-b border-gray-100 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button className="text-gray-600 p-1 active:bg-gray-100 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-bold">N</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">Niro.AI</p>
              <p className="text-[10px] text-emerald-600">Online</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container - Scrollable */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id}>
            <div className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`rounded-2xl px-4 py-3 break-words ${
                  msg.type === 'user'
                    ? 'max-w-[85%] sm:max-w-[70%] bg-emerald-600 text-white rounded-br-md'
                    : 'max-w-[85%] sm:max-w-[70%] bg-gray-100 text-gray-900 rounded-bl-md'
                }`}
              >
                <div className="text-sm leading-relaxed">
                  {msg.message.split(/\n\s*\n/).map((paragraph, idx) => (
                    <p key={idx} className="mb-3 whitespace-pre-wrap">
                      {paragraph}
                    </p>
                  ))}
                </div>
                <p className={`text-[10px] mt-2 ${msg.type === 'user' ? 'text-emerald-100' : 'text-gray-500'}`}>
                  {msg.timestamp}
                </p>
              </div>
            </div>
            
            {msg.type === 'ai' && (msg.reasons?.length > 0 || msg.dataGaps?.length > 0 || msg.timingWindows?.length > 0) && (
              <WhyAnswerSection 
                reasons={msg.reasons} 
                timingWindows={msg.timingWindows}
                dataGaps={msg.dataGaps}
              />
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
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

      {/* Input Area - Fixed at bottom */}
      <div className="flex-shrink-0 bg-white px-4 py-3 border-t border-gray-100" style={{ paddingBottom: 'max(0.75rem, env(safe-area-inset-bottom))' }}>
        <div className="flex items-end gap-2">
          <div className="flex-1 bg-gray-100 rounded-full px-4 py-2 flex items-center min-h-[44px]">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
              placeholder="Type your question..."
              className="flex-1 bg-transparent text-base outline-none text-gray-900 placeholder-gray-500"
            />
          </div>
          <button 
            onClick={handleSend}
            className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center text-white active:bg-emerald-700 transition-colors flex-shrink-0 min-h-[44px] min-w-[44px] flex justify-center items-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
