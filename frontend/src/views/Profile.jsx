import React, { useState, useEffect } from 'react';
import { getProfile } from '../api';
import { Code, Terminal, Brain, HardDrive, Layout, ChevronRight, User } from 'lucide-react';

const levelColors = {
    advanced: 'bg-indigo-500 text-indigo-400',
    intermediate: 'bg-emerald-500 text-emerald-400',
    beginner: 'bg-blue-500 text-blue-400',
    none: 'bg-gray-500 text-gray-400'
};

const getLevelWidth = (level) => {
    switch (level) {
        case 'advanced': return '100%';
        case 'intermediate': return '66%';
        case 'beginner': return '33%';
        default: return '0%';
    }
};

const Profile = () => {
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

    if (!profile) return <div className="p-8">Error loading profile data</div>;

    return (
        <div className="p-8 max-w-5xl mx-auto w-full animate-fade-in flex flex-col h-full">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Skill Profile</h1>
                <p className="text-gray-400">View your current proficiency levels and career trajectory.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* User Stats Sidebar */}
                <div className="col-span-1 flex flex-col space-y-6">
                    <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] text-center">
                        <div className="w-24 h-24 bg-gradient-to-tr from-blue-500 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl font-bold text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]">
                            {profile.name.substring(0, 2).toUpperCase()}
                        </div>
                        <h2 className="text-xl font-bold text-white">{profile.name}</h2>
                        <p className="text-blue-400 font-medium text-sm mt-1">{profile.goal}</p>
                    </div>

                    <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37]">
                        <h3 className="text-gray-300 font-medium mb-4 flex items-center"><Terminal size={18} className="mr-2" /> Overall Stats</h3>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                    <span>Career Track Progress</span>
                                    <span>{profile.career_progress}%</span>
                                </div>
                                <div className="w-full bg-[#0f1115] rounded-full h-2">
                                    <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${profile.career_progress}%` }}></div>
                                </div>
                            </div>
                            <div className="pt-2 border-t border-[#2a2e37]">
                                <p className="text-sm text-gray-400 mb-1">Current Focus</p>
                                <div className="inline-block bg-purple-500/20 text-purple-400 px-3 py-1 text-sm rounded-lg font-medium">
                                    {profile.current_stage} Stage
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Skills Grid */}
                <div className="col-span-1 lg:col-span-2">
                    <div className="bg-[#181a20] rounded-2xl p-6 border border-[#2a2e37] h-full">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center"><Brain size={20} className="mr-2" /> Tech Stack Proficiency</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(profile.skills).map(([skill, level]) => (
                                <div key={skill} className="bg-[#0f1115] p-4 rounded-xl border border-[#2a2e37]">
                                    <div className="flex justify-between items-center mb-3">
                                        <span className="font-medium text-gray-200">{skill}</span>
                                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-opacity-20 ${levelColors[level]}`}>
                                            {level}
                                        </span>
                                    </div>
                                    <div className="w-full bg-[#181a20] rounded-full h-1.5 border border-[#1f2229]">
                                        <div
                                            className={`h-full rounded-full transition-all duration-1000 ${level === 'none' ? 'bg-gray-700' : 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]'}`}
                                            style={{ width: getLevelWidth(level) }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {Object.keys(profile.skills).length === 0 && (
                            <div className="text-center p-12 text-gray-500 border border-dashed border-[#2a2e37] rounded-xl">
                                <Code size={40} className="mx-auto mb-4 opacity-20" />
                                <p>No skills recorded yet.</p>
                                <p className="text-sm mt-2">Complete tasks to start building your profile.</p>
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Profile;
