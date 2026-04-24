import React, { useEffect, useState } from 'react';
import { getAnalytics } from '../api';
import { Activity, Target, TrendingUp, Layers, AlertCircle, CheckCircle } from 'lucide-react';

const Analytics = () => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getAnalytics()
            .then(data => setAnalytics(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="p-8 w-full h-full flex justify-center items-center">
                <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!analytics) {
        return <div className="p-8 text-center text-slate-500">Could not load analytics.</div>;
    }

    // Prepare history data for simple SVG chart
    const history = analytics.readiness_history || [];
    const minVal = Math.min(...history.map(h => h.score), 0);
    const maxVal = 100;

    // Scale history to 0-1 range for plotting
    const pts = history.map((h, i) => {
        const x = history.length > 1 ? (i / (history.length - 1)) * 100 : 50;
        const y = 100 - ((h.score - minVal) / ((maxVal - minVal) || 1)) * 100;
        return `${x},${y}`;
    }).join(' ');

    return (
        <div className="p-8 max-w-6xl mx-auto w-full animate-fade-up">
            <header className="mb-10">
                <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
                    <Activity className="text-violet-500" size={32} />
                    Career Analytics
                </h1>
                <p className="text-slate-400">Deep insights into your real-world readiness and trajectory.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 stagger">
                <div className="stat-card">
                    <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-2">
                        <Target size={16} /> Readiness
                    </div>
                    <div className="text-4xl font-extrabold text-white">
                        {analytics.real_world_readiness}%
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Overall preparedness score</p>
                </div>

                <div className="stat-card">
                    <div className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2 flex items-center gap-2">
                        <TrendingUp size={16} /> Trajectory
                    </div>
                    <div className="text-2xl font-bold text-white capitalize mt-2">
                        {analytics.career_trajectory}
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Based on recent activity</p>
                </div>

                <div className="stat-card">
                    <div className="text-xs font-bold uppercase tracking-wider text-orange-400 mb-2 flex items-center gap-2">
                        <Layers size={16} /> Alignment
                    </div>
                    <div className="text-3xl font-extrabold text-white mt-1">
                        {analytics.trend_alignment_score}%
                    </div>
                    <p className="text-xs text-slate-400 mt-2">Skills aligned with trends</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 stagger">
                {/* Trajectory Graph */}
                <div className="lg:col-span-2 card p-8">
                    <h2 className="text-lg font-bold text-white mb-6">Readiness Trajectory</h2>
                    {history.length > 1 ? (
                        <div className="w-full h-48 relative border-b border-l border-white/10">
                            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                                <defs>
                                    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#7c3aed" />
                                        <stop offset="100%" stopColor="#3b82f6" />
                                    </linearGradient>
                                </defs>
                                <polyline
                                    fill="none"
                                    stroke="url(#lineGrad)"
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    points={pts}
                                />
                                {history.map((h, i) => {
                                    const x = (i / (history.length - 1)) * 100;
                                    const y = 100 - ((h.score - minVal) / ((maxVal - minVal) || 1)) * 100;
                                    return (
                                        <circle
                                            key={i}
                                            cx={x}
                                            cy={y}
                                            r="2.5"
                                            fill="#0d1117"
                                            stroke="#3b82f6"
                                            strokeWidth="1.5"
                                        >
                                            <title>{h.date.substring(0, 10)}: {h.score}%</title>
                                        </circle>
                                    );
                                })}
                            </svg>
                        </div>
                    ) : (
                        <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
                            Need more data points to show trajectory. Keep completing tasks!
                        </div>
                    )}
                </div>

                {/* Depth Breakdown */}
                <div className="card p-6 flex flex-col">
                    <h2 className="text-lg font-bold text-white mb-4">Skill Depth</h2>
                    <div className="flex-1 space-y-4 overflow-y-auto pr-2">
                        {Object.entries(analytics.skill_depth_breakdown || {}).length === 0 ? (
                            <p className="text-slate-500 text-sm">No skills tracked yet.</p>
                        ) : (
                            Object.entries(analytics.skill_depth_breakdown).map(([skill, info], idx) => (
                                <div key={idx} className="flex flex-col gap-1 border-b border-white/5 pb-2">
                                    <div className="flex justify-between items-center text-sm">
                                        <span className="font-semibold text-slate-200">{skill}</span>
                                        {info.depth === 'deep' && <span className="badge badge-advanced">Deep</span>}
                                        {info.depth === 'developing' && <span className="badge badge-blue">Developing</span>}
                                        {info.depth === 'surface' && <span className="badge badge-intermediate">Surface</span>}
                                    </div>
                                    <div className="flex justify-between items-center text-xs text-slate-400">
                                        <span className="capitalize">{info.level}</span>
                                        {info.confidence ? <span>Conf: {info.confidence}/5</span> : <span>No conf</span>}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 stagger">
                <div className="card-glass p-6 border-emerald-500/20 max-h-64 overflow-y-auto">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-4 flex items-center gap-2">
                        <CheckCircle size={16} /> Top Strengths
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {analytics.top_strength_skills?.length > 0 ? (
                            analytics.top_strength_skills.map((s, i) => (
                                <span key={i} className="px-3 py-1.5 bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 rounded-md text-sm font-medium">
                                    {s}
                                </span>
                            ))
                        ) : (
                            <span className="text-slate-500 text-sm">No deep strengths identified yet.</span>
                        )}
                    </div>
                </div>

                <div className="card-glass p-6 border-orange-500/20 max-h-64 overflow-y-auto">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                        <AlertCircle size={16} /> Highest Priority Gaps
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {analytics.highest_priority_gaps?.length > 0 ? (
                            analytics.highest_priority_gaps.map((s, i) => (
                                <span key={i} className="px-3 py-1.5 bg-orange-500/10 text-orange-300 border border-orange-500/20 rounded-md text-sm font-medium">
                                    {s}
                                </span>
                            ))
                        ) : (
                            <span className="text-slate-500 text-sm">No critical gaps identified right now.</span>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
};

export default Analytics;
