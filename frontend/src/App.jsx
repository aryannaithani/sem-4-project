import { useState } from 'react';
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
      case 'roadmap': return <Roadmap setCurrentView={setCurrentView} />;
      case 'profile': return <Profile />;
      case 'chat': return <Chat />;
      case 'analytics': return <Analytics />;
      default: return <Dashboard setCurrentView={setCurrentView} />;
    }
  };

  return (
    <div className="app-shell">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      <main className="main-content">
        <div className="container">{renderView()}</div>
      </main>
    </div>
  );
}

export default App;
