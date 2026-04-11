import React, { useEffect, useState } from 'react';
import { getProfile } from '../api';
import { Target, TrendingUp, Award, ArrowRight } from 'lucide-react';

const Dashboard = ({ setCurrentView }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await getProfile();
                setProfile(data);
            } catch (error) {
                console.error("Failed to load profile", error);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    if (loading) {
        return (
            <div className="p-8 w-full h-full flex justify-center items-center">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!profile) {
        return <div className="p-8 text-center text-gray-500">Could not load dashboard data.</div>;
    }

    return (
        <div className="p-8 max-w-5xl mx-auto w-full animate-fade-in">
            <header className="mb-10">
                <h1 className="text-3xl font-bold text-white mb-2">Welcome back, {profile.name}</h1>
                <p className="text-gray-400">Here's your career progress at a glance.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {/* Goal Card */}
                <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] shadow-lg flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Target size={60} />
                    </div>
                    <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Current Goal</p>
                    <div className="text-xl font-bold text-blue-400 mb-4">{profile.goal || "Not set"}</div>
                    <div className="mt-auto flex items-center text-sm text-gray-500 hover:text-blue-400 cursor-pointer transition" onClick={() => setCurrentView('profile')}>
                        View Skills <ArrowRight size={14} className="ml-1" />
                    </div>
                </div>

                {/* Global Progress Card */}
                <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] shadow-lg flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TrendingUp size={60} />
                    </div>
                    <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Overall Progress</p>
                    <div className="flex items-end mb-4">
                        <span className="text-3xl font-bold text-emerald-400">{profile.career_progress}%</span>
                    </div>
                    <div className="w-full bg-[#0f1115] rounded-full h-2 mt-auto">
                        <div className="bg-emerald-500 h-2 rounded-full transition-all duration-1000" style={{ width: `${profile.career_progress}%` }}></div>
                    </div>
                </div>

                {/* Current Stage Card */}
                <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] shadow-lg flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Award size={60} />
                    </div>
                    <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">Current Stage</p>
                    <div className="text-xl font-bold text-purple-400 mb-4">{profile.current_stage || "Unknown"}</div>
                    <div className="w-full bg-[#0f1115] rounded-full h-2 mt-auto mb-2">
                        <div className="bg-purple-500 h-2 rounded-full transition-all duration-1000" style={{ width: `${profile.stage_progress || 0}%` }}></div>
                    </div>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>Stage Progress</span>
                        <span>{profile.stage_progress || 0}%</span>
                    </div>
                </div>
            </div>

            {/* Mini Task Preview or Actions */}
            <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] shadow-lg">
                <h2 className="text-lg font-bold text-white mb-4 flex justify-between items-center">
                    <span>Quick Actions</span>
                </h2>
                <div className="flex gap-4">
                    <button
                        onClick={() => setCurrentView('tasks')}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:shadow-[0_0_20px_rgba(59,130,246,0.5)]">
                        Go to Tasks
                    </button>
                    <button
                        onClick={() => setCurrentView('roadmap')}
                        className="px-6 py-3 bg-[#2a2e37] hover:bg-[#3f4555] text-white font-medium rounded-xl transition-all">
                        View Roadmap
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
