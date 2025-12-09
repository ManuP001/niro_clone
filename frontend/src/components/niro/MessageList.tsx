import React, { useRef, useEffect } from 'react';
import { ChatMessage, SuggestedAction } from '../../types/niro';
import UserMessage from './UserMessage';
import NiroMessage from './NiroMessage';
import { Loader2 } from 'lucide-react';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onChipClick: (action: SuggestedAction) => void;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  onChipClick
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="max-w-4xl mx-auto space-y-2">
        {messages.map((message, index) => {
          const isLastNiro = message.role === 'niro' && 
            messages.slice(index + 1).every(m => m.role === 'user');

          if (message.role === 'user') {
            return <UserMessage key={message.id} message={message} />;
          } else {
            return (
              <NiroMessage
                key={message.id}
                message={message}
                onChipClick={onChipClick}
                showChips={isLastNiro && !isLoading}
                disabled={isLoading}
              />
            );
          }
        })}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start gap-2">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-sm">N</span>
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md shadow-sm px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-amber-500" />
                  <span className="text-sm text-gray-500">NIRO is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default MessageList;
