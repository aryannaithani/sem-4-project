import { useEffect, useState } from 'react';
import { LayoutDashboard, CheckSquare, Map, User, MessageSquare, Activity, GraduationCap } from 'lucide-react';
import { clsx } from 'clsx';
import { getProfile } from '../api';

const Sidebar = ({ currentView, setCurrentView }) => {
    const [profile, setProfile] = useState(null);

    useEffect(() => {
        getProfile().then(setProfile).catch(() => { });
    }, []);

    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
        { id: 'tasks', label: 'Task Board', icon: <CheckSquare size={20} /> },
        { id: 'roadmap', label: 'Roadmap', icon: <Map size={20} /> },
        { id: 'analytics', label: 'Analytics', icon: <Activity size={20} /> },
        { id: 'profile', label: 'Digital Twin', icon: <User size={20} /> },
        { id: 'chat', label: 'Mentor Chat', icon: <MessageSquare size={20} /> },
    ];

    return (
        <aside className="w-72 min-h-screen border-r border-[#232328] bg-[#09090b] p-5 flex flex-col gap-6">
            <div className="flex items-center gap-3 px-2">
                <div className="w-11 h-11 rounded-xl bg-white text-black flex items-center justify-center">
                    <GraduationCap size={20} />
                </div>
                <div>
                    <h1 className="font-extrabold tracking-tight">Scholars Mentor</h1>
                    <p className="text-xs muted">Advanced learning companion</p>
                </div>
            </div>

            <nav className="space-y-1">
                {navItems.map((item) => {
                    const isActive = currentView === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setCurrentView(item.id)}
                            className={clsx(
                                "w-full flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-semibold transition-all duration-200 text-left border",
                                isActive
                                    ? "bg-white text-black border-white"
                                    : "text-[#b0b0b7] border-transparent hover:bg-[#141418]"
                            )}
                        >
                            <span>{item.icon}</span>
                            <span className="truncate">{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            <div className="mt-auto panel-soft p-4">
                {profile && (
                    <div className="mb-4">
                        <div className="flex justify-between text-xs muted mb-2">
                            <span>Career progress</span>
                            <span>{profile.career_progress}%</span>
                        </div>
                        <div className="progress-track">
                            <div className="progress-fill" style={{ width: `${profile.career_progress}%` }} />
                        </div>
                    </div>
                )}

                <div className="flex items-center gap-3 bg-[#0f0f12] p-3 rounded-xl border border-[#26262a]">
                    <div className="w-10 h-10 rounded-full bg-white text-black font-bold flex items-center justify-center">
                        {profile?.name ? profile.name.substring(0, 2).toUpperCase() : "U"}
                    </div>
                    <div className="min-w-0">
                        <div className="text-sm font-semibold truncate">{profile?.name || 'User'}</div>
                        <div className="text-xs muted truncate">{profile?.goal || 'Mentee'}</div>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
