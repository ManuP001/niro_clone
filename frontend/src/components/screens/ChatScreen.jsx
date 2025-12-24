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

// Render message with formatting: paragraphs, bullets, headings
const RenderMessageText = ({ text }) => {
  if (!text) return '';

  // Split into paragraphs
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());

  return (
    <div className="space-y-2">
      {paragraphs.map((para, idx) => {
        // Check if paragraph contains bullets
        if (para.includes('•') || para.includes('-')) {
          const lines = para.split('\n').map(line => line.trim()).filter(l => l);
          return (
            <ul key={idx} className="space-y-1 ml-2">
              {lines.map((line, lineIdx) => {
                // Remove bullet if it starts with one
                const cleanedLine = line.replace(/^[•-]\s*/, '');
                return (
                  <li key={lineIdx} className="flex gap-2">
                    <span className="text-emerald-600 flex-shrink-0">•</span>
                    <span>{cleanedLine}</span>
                  </li>
                );
              })}
            </ul>
          );
        }

        // Check if line ends with colon (heading-like)
        if (para.trim().endsWith(':')) {
          return (
            <p key={idx} className="font-semibold text-gray-900 mt-3 mb-1">
              {para.trim()}
            </p>
          );
        }

        // Regular paragraph
        return (
          <p key={idx} className="leading-relaxed">
            {para.trim()}
          </p>
        );
      })}
    </div>
  );
};

// Format AI response text for readability
const formatAIResponse = (text) => {
  if (!text) return '';
  
  // Ensure text is a string
  let textStr = typeof text === 'string' ? text : (Array.isArray(text) ? text.join('\n') : String(text));

  // Strip accidental rawText: prefix
  let formatted = textStr.replace(/^rawText\s*:\s*/i, '').trim();

  // Strip section labels (SUMMARY:, REASONS:, etc.)
  formatted = formatted.replace(/^(SUMMARY|REASONS|REMEDIES|DATA_GAPS|ANSWER):\s*/gmi, '').trim();

  // Strip signal IDs [S1], [S2], etc. from the message
  formatted = formatted.replace(/\s*\[S\d+\]\s*/g, ' ');
  
  // Split into lines and filter out structured content
  const lines = formatted.split('\n');
  const cleanLines = lines.filter(line => {
    const trimmed = line.trim();
    
    // Keep empty lines (for paragraph breaks)
    if (!trimmed) return true;
    
    // Remove bullet points containing arrows (→) - these are reasons/remedies
    if ((trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) && trimmed.includes('→')) {
      return false;
    }
    
    // Remove "(empty)" lines
    if (trimmed.toLowerCase() === '(empty)' || trimmed.toLowerCase() === 'empty') {
      return false;
    }
    
    return true;
  });
  
  formatted = cleanLines.join('\n');
  
  // Clean up double spaces and multiple newlines
  formatted = formatted.replace(/  +/g, ' ');
  formatted = formatted.replace(/\n{3,}/g, '\n\n');

  // Normalize newlines
  formatted = formatted.replace(/\r\n/g, '\n');
  
  return formatted.trim();
};

const WhyAnswerSection = ({ reasons = [], timingWindows = [], dataGaps = [] }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Filter empty data gaps - only show non-empty gaps
  const filteredGaps = Array.isArray(dataGaps) 
    ? dataGaps.filter(gap => gap && gap !== 'none' && gap.trim() !== '')
    : [];

  // Only show if there's actual content
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
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [lastAiQuestion, setLastAiQuestion] = useState(null);
  const [typewriterIndex, setTypewriterIndex] = useState(-1);
  const messagesEndRef = useRef(null);

  // Get messages from global store
  const messages = getMessages(userId) || [];

  // Load personalized welcome message on mount
  useEffect(() => {
    const loadWelcome = async () => {
      try {
        // Check if welcome already in store
        if (messages.length > 0 && messages[0]?.isWelcome) {
          setWelcomeLoaded(true);
          return;
        }

        // Fetch personalized welcome from backend if authenticated
        if (token && userId) {
          try {
            const response = await fetch(`${BACKEND_URL}/api/profile/welcome`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (response.ok) {
              const data = await response.json();
              if (data.ok && data.welcome_message) {
                // NEW FORMAT: welcome_message (string) + suggested_questions (array)
                const messageText = data.welcome_message;
                const questions = data.suggested_questions || [];
                
                const welcomeMessage = {
                  id: 'welcome',
                  type: 'ai',
                  message: messageText,
                  timestamp: 'Welcome',
                  isWelcome: true,
                };
                // Store in global store for persistence
                setMessages(userId, [welcomeMessage]);
                setSuggestedQuestions(questions);
                setWelcomeLoaded(true);
                return;
              }
            }
          } catch (apiErr) {
            console.error('Error fetching personalized welcome:', apiErr);
          }
        }
      } catch (err) {
        console.error('Error loading welcome message:', err);
      }

      // Fallback: always show generic welcome if no personalized message was loaded
      if (messages.length === 0) {
        setMessages(userId, [WELCOME_MESSAGE]);
      }
      setWelcomeLoaded(true);
    };

    loadWelcome();
  }, [userId, token, messages.length]);

  // Typewriter effect for new messages
  useEffect(() => {
    if (typewriterIndex >= 0 && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === 'ai' && typeof lastMessage.message === 'string') {
        const fullText = lastMessage.message;
        // Show typewriter effect for first ~240 chars or first 2-3 lines
        const typewriterLength = Math.min(240, fullText.split('\n').slice(0, 3).join('\n').length);
        
        if (typewriterIndex < typewriterLength) {
          const timer = setTimeout(() => {
            setTypewriterIndex(typewriterIndex + 1);
          }, 30); // ~30ms per character for typewriter feel
          return () => clearTimeout(timer);
        } else {
          // Typewriter done
          setTypewriterIndex(-1);
        }
      }
    }
  }, [typewriterIndex, messages]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Extract last AI question for context
  const extractQuestion = (text) => {
    if (!text) return null;
    // Check if last message contains a question mark or is a choice prompt
    if (text.includes('?') || text.includes('Pick one') || text.includes('Which of these')) {
      return text;
    }
    return null;
  };

  const handleSendChip = (chipText) => {
    setInput(chipText);
    // Send immediately
    setTimeout(() => {
      handleSend(chipText);
    }, 0);
  };

  const handleSend = async (messageOverride = null) => {
    const userMessageText = messageOverride || input.trim();
    if (!userMessageText) return;
    
    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      message: userMessageText,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
    };
    
    // Add user message to store
    addMessage(userId, newMessage);
    setInput('');
    setIsTyping(true);
    setSuggestedQuestions([]); // Hide chips after sending

    try {
      // Check if this is a short reply that needs context
      let messageToSend = userMessageText;
      const isShortReply = userMessageText.length <= 12 || 
        ['yes', 'no', 'ok', 'go on', 'continue'].some(word => userMessageText.toLowerCase() === word);
      
      if (isShortReply && lastAiQuestion) {
        // Append context for short replies
        messageToSend = `${userMessageText}\n\nContext: The assistant previously asked: ${lastAiQuestion}`;
      }

      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          sessionId: sessionId,
          message: messageToSend,
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
      
      // Select best available message (rawText > summary, never use arrays as main message)
      let selectedMessage = data.reply?.rawText || data.reply?.summary || 'Sorry, I could not process your request.';
      // Ensure selectedMessage is a string (not an array)
      if (typeof selectedMessage !== 'string') {
        selectedMessage = Array.isArray(selectedMessage) ? selectedMessage.join('\n') : String(selectedMessage);
      }
      
      // Format the message
      const formattedMessage = formatAIResponse(selectedMessage);
      
      // Extract any questions for context
      const extractedQuestion = extractQuestion(formattedMessage);
      if (extractedQuestion) {
        setLastAiQuestion(extractedQuestion);
      }
      
      const aiResponse = {
        id: messages.length + 2,
        type: 'ai',
        message: formattedMessage,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
        reasons: data.reply?.reasons || [],
        remedies: data.reply?.remedies || [],
        timingWindows: data.reading_pack?.timing_windows || [],
        dataGaps: data.reading_pack?.data_gaps || [],
        requestId: data.requestId
      };
      // Add AI response to store
      addMessage(userId, aiResponse);
      setTypewriterIndex(0); // Start typewriter effect
    } catch (error) {
      console.error('Error sending message:', error);
      const errorResponse = {
        id: messages.length + 2,
        type: 'ai',
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }),
      };
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
                className={`rounded-2xl px-4 py-3 ${
                  msg.type === 'user'
                    ? 'max-w-[85%] sm:max-w-[70%] bg-emerald-600 text-white rounded-br-md'
                    : 'max-w-[85%] sm:max-w-[70%] bg-gray-100 text-gray-900 rounded-bl-md'
                }`}
              >
                <div className="text-sm leading-relaxed">
                  {msg.type === 'user' ? (
                    // User message: plain text
                    <p className="whitespace-pre-wrap">{msg.message}</p>
                  ) : (
                    // AI message: formatted text
                    <RenderMessageText text={msg.message} />
                  )}
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
            
            {/* Render suggested questions under welcome message */}
            {msg.isWelcome && suggestedQuestions.length > 0 && (
              <div className="flex justify-start mt-3">
                <div className="flex flex-wrap gap-2 max-w-[85%] sm:max-w-[70%]">
                  {suggestedQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendChip(question)}
                      className="inline-block px-3 py-2 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium hover:bg-emerald-200 transition-colors active:bg-emerald-300"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3 rounded-bl-md">
              <p className="text-sm text-gray-700 font-medium">Niro.AI is typing…</p>
              <div className="flex gap-1 mt-2">
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
            onClick={() => handleSend()}
            className="w-10 h-10 bg-emerald-600 rounded-full flex items-center justify-center text-white active:bg-emerald-700 transition-colors flex-shrink-0 min-h-[44px] min-w-[44px]"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
