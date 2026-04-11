import React, { useState, useEffect } from 'react';
import { getRoadmap } from '../api';
import { Map, MapPin, Check, Lock, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';

const stages = ['Foundations', 'Intermediate', 'Advanced'];

const Roadmap = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRoadmap = async () => {
            try {
                const res = await getRoadmap();
                setData(res);
            } catch (error) {
                console.error("Failed to load roadmap", error);
            } finally {
                setLoading(false);
            }
        };
        fetchRoadmap();
    }, []);

    if (loading) {
        return (
            <div className="p-8 w-full h-full flex justify-center items-center">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!data) return <div className="p-8">Error loading roadmap</div>;

    const currentStageIndex = stages.indexOf(data.current_stage);

    return (
        <div className="p-8 max-w-4xl mx-auto w-full animate-fade-in pb-20">
            <header className="mb-12">
                <h1 className="text-3xl font-bold text-white mb-2">Career Roadmap</h1>
                <p className="text-gray-400">Track your linear progression through career stages.</p>
            </header>

            <div className="relative">
                {/* Connecting line */}
                <div className="absolute left-6 top-10 bottom-10 w-1 bg-[#1f2229] rounded-full">
                    <div
                        className="w-full bg-blue-500 rounded-full transition-all duration-1000"
                        style={{ height: `${(currentStageIndex / (stages.length - 1)) * 100}%` }}
                    ></div>
                </div>

                <div className="space-y-12">
                    {stages.map((stageTitle, index) => {
                        const isCompleted = index < currentStageIndex;
                        const isCurrent = index === currentStageIndex;
                        const isLocked = index > currentStageIndex;

                        return (
                            <div key={stageTitle} className={clsx("relative pl-16 transition-all duration-500", isLocked ? "opacity-50" : "opacity-100")}>

                                {/* Node */}
                                <div className={clsx(
                                    "absolute left-2.5 -ml-px top-6 w-8 h-8 rounded-full border-4 flex items-center justify-center z-10 transition-all duration-500 shadow-lg",
                                    isCompleted ? "bg-emerald-500 border-[#0f1115]" :
                                        isCurrent ? "bg-blue-500 border-[#0f1115] shadow-blue-500/50" :
                                            "bg-[#181a20] border-[#2a2e37]"
                                )}>
                                    {isCompleted && <Check size={14} className="text-white" />}
                                    {isCurrent && <MapPin size={14} className="text-white" />}
                                    {isLocked && <Lock size={12} className="text-gray-500" />}
                                </div>

                                {/* Content Card */}
                                <div className={clsx(
                                    "bg-[#181a20] rounded-2xl p-6 border transition-all duration-300",
                                    isCurrent ? "border-blue-500 border-opacity-50 shadow-[0_0_15px_rgba(59,130,246,0.15)]" : "border-[#2a2e37]"
                                )}>
                                    <div className="flex justify-between items-center mb-4">
                                        <h2 className="text-xl font-bold text-white">{stageTitle}</h2>
                                        {isCurrent && (
                                            <span className="bg-blue-500 bg-opacity-20 text-blue-400 text-xs px-3 py-1 rounded-full font-bold">
                                                Current Stage
                                            </span>
                                        )}
                                        {isCompleted && (
                                            <span className="text-emerald-500 text-sm font-medium flex items-center">
                                                <Check size={16} className="mr-1" /> Completed
                                            </span>
                                        )}
                                    </div>

                                    {isCurrent && (
                                        <div className="mb-6">
                                            <div className="flex justify-between text-sm text-gray-400 mb-2">
                                                <span>Stage Mastery</span>
                                                <span>{data.stage_progress || 0}%</span>
                                            </div>
                                            <div className="w-full bg-[#0f1115] rounded-full h-3 border border-[#2a2e37]">
                                                <div
                                                    className="bg-blue-500 h-full rounded-full transition-all duration-1000"
                                                    style={{ width: `${data.stage_progress || 0}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    )}

                                    <p className="text-gray-500 text-sm">
                                        {isCompleted ? "You have mastered the core requirements for this stage." :
                                            isCurrent ? "Focus on currently assigned tasks to build proficiency and unlock the next stage." :
                                                "This stage is currently locked. Complete previous stages to access advanced skill building."}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default Roadmap;
