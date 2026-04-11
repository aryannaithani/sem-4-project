import React from 'react';
import { LayoutDashboard, CheckSquare, Map, User, MessageSquare } from 'lucide-react';
import { clsx } from 'clsx';

const Sidebar = ({ currentView, setCurrentView }) => {
    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
        { id: 'tasks', label: 'Task Board', icon: <CheckSquare size={20} /> },
        { id: 'roadmap', label: 'Roadmap', icon: <Map size={20} /> },
        { id: 'profile', label: 'Profile', icon: <User size={20} /> },
        { id: 'chat', label: 'Mentor Chat', icon: <MessageSquare size={20} /> },
    ];

    return (
        <aside className="w-64 h-screen bg-[#181a20] border-r border-[#2a2e37] flex flex-col items-center py-6 px-4 shrink-0 transition-all duration-300">
            <div className="flex items-center space-x-3 mb-10 w-full px-2">
                <div className="w-8 h-8 rounded-lg bg-blue-500 bg-opacity-20 flex items-center justify-center">
                    <Map className="text-blue-500" size={18} />
                </div>
                <h1 className="text-lg font-bold tracking-wide text-gray-100">AI Career Mentor</h1>
            </div>

            <nav className="w-full flex-1 space-y-2">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setCurrentView(item.id)}
                        className={clsx(
                            "w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer text-sm font-medium",
                            currentView === item.id
                                ? "bg-blue-600 bg-opacity-15 text-blue-500"
                                : "text-gray-400 hover:bg-[#20232b] hover:text-gray-200"
                        )}
                    >
                        <span>{item.icon}</span>
                        <span>{item.label}</span>
                    </button>
                ))}
            </nav>

            <div className="mt-auto w-full pt-6 border-t border-[#2a2e37]">
                <div className="flex items-center space-x-3 px-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
                        AM
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-200">Aryan M.</span>
                        <span className="text-xs text-gray-500">Mentee</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
