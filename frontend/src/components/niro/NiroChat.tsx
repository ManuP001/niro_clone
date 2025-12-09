import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import {
  ChatMessage,
  UserChatMessage,
  NiroChatMessage,
  NiroChatResponse,
  SuggestedAction
} from '../../types/niro';

import MessageList from './MessageList';
import ChatInput from './ChatInput';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Session ID key for localStorage
const SESSION_KEY = 'niro_session_id';

// Generate a unique ID
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Get or create session ID from localStorage
const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = generateId();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
};

// Welcome message from NIRO
const createWelcomeMessage = (): NiroChatMessage => ({
  id: generateId(),
  role: 'niro',
  reply: {
    summary: "Namaste! I'm NIRO, your personal Vedic astrology guide. I'm here to help you understand life's patterns through the ancient wisdom of Jyotish.",
    reasons: [
      "Share your birth details (date, time, place) for personalized insights",
      "Ask about career, relationships, health, or any life area",
      "Explore your past patterns or get guidance for the future"
    ],
    remedies: []
  },
  mode: 'WELCOME',
  focus: null,
  suggestedActions: [
    { id: 'focus_career', label: 'Career' },
    { id: 'focus_relationship', label: 'Relationships' },
    { id: 'past_themes', label: 'Past 2 years' },
    { id: 'daily_guidance', label: 'Daily guidance' }
  ],
  timestamp: new Date()
});

export const NiroChat: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize session and welcome message
  useEffect(() => {
    const sid = getSessionId();
    setSessionId(sid);
    setMessages([createWelcomeMessage()]);
  }, []);

  // Send message to backend
  const sendMessage = useCallback(async (
    messageText: string,
    actionId: string | null = null
  ) => {
    if (!messageText.trim() || isLoading) return;

    // Clear any previous error
    setError(null);

    // Create user message
    const userMessage: UserChatMessage = {
      id: generateId(),
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post<NiroChatResponse>(`${API}/chat`, {
        sessionId,
        message: messageText,
        actionId
      });

      // Create NIRO message from response
      const niroMessage: NiroChatMessage = {
        id: generateId(),
        role: 'niro',
        reply: response.data.reply,
        mode: response.data.mode,
        focus: response.data.focus,
        suggestedActions: response.data.suggestedActions || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, niroMessage]);

    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to get response from NIRO';
      setError(errorMsg);
      toast.error(errorMsg);

      // Add error message
      const errorMessage: NiroChatMessage = {
        id: generateId(),
        role: 'niro',
        reply: {
          summary: "I apologize, but I encountered an issue processing your request. Please try again.",
          reasons: [
            "There might be a temporary connection issue",
            "Try rephrasing your question"
          ],
          remedies: []
        },
        mode: 'ERROR',
        focus: null,
        suggestedActions: [
          { id: 'retry', label: 'Try again' }
        ],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, isLoading]);

  // Handle chip click
  const handleChipClick = useCallback((action: SuggestedAction) => {
    sendMessage(action.label, action.id);
  }, [sendMessage]);

  // Handle send from input
  const handleSend = useCallback((message: string) => {
    sendMessage(message, null);
  }, [sendMessage]);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Fixed Header */}
      <header className="flex-shrink-0 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-1 text-gray-500 hover:text-gray-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back</span>
            </button>

            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  NIRO
                </h1>
                <p className="text-xs text-gray-500">Your Astrology Guide</p>
              </div>
            </div>

            <div className="w-16" /> {/* Spacer for centering */}
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="flex-shrink-0 bg-red-50 border-b border-red-200 px-4 py-2">
          <p className="text-sm text-red-600 text-center">{error}</p>
        </div>
      )}

      {/* Message List */}
      <MessageList
        messages={messages}
        isLoading={isLoading}
        onChipClick={handleChipClick}
      />

      {/* Input Bar */}
      <ChatInput
        onSend={handleSend}
        disabled={isLoading}
        placeholder="Ask about your birth chart, career, relationships..."
      />
    </div>
  );
};

export default NiroChat;
