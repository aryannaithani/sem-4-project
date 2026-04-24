import React, { useState, useEffect } from 'react';
import { getTasks, completeTask, generateTasks } from '../api';
import { CheckCircle, Circle, RefreshCw, Zap, Bookmark, Clock, Flag, Layout, Flame } from 'lucide-react';
import { clsx } from 'clsx';

const TaskBoard = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            setLoading(true);
            const data = await getTasks();
            setTasks(data?.tasks || []);
        } catch (error) {
            console.error("Error fetching tasks:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        try {
            setGenerating(true);
            const data = await generateTasks();
            if (data.tasks) {
                setTasks(data.tasks);
            } else {
                await fetchTasks();
            }
        } catch (error) {
            console.error("Error generating tasks:", error);
        } finally {
            setGenerating(false);
        }
    };

    const handleCompleteTask = async (taskId) => {
        try {
            const data = await completeTask(taskId);
            if (data.updated_tasks) {
                setTasks(data.updated_tasks);
            } else {
                await fetchTasks();
            }
        } catch (error) {
            console.error("Error completing task:", error);
        }
    };

    if (loading) {
        return (
            <div className="p-8 w-full h-full flex justify-center items-center">
                <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    let pendingTasks = tasks.filter(t => t.status === 'pending');
    if (filter !== 'all') {
        pendingTasks = pendingTasks.filter(t => (t.difficulty || 'beginner') === filter);
    }
    const completedTasks = tasks.filter(t => t.status === 'completed');

    return (
        <div className="p-8 max-w-7xl mx-auto w-full animate-fade-up flex flex-col h-full h-screen">
            <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4 shrink-0">
                <div>
                    <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
                        <Layout className="text-violet-500" size={32} />
                        Task Board
                    </h1>
                    <p className="text-slate-400">Complete project-based tasks to build your real-world readiness.</p>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-4">
                    <div className="flex bg-white/5 p-1 rounded-lg border border-white/5">
                        <button onClick={() => setFilter('all')} className={clsx("px-4 py-1.5 rounded-md text-sm font-medium transition-all", filter === 'all' ? "bg-white/10 text-white shadow-sm" : "text-slate-400 hover:text-slate-200")}>All</button>
                        <button onClick={() => setFilter('beginner')} className={clsx("px-4 py-1.5 rounded-md text-sm font-medium transition-all", filter === 'beginner' ? "bg-emerald-500/20 text-emerald-400 shadow-sm" : "text-slate-400 hover:text-slate-200")}>Beginner</button>
                        <button onClick={() => setFilter('intermediate')} className={clsx("px-4 py-1.5 rounded-md text-sm font-medium transition-all", filter === 'intermediate' ? "bg-orange-500/20 text-orange-400 shadow-sm" : "text-slate-400 hover:text-slate-200")}>Intermediate</button>
                        <button onClick={() => setFilter('advanced')} className={clsx("px-4 py-1.5 rounded-md text-sm font-medium transition-all", filter === 'advanced' ? "bg-red-500/20 text-red-400 shadow-sm" : "text-slate-400 hover:text-slate-200")}>Advanced</button>
                    </div>

                    <button
                        onClick={handleGenerate}
                        disabled={generating}
                        className="btn btn-primary shadow-glow"
                    >
                        {generating ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
                        <span>{generating ? 'Generating...' : 'Generate AI Tasks'}</span>
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0 pb-6 stagger">

                {/* Pending Tasks Column */}
                <div className="flex flex-col bg-bg-surface rounded-2xl border border-white/5 overflow-hidden shadow-lg h-full">
                    <div className="p-4 border-b border-white/5 bg-black/20 flex justify-between items-center backdrop-blur-md">
                        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Pending Execution</h2>
                        <span className="bg-violet-500/20 text-violet-400 text-xs px-2.5 py-0.5 rounded-full font-bold border border-violet-500/30">
                            {pendingTasks.length}
                        </span>
                    </div>
                    <div className="p-4 overflow-y-auto scroll-area flex-1 space-y-4">
                        {pendingTasks.length === 0 ? (
                            <div className="text-center p-12 text-slate-500 flex flex-col items-center">
                                <Bookmark size={48} className="mb-4 opacity-20" />
                                <p>No {filter !== 'all' ? filter : ''} pending tasks.</p>
                                <button onClick={handleGenerate} className="mt-4 text-violet-400 hover:text-violet-300 text-sm font-medium">Generate your next challenge</button>
                            </div>
                        ) : (
                            pendingTasks.map((task) => (
                                <div key={task.id} className="card p-5 hover:border-violet-500/30 group">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <span className="badge badge-accent">
                                                {task.skill}
                                            </span>
                                            {task.trend_alignment && (
                                                <span className="text-[10px] uppercase font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-sm border border-emerald-500/20 flex items-center gap-1">
                                                    <Flame size={12} /> Trending
                                                </span>
                                            )}
                                        </div>
                                        <span className={clsx(
                                            "badge",
                                            task.difficulty === 'advanced' ? "badge-advanced" :
                                                task.difficulty === 'intermediate' ? "badge-intermediate" :
                                                    "badge-beginner"
                                        )}>
                                            {task.difficulty || 'beginner'}
                                        </span>
                                    </div>
                                    <h3 className="text-white font-semibold mb-3 leading-snug text-lg">{task.task}</h3>

                                    <div className="text-sm text-slate-400 mb-6 bg-white/5 p-3 rounded-lg border border-white/5">
                                        <p className="font-medium text-slate-300 mb-1 flex items-center gap-2">
                                            <Flag size={14} className="text-blue-400" /> Context
                                        </p>
                                        <p>{task.reason}</p>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <button
                                            onClick={() => handleCompleteTask(task.id)}
                                            className="flex-1 btn btn-secondary border-emerald-500/20 hover:border-emerald-500 hover:bg-emerald-500/10 hover:text-emerald-400"
                                        >
                                            <Circle size={18} className="group-hover:hidden" />
                                            <CheckCircle size={18} className="hidden group-hover:block" />
                                            Mark as Complete
                                        </button>

                                        {task.estimated_hours && (
                                            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 bg-black/20 px-3 py-2 rounded-lg border border-white/5">
                                                <Clock size={14} /> {task.estimated_hours}h
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Completed Tasks Column */}
                <div className="flex flex-col bg-bg-surface rounded-2xl border border-white/5 overflow-hidden shadow-lg h-full">
                    <div className="p-4 border-b border-white/5 bg-black/20 flex justify-between items-center backdrop-blur-md">
                        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Completed</h2>
                        <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2.5 py-0.5 rounded-full font-bold border border-emerald-500/30">
                            {completedTasks.length}
                        </span>
                    </div>
                    <div className="p-4 overflow-y-auto scroll-area flex-1 space-y-3">
                        {completedTasks.length === 0 ? (
                            <div className="text-center p-12 text-slate-500">
                                <p>No completed tasks yet.</p>
                            </div>
                        ) : (
                            completedTasks.slice(0).reverse().map((task) => (
                                <div key={task.id} className="p-4 rounded-xl border border-white/5 bg-white/[0.02] opacity-80 hover:opacity-100 transition-opacity">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                                            {task.skill}
                                        </span>
                                        <CheckCircle size={16} className="text-emerald-500/80" />
                                    </div>
                                    <h3 className="text-slate-400 text-sm">{task.task}</h3>
                                </div>
                            ))
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default TaskBoard;
