import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import HomeScreen from './HomeScreen';
import ExpertsScreen from './ExpertsScreen';

/**
 * FreeCallWizard — 2-step wizard rendered as a proper route (/app/wizard).
 * Because it is a route (not a fixed overlay) the layout's BottomNav and
 * each screen's ResponsiveHeader are always visible.
 *
 * Step 1: Topic Picker  (HomeScreen in picker mode)
 * Step 2: Expert List   (ExpertsScreen filtered by topic)
 *          → clicking an expert navigates to Expert Profile
 *
 * Navigation state: pass { topicId } to pre-select a topic and start at step 2.
 */

const TOPICS_WITH_PACKAGES = [
  'career', 'money', 'health', 'marriage', 'love', 'mental_health', 'spiritual',
];

export default function FreeCallWizard({ token, userState, onNavigate, onTabChange }) {
  const navigate = useNavigate();
  const { state } = useLocation();

  const initialTopicId = state?.topicId || null;
  const [step, setStep] = useState(initialTopicId ? 2 : 1);
  const [selectedTopicId, setSelectedTopicId] = useState(initialTopicId);

  const handleTopicSelect = (topicId) => {
    setSelectedTopicId(topicId);
    setStep(2);
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(s => s - 1);
    } else {
      navigate(-1);
    }
  };

  const handleExpertClick = (expert) => {
    if (expert?.expert_id) {
      onNavigate('expertProfile', {
        expertId: expert.expert_id,
        topicId: selectedTopicId,
      });
    }
  };

  if (step === 1) {
    return (
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
    );
  }

  return (
    <ExpertsScreen
      token={token}
      userState={userState}
      topicId={selectedTopicId}
      maxResults={8}
      onBookFreeCall={handleExpertClick}
      onNavigate={onNavigate}
      onTabChange={onTabChange}
      hasBottomNav={true}
    />
  );
}
