import React, { useState } from 'react';
import { colors } from './theme';

const TOPIC_QUESTIONS = {
  career:        { q: "What's your main focus right now?",   opts: ["Job search", "Career growth", "Work-life balance", "Starting a business"] },
  love:          { q: "What guidance do you need?",          opts: ["Finding a partner", "Relationship issues", "Marriage readiness", "Moving on"] },
  marriage:      { q: "What's on your mind?",               opts: ["Compatibility check", "Right timing", "In-law dynamics", "Post-marriage life"] },
  money:         { q: "What concerns you most?",             opts: ["Income growth", "Debt & savings", "Investments", "Business finances"] },
  health:        { q: "What are you seeking?",               opts: ["Mental wellbeing", "Physical health", "Chronic issues", "Energy & vitality"] },
  mental_health: { q: "What brings you here?",               opts: ["Anxiety & worry", "Low mood", "Stress & burnout", "Life decisions"] },
  spiritual:     { q: "What are you seeking?",               opts: ["Purpose & direction", "Healing", "Spiritual growth", "Connection"] },
};

const DEFAULT_Q = { q: "What brings you here today?", opts: ["Clarity", "Guidance", "Timing", "Direction"] };

const TOPIC_LABELS = {
  career: 'Career & Work', love: 'Love & Relationships', marriage: 'Marriage & Family',
  money: 'Money & Finance', health: 'Health & Wellness', mental_health: 'Mental Health',
  spiritual: 'Spiritual Growth',
};

const TOPIC_ICONS = {
  career: '💼', love: '💛', marriage: '💍', money: '💰',
  health: '🌿', mental_health: '🧠', spiritual: '✨',
};

/**
 * TopicQuestionScreen — step 2 of the booking wizard.
 * Shows 1 topic-specific question with 4 chip options.
 * Calls onAnswer(selectedOption) when user taps "Continue".
 */
export default function TopicQuestionScreen({ topicId, onAnswer, onBack }) {
  const [selected, setSelected] = useState(null);
  const { q, opts } = TOPIC_QUESTIONS[topicId] || DEFAULT_Q;
  const label = TOPIC_LABELS[topicId] || topicId;
  const icon = TOPIC_ICONS[topicId] || '🔮';

  return (
    <div
      className="flex flex-col min-h-screen px-5 pt-8 pb-6"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Topic context */}
      <div className="flex items-center gap-3 mb-8">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center text-2xl flex-shrink-0"
          style={{ backgroundColor: `${colors.teal.primary}12` }}
        >
          {icon}
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.text.muted }}>
            You selected
          </p>
          <p className="font-bold text-lg" style={{ color: colors.text.dark }}>{label}</p>
        </div>
      </div>

      {/* Question */}
      <h2 className="text-xl font-bold mb-6 leading-snug" style={{ color: colors.text.dark }}>
        {q}
      </h2>

      {/* Option chips */}
      <div className="flex flex-col gap-3 flex-1">
        {opts.map((opt) => (
          <button
            key={opt}
            onClick={() => setSelected(selected === opt ? null : opt)}
            className="w-full text-left px-5 py-4 rounded-2xl font-medium text-sm transition-all active:scale-[0.98]"
            style={selected === opt
              ? {
                  backgroundColor: colors.teal.primary,
                  color: '#ffffff',
                  boxShadow: `0 4px 16px ${colors.teal.primary}40`,
                }
              : {
                  backgroundColor: '#ffffff',
                  color: colors.text.dark,
                  border: `1.5px solid ${colors.ui.borderDark}`,
                }
            }
          >
            {opt}
          </button>
        ))}
      </div>

      {/* Continue button */}
      <div className="mt-8">
        <button
          onClick={() => selected && onAnswer(selected)}
          disabled={!selected}
          className="w-full py-4 rounded-2xl font-semibold text-base transition-all"
          style={{
            backgroundColor: selected ? colors.teal.primary : `${colors.teal.primary}40`,
            color: '#ffffff',
            cursor: selected ? 'pointer' : 'not-allowed',
          }}
        >
          Continue →
        </button>
        <button
          onClick={onBack}
          className="w-full mt-3 py-3 text-sm font-medium"
          style={{ color: colors.text.muted }}
        >
          ← Back
        </button>
      </div>
    </div>
  );
}
