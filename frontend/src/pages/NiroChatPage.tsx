import React from 'react';
import NiroChat from '../components/niro/NiroChat';

/**
 * NIRO Chat Page
 * 
 * Example usage:
 * Import this component and add it to your routes:
 * 
 * ```tsx
 * import NiroChatPage from './pages/NiroChatPage';
 * 
 * <Route path="/niro" element={<NiroChatPage />} />
 * ```
 */
const NiroChatPage: React.FC = () => {
  return <NiroChat />;
};

export default NiroChatPage;
