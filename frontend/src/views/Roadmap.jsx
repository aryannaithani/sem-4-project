import React, { useEffect, useState } from 'react';
import { getFullRoadmap } from '../api';
import { Map, CheckCircle, ArrowRight, Lock, Unlock, Compass } from 'lucide-react';
import { clsx } from 'clsx';

const Roadmap = ({ setCurrentView }) => {
    const [roadmap, setRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getFullRoadmap()
            .then(data => setRoadmap(data))
            .catch(err => console.error("Error fetching full roadmap:", err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="p-8 w-full h-full flex justify-center items-center">
                <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!roadmap || !roadmap.stages) {
        return <div className="p-8 text-center text-slate-500">Could not load roadmap data.</div>;
    }

    // Determine current stage index based on exact name or first incomplete stage
    let currentStageObj = roadmap.stages.find(s => !s.complete);
    if (!currentStageObj) currentStageObj = roadmap.stages[roadmap.stages.length - 1]; // All complete

    return (
        <div className="p-8 max-w-5xl mx-auto w-full animate-fade-up">
            <header className="mb-12 flex justify-between items-end border-b border-white/5 pb-6">
                <div>
                    <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
                        <Map className="text-violet-500" size={32} />
                        Dynamic Roadmap
                    </h1>
                    <p className="text-slate-400">Your personalized path to becoming a <strong className="text-slate-200">{roadmap.goal}</strong>.</p>
                </div>
                <div className="text-right">
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">Current Focus</div>
                    <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-400 to-blue-400">{roadmap.current_stage}</div>
                </div>
            </header>

            <div className="relative border-l-2 border-white/10 ml-6 pb-8 space-y-12">
                {roadmap.stages.map((stage, idx) => {
                    const isCurrent = stage.name === roadmap.current_stage;
                    const isFuture = !stage.complete && !isCurrent;

                    return (
                        <div key={idx} className={clsx("relative pl-10 transition-all duration-500", !stage.complete && !isCurrent ? "opacity-60 grayscale hover:grayscale-0" : "")}>
                            {/* Node dot on timeline */}
                            <div className={clsx(
                                "absolute -left-[17px] top-1 w-8 h-8 rounded-full flex items-center justify-center border-4 border-bg-base shadow-lg z-10 transition-all",
                                stage.complete ? "bg-emerald-500" : isCurrent ? "bg-violet-500 shadow-glow" : "bg-slate-700"
                            )}>
                                {stage.complete ? <CheckCircle size={16} className="text-white" /> :
                                    isCurrent ? <Compass size={16} className="text-white" /> :
                                        <Lock size={14} className="text-slate-400" />}
                            </div>

                            <div className={clsx(
                                "card p-6 border transition-all",
                                isCurrent ? "border-violet-500/50 shadow-glow" : "border-white/5"
                            )}>
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                                            {stage.name}
                                            {isCurrent && <span className="text-[10px] uppercase tracking-wider font-bold bg-violet-500 text-white px-2 py-0.5 rounded ml-2">Active</span>}
                                        </h2>
                                        <p className="text-sm text-slate-400">
                                            {stage.learned} of {stage.total} skills mastered
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-3xl font-extrabold" style={{ color: stage.complete ? 'var(--emerald-400)' : isCurrent ? 'var(--violet-400)' : 'var(--text-muted)' }}>
                                            {stage.progress}%
                                        </div>
                                    </div>
                                </div>

                                <div className="progress-track w-full mb-6 bg-white/5">
                                    <div className={clsx(
                                        "progress-fill",
                                        stage.complete ? "bg-emerald-500" : "bg-violet-500"
                                    )} style={{ width: `${stage.progress}%` }}></div>
                                </div>

                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                    {stage.skills.map((skill, sIdx) => {
                                        const known = skill.level !== 'none' && skill.level !== 'absent';
                                        return (
                                            <div key={sIdx} className={clsx(
                                                "p-3 rounded-lg border text-sm font-medium flex items-center gap-2 transition-colors",
                                                known ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
                                                    : "bg-white/5 border-white/5 text-slate-300"
                                            )}>
                                                {known ? <CheckCircle size={14} className="min-w-fit" /> : <Circle size={14} className="text-slate-500 min-w-fit" />}
                                                <span className="truncate">{skill.name}</span>
                                            </div>
                                        );
                                    })}
                                </div>

                                {isCurrent && (
                                    <div className="mt-6 pt-5 border-t border-white/5 flex justify-end">
                                        <button
                                            onClick={() => setCurrentView && setCurrentView('tasks')}
                                            className="btn btn-primary text-sm shadow-glow"
                                        >
                                            Generate Tasks for {stage.name} <ArrowRight size={14} />
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
            {roadmap.stages.every(s => s.complete) && (
                <div className="mt-8 card-glass p-8 text-center border-emerald-500/30">
                    <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Unlock size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">You've mastered this roadmap!</h2>
                    <p className="text-slate-400 mb-6">You've attained the skills required for a {roadmap.goal}. Time to update your goal in profile.</p>
                </div>
            )}
        </div>
    );
};

// Also inline a simple Circle icon if we didn't import it
const Circle = ({ size, className }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <circle cx="12" cy="12" r="10"></circle>
    </svg>
);

export default Roadmap;
