import React from 'react';
import { SuggestedAction } from '../../types/niro';

interface QuickReplyChipsProps {
  actions: SuggestedAction[];
  onChipClick: (action: SuggestedAction) => void;
  disabled?: boolean;
}

export const QuickReplyChips: React.FC<QuickReplyChipsProps> = ({
  actions,
  onChipClick,
  disabled = false
}) => {
  if (!actions || actions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-3 ml-11">
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => onChipClick(action)}
          disabled={disabled}
          className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-full border-2 border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100 hover:border-purple-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          {action.label}
        </button>
      ))}
    </div>
  );
};

export default QuickReplyChips;
