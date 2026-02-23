import React, { useState } from 'react';
import HomeScreen from './HomeScreen';
import ExpertsScreen from './ExpertsScreen';
import ExpertProfileScreen from './ExpertProfileScreen';
import ScheduleCallScreen from './ScheduleCallScreenV2';
import { colors } from './theme';

/**
 * FreeCallWizard — 4-step guided wizard for booking a free consultation.
 *
 * Step 1: Topic Picker  (HomeScreen in picker mode)
 * Step 2: Matched Astrologers (ExpertsScreen filtered by topic, max 3)
 * Step 3: Expert Profile  (ExpertProfileScreen in wizard mode)
 * Step 4: Schedule Call  (ScheduleCallScreenV2 with expertId + topicId)
 *
 * Renders as a full-screen fixed overlay so it doesn't break existing routing.
 */

// Only show topics that have packages defined in the backend.
// Add a topic ID here once its packages are created.
const TOPICS_WITH_PACKAGES = [
  'career',
  'money',
  'health',
  'marriage',
  'love',
  'mental_health',
  'spiritual',
];

export default function FreeCallWizard({ token, user, userState, onClose, onNavigate, onTabChange }) {
  const [step, setStep] = useState(1);
  const [selectedTopicId, setSelectedTopicId] = useState(null);
  const [selectedExpertId, setSelectedExpertId] = useState(null);
  const [selectedExpertName, setSelectedExpertName] = useState(null);

  const handleTopicSelect = (topicId) => {
    setSelectedTopicId(topicId);
    setStep(2);
  };

  const handleExpertSelect = (expertId, expertName) => {
    setSelectedExpertId(expertId);
    setSelectedExpertName(expertName || null);
    setStep(3);
  };

  const handleBookFreeCall = () => {
    setStep(4);
  };

  const handleBack = () => {
    if (step === 1) {
      onClose();
    } else {
      setStep(s => s - 1);
    }
  };

  const handleScheduleComplete = () => {
    onClose();
    // Navigate to mypack so the user can see their upcoming call
    if (onNavigate) onNavigate('mypack');
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Progress dots */}
      <div className="flex items-center justify-center gap-2 pt-3 pb-1">
        {[1, 2, 3, 4].map((s) => (
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
        {step === 1 && 'Step 1 of 4 — Choose your topic'}
        {step === 2 && 'Step 2 of 4 — Pick an astrologer'}
        {step === 3 && 'Step 3 of 4 — Review & confirm'}
        {step === 4 && 'Step 4 of 4 — Choose a time'}
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
          <ExpertsScreen
            token={token}
            userState={userState}
            topicId={selectedTopicId}
            maxResults={3}
            onExpertSelect={handleExpertSelect}
            onNavigate={onNavigate}
            onTabChange={onTabChange}
            hasBottomNav={false}
          />
        )}

        {step === 3 && selectedExpertId && (
          <ExpertProfileScreen
            token={token}
            expertId={selectedExpertId}
            userState={userState}
            wizardMode={true}
            wizardTopicId={selectedTopicId}
            onBookFreeCall={handleBookFreeCall}
            onBack={handleBack}
            onNavigate={onNavigate}
            onTabChange={onTabChange}
            hasBottomNav={false}
          />
        )}

        {step === 4 && (
          <ScheduleCallScreen
            token={token}
            user={user}
            expertId={selectedExpertId}
            topicId={selectedTopicId}
            expertName={selectedExpertName}
            onBack={handleBack}
            onComplete={handleScheduleComplete}
          />
        )}
      </div>
    </div>
  );
}
