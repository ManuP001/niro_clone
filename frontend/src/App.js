import React, { useState } from 'react';
import './App.css';
import MobileFrame from './components/MobileFrame';
import HomeScreen from './components/screens/HomeScreen';
import ChatScreen from './components/screens/ChatScreen';
import HoroscopeScreen from './components/screens/HoroscopeScreen';
import PanchangScreen from './components/screens/PanchangScreen';
import CompatibilityScreen from './components/screens/CompatibilityScreen';
import BottomNav from './components/BottomNav';

function App() {
  const [activeScreen, setActiveScreen] = useState('home');

  const renderScreen = () => {
    switch (activeScreen) {
      case 'home':
        return <HomeScreen onNavigate={setActiveScreen} />;
      case 'chat':
        return <ChatScreen />;
      case 'horoscope':
        return <HoroscopeScreen />;
      case 'panchang':
        return <PanchangScreen />;
      case 'compatibility':
        return <CompatibilityScreen />;
      default:
        return <HomeScreen onNavigate={setActiveScreen} />;
    }
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
      <MobileFrame>
        <div className="flex flex-col h-full">
          <div className="flex-1 overflow-y-auto">
            {renderScreen()}
          </div>
          <BottomNav activeScreen={activeScreen} onNavigate={setActiveScreen} />
        </div>
      </MobileFrame>
    </div>
  );
}

export default App;
