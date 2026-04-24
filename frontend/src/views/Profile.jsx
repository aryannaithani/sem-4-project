import React, { useEffect, useState } from 'react';
import { getProfile, getLearningProfile } from '../api';
import { User as UserIcon, GitBranch, Clock, ShieldCheck, Target, Activity } from 'lucide-react';
import { clsx } from 'clsx';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [learningProfile, setLearningProfile] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([getProfile(), getLearningProfile()])
            .then(([p, lp]) => {
                setProfile(p);
                setLearningProfile(lp);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="p-4 md:p-8 w-full h-full flex flex-col justify-center items-center gap-4">
                <div className="w-12 h-12 border-4 border-white/10 border-t-violet-500 rounded-full animate-spin shadow-[0_0_15px_rgba(124,58,237,0.5)]"></div>
                <div className="text-slate-400 font-medium animate-pulse">Loading digital twin...</div>
            </div>
        );
    }

    if (!profile || !learningProfile) {
        return (
            <div className="p-4 md:p-8 w-full h-full flex justify-center items-center">
                <div className="card max-w-md w-full p-8 text-center shadow-2xl border-white/10">
                    <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4 border border-red-500/20 text-red-400">
                        <UserIcon size={28} />
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">Profile Unavailable</h2>
                    <p className="text-slate-400 text-sm mb-6">Could not load digital twin data. Ensure the backend is active.</p>
                    <button onClick={() => window.location.reload()} className="btn btn-secondary w-full justify-center">Try Again</button>
                </div>
            </div>
        );
    }

    // Prepare Skill Radar Chart Data
    // We'll pick the top 6-8 skills and map "beginner"=33 "intermediate"=66 "advanced"=100
    const topSkills = Object.entries(profile.skills)
        .filter(([, level]) => level !== 'none' && level !== 'absent')
        .slice(0, 6);

    // Fill up to 6 properties if short
    while (topSkills.length > 0 && topSkills.length < 6) {
        topSkills.push([`Placeholder ${topSkills.length}`, "none"]);
    }

    const levelToNum = (level) => {
        if (level === 'advanced') return 100;
        if (level === 'intermediate') return 60;
        if (level === 'beginner') return 25;
        return 0;
    };

    // Calculate radar points
    const drawRadar = (radius, cx, cy) => {
        if (topSkills.length === 0) return '';
        const angleStep = (Math.PI * 2) / topSkills.length;
        const pts = topSkills.map((st, i) => {
            const val = levelToNum(st[1]) / 100;
            const r = radius * val;
            const x = cx + r * Math.sin(i * angleStep);
            const y = cy - r * Math.cos(i * angleStep);
            return `${x},${y}`;
        }).join(' ');
        return pts;
    };

    const drawGrid = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        return Array.from({ length: 4 }).map((_, level) => {
            const r = radius * ((level + 1) / 4);
            const angleStep = (Math.PI * 2) / numSides;
            const pts = Array.from({ length: numSides }).map((_, i) => {
                const x = cx + r * Math.sin(i * angleStep);
                const y = cy - r * Math.cos(i * angleStep);
                return `${x},${y}`;
            }).join(' ');
            return <polygon key={level} points={pts} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />;
        });
    };

    const drawAxes = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        const angleStep = (Math.PI * 2) / numSides;
        return Array.from({ length: numSides }).map((_, i) => {
            const x = cx + radius * Math.sin(i * angleStep);
            const y = cy - radius * Math.cos(i * angleStep);
            return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />;
        });
    };

    const renderLabels = (radius, cx, cy, numSides) => {
        if (numSides < 3) return null;
        const angleStep = (Math.PI * 2) / numSides;
        return topSkills.map(([skill], i) => {
            const x = cx + (radius + 20) * Math.sin(i * angleStep);
            const y = cy - (radius + 20) * Math.cos(i * angleStep);
            return (
                <text key={i} x={x} y={y} fontSize="10" fill="#94a3b8" textAnchor="middle" dominantBaseline="middle">
                    {skill.length > 15 ? skill.substring(0, 12) + '...' : skill}
                </text>
            );
        });
    }

    return (
        <div className="p-8 max-w-6xl mx-auto w-full animate-fade-up">
            <header className="mb-10 flex items-center gap-5">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-violet-600 to-blue-600 flex items-center justify-center text-white text-2xl font-bold shadow-glow">
                    {profile.name.substring(0, 2).toUpperCase()}
                </div>
                <div>
                    <h1 className="text-3xl font-extrabold text-white">{profile.name}'s Digital Twin</h1>
                    <p className="text-slate-400 flex items-center gap-2 mt-1">
                        <Target size={14} /> Goal: <span className="text-slate-200">{profile.goal}</span>
                        {profile.github && <><span className="mx-2 text-white/20">|</span> <GitBranch size={14} /> {profile.github}</>}
                    </p>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 stagger">

                {/* Learning Profile Summary */}
                <div className="card p-6 flex flex-col gap-6">
                    <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Learning Characteristics</h2>

                    <div className="flex flex-col gap-4">
                        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                            <div className="text-xs text-slate-400 mb-1 flex items-center gap-2"><Clock size={14} /> Learning Velocity</div>
                            <div className="text-2xl font-bold text-emerald-400">{learningProfile.learning_velocity} <span className="text-xs text-slate-500 font-normal">tasks/day</span></div>
                        </div>

                        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                            <div className="text-xs text-slate-400 mb-1 flex items-center gap-2"><Activity size={14} /> Consistency Score</div>
                            <div className="flex items-end gap-3">
                                <div className="text-2xl font-bold text-blue-400">{learningProfile.consistency_score}%</div>
                                <div className="flex-1 mb-2 progress-track">
                                    <div className="progress-fill" style={{ width: `${learningProfile.consistency_score}%` }}></div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                            <div className="text-xs text-slate-400 mb-1 flex items-center gap-2"><ShieldCheck size={14} /> Project Complexity Index</div>
                            <div className="flex items-end gap-3">
                                <div className="text-2xl font-bold text-violet-400">{learningProfile.project_complexity_index}</div>
                                <div className="flex-1 mb-2 progress-track">
                                    <div className="progress-fill" style={{ width: `${learningProfile.project_complexity_index}%`, background: 'var(--gradient-primary)' }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Radar Chart */}
                <div className="lg:col-span-2 card p-6 flex flex-col items-center justify-center relative">
                    <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 absolute top-6 left-6">Skill Profile Shape</h2>
                    {topSkills.length >= 3 ? (
                        <div className="w-full h-80 max-w-sm mt-8">
                            <svg viewBox="0 0 300 300" className="w-full h-full overflow-visible">
                                <defs>
                                    <linearGradient id="radarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="rgba(124,58,237,0.4)" />
                                        <stop offset="100%" stopColor="rgba(59,130,246,0.3)" />
                                    </linearGradient>
                                </defs>
                                {drawGrid(100, 150, 150, topSkills.length)}
                                {drawAxes(100, 150, 150, topSkills.length)}
                                <polygon
                                    points={drawRadar(100, 150, 150)}
                                    fill="url(#radarGrad)"
                                    stroke="#8b5cf6"
                                    strokeWidth="2"
                                />
                                {renderLabels(100, 150, 150, topSkills.length)}
                                {topSkills.map((st, i) => {
                                    const val = levelToNum(st[1]) / 100;
                                    const r = 100 * val;
                                    const angleStep = (Math.PI * 2) / topSkills.length;
                                    const x = 150 + r * Math.sin(i * angleStep);
                                    const y = 150 - r * Math.cos(i * angleStep);
                                    return <circle key={i} cx={x} cy={y} r="3" fill="#ffffff" />;
                                })}
                            </svg>
                        </div>
                    ) : (
                        <div className="text-slate-500 text-sm">Need at least 3 skills to show the radar profile.</div>
                    )}
                </div>

            </div>

            {/* Raw skills list */}
            <div className="mt-8 card p-6 stagger">
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-6">Complete Skill Inventory</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(profile.skills).filter(([, l]) => l !== 'none' && l !== 'absent').map(([skill, level], idx) => (
                        <div key={idx} className="bg-white/5 border border-white/5 p-3 rounded-lg flex flex-col gap-2">
                            <span className="font-semibold text-slate-200 text-sm">{skill}</span>
                            <div className="flex items-center gap-2">
                                <span className={clsx(
                                    "w-2 h-2 rounded-full",
                                    level === 'beginner' ? 'bg-emerald-500' :
                                        level === 'intermediate' ? 'bg-orange-500' :
                                            'bg-violet-500'
                                )}></span>
                                <span className="text-xs text-slate-400 capitalize">{level}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Profile;
