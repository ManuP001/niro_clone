import React, { useState } from 'react';
import HomeScreen from './HomeScreen';
import ExpertsScreen from './ExpertsScreen';
import TopicQuestionScreen from './TopicQuestionScreen';
import { colors } from './theme';

/**
 * FreeCallWizard — 3-step guided wizard for booking a consultation.
 *
 * Step 1: Topic Picker     (HomeScreen in picker mode)
 * Step 2: Topic Question   (TopicQuestionScreen — 1 chip question)
 * Step 3: Expert List      (ExpertsScreen filtered by topic)
 *          → clicking an expert closes wizard and navigates to Expert Profile
 *
 * Booking (session selection, slot, OTP, confirmation) happens on ExpertProfileScreen.
 */

const TOPICS_WITH_PACKAGES = [
  'career', 'money', 'health', 'marriage', 'love', 'mental_health', 'spiritual',
];

export default function FreeCallWizard({ token, user, userState, onClose, onNavigate, onTabChange, initialTopicId }) {
  const [step, setStep] = useState(initialTopicId ? 2 : 1);
  const [selectedTopicId, setSelectedTopicId] = useState(initialTopicId || null);
  const [topicContext, setTopicContext] = useState(null);

  const handleTopicSelect = (topicId) => {
    setSelectedTopicId(topicId);
    setStep(2);
  };

  const handleAnswer = (answer) => {
    setTopicContext(answer);
    setStep(3);
  };

  const handleBack = () => {
    if (step === 1) {
      onClose();
    } else {
      setStep(s => s - 1);
    }
  };

  // Expert selected — close wizard and open their profile
  const handleExpertClick = (expert) => {
    onClose();
    if (expert?.expert_id) {
      onNavigate('expertProfile', {
        expertId: expert.expert_id,
        topicId: selectedTopicId,
        topicContext,
      });
    }
  };

  const STEP_LABELS = {
    1: 'Step 1 of 3 — Choose your topic',
    2: 'Step 2 of 3 — A quick question',
    3: 'Step 3 of 3 — Your astrologers',
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Progress dots */}
      <div className="flex items-center justify-center gap-2 pt-3 pb-1">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className="rounded-full transition-all"
            style={{
              width: s === step ? 20 : 8,
              height: 8,
              backgroundColor: s <= step ? colors.teal.primary : `${colors.teal.primary}30`,
            }}
          />
        ))}
      </div>

      {/* Step label */}
      <p className="text-center text-xs pb-2" style={{ color: colors.text.muted }}>
        {STEP_LABELS[step]}
      </p>

      {/* Step content */}
      <div className="flex-1 overflow-auto">
        {step === 1 && (
          <HomeScreen
            token={token}
            userState={userState}
            mode="picker"
            onTopicSelect={handleTopicSelect}
            enabledTopicIds={TOPICS_WITH_PACKAGES}
            onNavigate={onNavigate}
            onTabChange={onTabChange}
            onBack={handleBack}
          />
        )}

        {step === 2 && selectedTopicId && (
          <TopicQuestionScreen
            topicId={selectedTopicId}
            onAnswer={handleAnswer}
            onBack={handleBack}
          />
        )}

        {step === 3 && selectedTopicId && (
          <ExpertsScreen
            token={token}
            userState={userState}
            topicId={selectedTopicId}
            maxResults={8}
            onBookFreeCall={handleExpertClick}
            onNavigate={onNavigate}
            onTabChange={onTabChange}
            hasBottomNav={false}
          />
        )}
      </div>
    </div>
  );
}
