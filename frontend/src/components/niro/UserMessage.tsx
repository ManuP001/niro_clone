import React from 'react';
import { UserChatMessage } from '../../types/niro';
import { User } from 'lucide-react';

interface UserMessageProps {
  message: UserChatMessage;
}

export const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  return (
    <div className="flex justify-end mb-4">
      <div className="flex items-end gap-2 max-w-[80%]">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          <p className="text-xs text-purple-200 mt-1 text-right">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-sm">
          <User className="w-4 h-4 text-white" />
        </div>
      </div>
    </div>
  );
};

export default UserMessage;
