import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './views/Dashboard';
import TaskBoard from './views/TaskBoard';
import Roadmap from './views/Roadmap';
import Profile from './views/Profile';
import Chat from './views/Chat';
import Analytics from './views/Analytics';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard setCurrentView={setCurrentView} />;
      case 'tasks': return <TaskBoard />;
      case 'roadmap': return <Roadmap />;
      case 'profile': return <Profile />;
      case 'chat': return <Chat />;
      case 'analytics': return <Analytics />;
      default: return <Dashboard setCurrentView={setCurrentView} />;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-base)' }}>
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <main style={{ flex: 1, overflowY: 'auto' }} className="scroll-area">
        {renderView()}
      </main>
    </div>
  );
}

export default App;
