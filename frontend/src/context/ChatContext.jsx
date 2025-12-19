import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * Global Chat Store Context
 * 
 * Provides:
 * - Persistent chat history keyed by userId
 * - localStorage sync for cross-tab persistence
 * - Session-based welcome tracking
 * - Message management (add, clear, get)
 */

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [chatHistory, setChatHistory] = useState({});

  // Initialize from localStorage on mount
  useEffect(() => {
    const loadChatHistory = () => {
      try {
        const keys = Object.keys(localStorage);
        const loaded = {};
        
        keys.forEach(key => {
          if (key.startsWith('niro_chat_')) {
            const userId = key.replace('niro_chat_', '');
            try {
              loaded[userId] = JSON.parse(localStorage.getItem(key)) || [];
            } catch (e) {
              console.error(`Failed to parse chat history for ${userId}:`, e);
            }
          }
        });
        
        if (Object.keys(loaded).length > 0) {
          setChatHistory(loaded);
        }
      } catch (e) {
        console.error('Failed to load chat history from localStorage:', e);
      }
    };
    
    loadChatHistory();
  }, []);

  /**
   * Add a message to the chat history for a specific user
   * Syncs to localStorage automatically
   */
  const addMessage = (userId, message) => {
    if (!userId) return;
    
    setChatHistory(prev => {
      const userMessages = prev[userId] || [];
      const updated = [...userMessages, message];
      
      // Sync to localStorage
      try {
        localStorage.setItem(`niro_chat_${userId}`, JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save chat history to localStorage:', e);
      }
      
      return {
        ...prev,
        [userId]: updated
      };
    });
  };

  /**
   * Add multiple messages at once (useful for bulk operations)
   */
  const addMessages = (userId, messages) => {
    if (!userId || !Array.isArray(messages)) return;
    
    setChatHistory(prev => {
      const userMessages = prev[userId] || [];
      const updated = [...userMessages, ...messages];
      
      // Sync to localStorage
      try {
        localStorage.setItem(`niro_chat_${userId}`, JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save chat history to localStorage:', e);
      }
      
      return {
        ...prev,
        [userId]: updated
      };
    });
  };

  /**
   * Get all messages for a specific user
   */
  const getMessages = (userId) => {
    if (!userId) return [];
    return chatHistory[userId] || [];
  };

  /**
   * Clear all messages for a specific user
   */
  const clearMessages = (userId) => {
    if (!userId) return;
    
    setChatHistory(prev => {
      const updated = { ...prev };
      delete updated[userId];
      
      // Remove from localStorage
      try {
        localStorage.removeItem(`niro_chat_${userId}`);
      } catch (e) {
        console.error('Failed to clear chat history from localStorage:', e);
      }
      
      return updated;
    });
  };

  /**
   * Replace all messages for a specific user
   * (useful when loading initial welcome message)
   */
  const setMessages = (userId, messages) => {
    if (!userId || !Array.isArray(messages)) return;
    
    setChatHistory(prev => {
      // Sync to localStorage
      try {
        localStorage.setItem(`niro_chat_${userId}`, JSON.stringify(messages));
      } catch (e) {
        console.error('Failed to save chat history to localStorage:', e);
      }
      
      return {
        ...prev,
        [userId]: messages
      };
    });
  };

  const value = {
    chatHistory,
    addMessage,
    addMessages,
    getMessages,
    clearMessages,
    setMessages,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

/**
 * Hook to use the Chat context
 */
export const useChatStore = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatStore must be used within ChatProvider');
  }
  return context;
};

export default ChatContext;
