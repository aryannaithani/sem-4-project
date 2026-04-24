import React, { useEffect, useState } from 'react';
import { LayoutDashboard, CheckSquare, Map, User, MessageSquare, Activity } from 'lucide-react';
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
        <aside className="w-64 h-screen bg-[#0d1117] border-r border-[#ffffff10] flex flex-col py-6 px-4 shrink-0 relative overflow-hidden transition-all duration-300 z-50">
            <div className="absolute inset-0 bg-gradient-to-b from-violet-500/5 to-transparent pointer-events-none"></div>

            {/* Brand */}
            <div className="flex items-center gap-3 mb-10 w-full px-2 relative z-10 shrink-0">
                <div className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)]">
                    <Map className="text-white" size={20} strokeWidth={2.5} />
                </div>
                <div className="flex-1 min-w-0">
                    <h1 className="text-base font-bold tracking-tight text-white leading-tight truncate block">AI Career<br />Mentor</h1>
                </div>
            </div>

            {/* Navigation */}
            <nav className="w-full flex-1 space-y-1 relative z-10 overflow-y-auto scroll-area pr-1">
                {navItems.map((item) => {
                    const isActive = currentView === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setCurrentView(item.id)}
                            className={clsx(
                                "interactive w-full flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-semibold transition-all duration-200 text-left",
                                isActive
                                    ? "bg-violet-500/10 text-violet-400 border border-violet-500/20 shadow-[inset_0_0_12px_rgba(124,58,237,0.05)]"
                                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent"
                            )}
                        >
                            <span className={clsx("shrink-0 transition-transform duration-200 flex items-center justify-center w-5 h-5", isActive ? "scale-110 text-violet-400 drop-shadow-md" : "")}>
                                {item.icon}
                            </span>
                            <span className="truncate flex-1 min-w-0">{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            {/* Profile Section */}
            <div className="w-full pt-6 border-t border-[#ffffff10] relative z-10 shrink-0">
                {profile && (
                    <div className="mb-4 px-2">
                        <div className="flex justify-between items-center text-xs font-semibold text-slate-400 mb-2">
                            <span className="truncate pr-2">Career Progress</span>
                            <span className="text-emerald-400 shrink-0">{profile.career_progress}%</span>
                        </div>
                        <div className="progress-track w-full overflow-hidden">
                            <div className="progress-fill progress-fill-green" style={{ width: `${profile.career_progress}%` }}></div>
                        </div>
                    </div>
                )}

                <div className="flex items-center gap-3 mt-4 bg-white/5 p-3 rounded-xl border border-white/5 w-full">
                    <div className="shrink-0 w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm shadow-md ring-2 ring-violet-500/20">
                        {profile?.name ? profile.name.substring(0, 2).toUpperCase() : "U"}
                    </div>
                    <div className="flex flex-col flex-1 min-w-0">
                        <span className="text-sm font-bold text-white truncate w-full block leading-tight">{profile?.name || "User"}</span>
                        <span className="text-xs text-violet-300 font-medium truncate w-full block mt-0.5">{profile?.goal || "Mentee"}</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
