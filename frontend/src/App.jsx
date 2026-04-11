import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './views/Dashboard';
import TaskBoard from './views/TaskBoard';
import Roadmap from './views/Roadmap';
import Profile from './views/Profile';
import Chat from './views/Chat';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard setCurrentView={setCurrentView} />;
      case 'tasks':
        return <TaskBoard />;
      case 'roadmap':
        return <Roadmap />;
      case 'profile':
        return <Profile />;
      case 'chat':
        return <Chat />;
      default:
        return <Dashboard setCurrentView={setCurrentView} />;
    }
  };

  return (
    <div className="flex h-screen bg-[#0f1115] text-slate-200 overflow-hidden font-sans">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <main className="flex-1 overflow-y-auto w-full">
        {renderView()}
      </main>
    </div>
  );
}

export default App;
