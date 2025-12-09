import React from 'react';
import { NiroChatMessage, SuggestedAction } from '../../types/niro';
import { Star, CheckCircle, Sparkles } from 'lucide-react';
import QuickReplyChips from './QuickReplyChips';

interface NiroMessageProps {
  message: NiroChatMessage;
  onChipClick: (action: SuggestedAction) => void;
  showChips?: boolean;
  disabled?: boolean;
}

export const NiroMessage: React.FC<NiroMessageProps> = ({
  message,
  onChipClick,
  showChips = true,
  disabled = false
}) => {
  const { reply, suggestedActions, timestamp } = message;

  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start gap-2 max-w-[85%]">
        {/* Avatar */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-md">
          <span className="text-white font-bold text-sm">N</span>
        </div>

        <div className="flex-1">
          {/* Name label */}
          <p className="text-xs font-semibold text-amber-600 mb-1 ml-1">NIRO</p>

          {/* Message card */}
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-md shadow-sm overflow-hidden">
            
            {/* Summary Section */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-amber-500" />
                <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Summary</h4>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                {reply.summary}
              </p>
            </div>

            {/* Reasons Section */}
            {reply.reasons && reply.reasons.length > 0 && (
              <div className="p-4 border-b border-gray-100 bg-gray-50/50">
                <div className="flex items-center gap-2 mb-3">
                  <Star className="w-4 h-4 text-purple-500" />
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Reasons</h4>
                </div>
                <ul className="space-y-2">
                  {reply.reasons.map((reason, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="w-5 h-5 rounded-full bg-purple-100 text-purple-600 text-xs font-medium flex items-center justify-center flex-shrink-0 mt-0.5">
                        {index + 1}
                      </span>
                      <span className="text-sm text-gray-700">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Remedies Section (only if non-empty) */}
            {reply.remedies && reply.remedies.length > 0 && (
              <div className="p-4 bg-green-50/50">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Remedies</h4>
                </div>
                <ul className="space-y-2">
                  {reply.remedies.map((remedy, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0 mt-1.5" />
                      <span className="text-sm text-gray-700">{remedy}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Timestamp */}
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-400">
                {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>

          {/* Quick Reply Chips */}
          {showChips && suggestedActions && suggestedActions.length > 0 && (
            <QuickReplyChips
              actions={suggestedActions}
              onChipClick={onChipClick}
              disabled={disabled}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default NiroMessage;
