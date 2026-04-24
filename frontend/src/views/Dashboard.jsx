import React, { useEffect, useState } from 'react';
import { getProfile, getAnalytics } from '../api';
import { Target, TrendingUp, Award, ArrowRight, Zap, Target as TargetIcon } from 'lucide-react';
import TrendFeed from '../components/TrendFeed';

const Dashboard = ({ setCurrentView }) => {
    const [profile, setProfile] = useState(null);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [pData, aData] = await Promise.all([
                    getProfile(),
                    getAnalytics()
                ]);
                setProfile(pData);
                setAnalytics(aData);
            } catch (error) {
                console.error("Failed to load dashboard data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="p-4 md:p-8 w-full h-full flex flex-col justify-center items-center gap-4">
                <div className="w-12 h-12 border-4 border-white/10 border-t-violet-500 rounded-full animate-spin shadow-[0_0_15px_rgba(124,58,237,0.5)]"></div>
                <div className="text-slate-400 font-medium animate-pulse">Loading dashboard...</div>
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="p-4 md:p-8 w-full h-full flex justify-center items-center">
                <div className="card max-w-md w-full p-8 text-center shadow-2xl border-white/10 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-orange-500/5 z-0 pointer-events-none"></div>
                    <div className="relative z-10">
                        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4 border border-red-500/20 text-red-400">
                            <Target size={28} />
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">Data Unavailable</h2>
                        <p className="text-slate-400 text-sm mb-6">We couldn't connect to the mentor backend. Ensure the FastAPI server is running.</p>
                        <button onClick={() => window.location.reload()} className="btn btn-secondary w-full justify-center">Try Again</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="py-8 px-4 md:px-8 max-w-6xl mx-auto w-full animate-fade-up">
            <header className="mb-10 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-extrabold text-white mb-2">Welcome back, <span className="gradient-text">{profile.name}</span></h1>
                    <p className="text-slate-400">Your digital twin is tracking your progress towards becoming a <strong className="text-slate-200">{profile.goal}</strong>.</p>
                </div>
                {analytics && (
                    <div className="text-right">
                        <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Real-World Readiness</div>
                        <div className="text-3xl font-extrabold gradient-text-green">{analytics.real_world_readiness}%</div>
                    </div>
                )}
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 stagger">
                {/* Goal Card */}
                <div className="stat-card">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TargetIcon size={80} />
                    </div>
                    <div className="flex items-center gap-2 mb-2 text-violet-400">
                        <Target size={18} />
                        <span className="text-xs font-bold uppercase tracking-wider">Current Goal</span>
                    </div>
                    <div className="text-2xl font-bold text-white mb-6">{profile.goal || "Not set"}</div>
                    <button
                        onClick={() => setCurrentView('profile')}
                        className="btn btn-secondary w-full justify-center text-xs border-violet-500/20 hover:border-violet-500/50"
                    >
                        View Digital Twin <ArrowRight size={14} />
                    </button>
                </div>

                {/* Global Progress Card */}
                <div className="stat-card">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TrendingUp size={80} />
                    </div>
                    <div className="flex items-center gap-2 mb-2 text-emerald-400">
                        <TrendingUp size={18} />
                        <span className="text-xs font-bold uppercase tracking-wider">Overall Progress</span>
                    </div>
                    <div className="stat-value text-emerald-400 mb-4">{profile.career_progress}%</div>
                    <div className="progress-track w-full mt-auto">
                        <div className="progress-fill progress-fill-green" style={{ width: `${profile.career_progress}%` }}></div>
                    </div>
                </div>

                {/* Current Stage Card */}
                <div className="stat-card">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Award size={80} />
                    </div>
                    <div className="flex items-center gap-2 mb-2 text-blue-400">
                        <Award size={18} />
                        <span className="text-xs font-bold uppercase tracking-wider">Current Stage</span>
                    </div>
                    <div className="text-xl font-bold text-white mb-4">{profile.current_stage || "Unknown"}</div>
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-400 mb-2">
                        <span>Stage Progress</span>
                        <span>{profile.stage_progress || 0}%</span>
                    </div>
                    <div className="progress-track w-full mt-auto">
                        <div className="progress-fill" style={{ width: `${profile.stage_progress || 0}%` }}></div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 stagger">
                <div className="lg:col-span-2 space-y-6">
                    {/* Action Spotlight */}
                    <div className="card-glass p-8 border-violet-500/20 shadow-glow relative overflow-hidden">
                        <div className="absolute -right-10 -top-10 text-violet-500/10">
                            <Zap size={200} />
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2 relative z-10">Ready for your next challenge?</h2>
                        <p className="text-slate-300 mb-6 max-w-lg relative z-10 text-sm">
                            Your mentor has curated specific tasks to close your gaps and boost your real-world readiness.
                        </p>
                        <div className="flex gap-4 relative z-10">
                            <button onClick={() => setCurrentView('tasks')} className="btn btn-primary btn-lg shadow-glow">
                                Open Task Board <ArrowRight size={18} />
                            </button>
                            <button onClick={() => setCurrentView('chat')} className="btn btn-secondary btn-lg">
                                Ask Mentor
                            </button>
                        </div>
                    </div>

                    {/* Basic Analytics Summary */}
                    {analytics && (
                        <div className="grid grid-cols-2 gap-4">
                            <div className="card p-5">
                                <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Career Trajectory</div>
                                <div className="text-lg font-bold text-white capitalize">{analytics.career_trajectory}</div>
                            </div>
                            <div className="card p-5">
                                <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Trend Alignment</div>
                                <div className="text-lg font-bold text-white">{analytics.trend_alignment_score}%</div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="lg:col-span-1">
                    <TrendFeed />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
