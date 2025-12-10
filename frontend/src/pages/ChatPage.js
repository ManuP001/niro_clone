import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Sparkles, User, Bot, Loader2, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message
  useEffect(() => {
    setMessages([{
      role: 'assistant',
      content: '🌟 Welcome to AstroTrust Chat! I can help you understand your astrological chart through conversation. Just tell me your birth details (name, date, time, and place of birth) and what you\'d like to know!',
      timestamp: new Date().toISOString()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMsg = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      setSessionId(currentSessionId);
    }

    try {
      const response = await axios.post(`${API}/chat`, {
        sessionId: currentSessionId,
        message: userMsg.content,
        actionId: null
      });

      const reply = response.data?.reply || {};

      const assistantMsg = {
        role: 'assistant',
        content: reply.rawText || '',
        timestamp: new Date().toISOString(),
        niroSummary: reply.summary,
        niroReasons: reply.reasons,
        niroRemedies: reply.remedies
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        
        {/* Back Button */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </div>

        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center mb-2">
            <Sparkles className="w-8 h-8 text-blue-600 mr-2" />
            <h1 className="text-4xl font-bold text-blue-600">
              AstroTrust Chat
            </h1>
          </div>
          <p className="text-gray-600">
            Conversational Astrology powered by AI
          </p>
        </div>

        {/* Chat Container */}
        <Card className="shadow-lg border border-gray-200 h-[600px] flex flex-col bg-white">
          <CardHeader className="bg-blue-50 border-b border-gray-200">
            <CardTitle className="text-xl flex items-center gap-2 text-blue-600">
              <Bot className="w-5 h-5" />
              Chat with AstroTrust
            </CardTitle>
            <CardDescription className="text-gray-600">
              Share your birth details and I'll provide personalized insights
            </CardDescription>
          </CardHeader>

          {/* Messages Area */}
          <ScrollArea className="flex-1 p-6">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`flex gap-3 max-w-[80%] ${
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    }`}
                  >
                    {/* Avatar */}
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === 'user'
                          ? 'bg-blue-600'
                          : 'bg-blue-500'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-white" />
                      )}
                    </div>

                    {/* Message Content */}
                    <div
                      className={`rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-50 border border-gray-200 text-gray-800'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      
                      {/* Confidence metadata */}
                      {message.confidence_metadata && (
                        <div className="mt-3 pt-3 border-t border-gray-200 text-xs">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Confidence:</span>
                            <span className="text-green-600">
                              {(message.confidence_metadata.overall_confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                          {message.confidence_metadata.assumptions?.length > 0 && (
                            <div className="mt-1 text-gray-600">
                              <span className="font-medium">Assumptions:</span>
                              <ul className="list-disc list-inside mt-1">
                                {message.confidence_metadata.assumptions.slice(0, 3).map((assumption, i) => (
                                  <li key={i}>{assumption}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}

                      <p className="text-xs mt-2 opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex gap-3 max-w-[80%]">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <CardContent className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                placeholder="Type your message... (e.g., 'I was born on 15 Aug 1990 at 2:30 PM in Mumbai')"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              💡 Tip: Share your name, birth date, time, and place for accurate insights
            </p>
          </CardContent>
        </Card>

        {/* Example queries */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 mb-3">Try asking:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              "I was born on 15 Aug 1990 at 2:30 PM in Mumbai. Tell me about my career.",
              "What does my birth chart say about relationships?",
              "I need a panchang for today"
            ].map((example, i) => (
              <button
                key={i}
                onClick={() => setInputMessage(example)}
                className="text-xs px-3 py-2 bg-white border border-blue-200 rounded-full hover:bg-blue-50 transition-colors"
                disabled={isLoading}
              >
                {example.substring(0, 50)}...
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
