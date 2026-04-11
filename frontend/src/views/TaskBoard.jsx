import React, { useState, useEffect } from 'react';
import { getTasks, completeTask, generateTasks } from '../api';
import { CheckCircle, Circle, RefreshCw, Zap, Bookmark } from 'lucide-react';
import { clsx } from 'clsx';

const TaskBoard = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            setLoading(true);
            const data = await getTasks();
            setTasks(data || []);
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
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    const pendingTasks = tasks.filter(t => t.status === 'pending');
    const completedTasks = tasks.filter(t => t.status === 'completed');

    return (
        <div className="p-8 max-w-6xl mx-auto w-full animate-fade-in flex flex-col h-full">
            <header className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Task Board</h1>
                    <p className="text-gray-400">Complete tasks to gain skills and progress your career roadmap.</p>
                </div>
                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-medium rounded-xl transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:shadow-[0_0_20px_rgba(59,130,246,0.5)]"
                >
                    {generating ? <RefreshCw className="animate-spin" size={18} /> : <Zap size={18} />}
                    <span>{generating ? 'Generating...' : 'Generate AI Tasks'}</span>
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1 pb-10">

                {/* Pending Tasks Column */}
                <div className="flex flex-col bg-[#121418] rounded-2xl border border-[#2a2e37] overflow-hidden">
                    <div className="p-4 border-b border-[#2a2e37] bg-[#181a20] flex justify-between items-center">
                        <h2 className="text-lg font-bold text-gray-200">Pending Tasks</h2>
                        <span className="bg-blue-500 bg-opacity-20 text-blue-400 text-xs px-3 py-1 rounded-full font-bold">
                            {pendingTasks.length}
                        </span>
                    </div>
                    <div className="p-4 overflow-y-auto flex-1 space-y-4">
                        {pendingTasks.length === 0 ? (
                            <div className="text-center p-10 text-gray-500">
                                <Bookmark size={40} className="mx-auto mb-4 opacity-20" />
                                <p>No pending tasks.</p>
                                <button onClick={handleGenerate} className="mt-4 text-blue-500 hover:text-blue-400 text-sm">Generate some!</button>
                            </div>
                        ) : (
                            pendingTasks.map((task) => (
                                <div key={task.id} className="bg-[#181a20] p-5 rounded-xl border border-[#2a2e37] transition-all hover:border-blue-500/50 group shadow-md hover:shadow-lg">
                                    <div className="flex justify-between items-start mb-3">
                                        <span className="inline-block bg-blue-500/10 text-blue-400 text-xs px-2 py-1 rounded-md font-medium">
                                            Skill: {task.skill}
                                        </span>
                                        <span className={clsx(
                                            "text-xs px-2 py-1 rounded-md font-medium bg-opacity-10",
                                            task.difficulty === 'advanced' ? "bg-red-500 text-red-400" :
                                                task.difficulty === 'intermediate' ? "bg-orange-500 text-orange-400" :
                                                    "bg-emerald-500 text-emerald-400"
                                        )}>
                                            {task.difficulty || 'beginner'}
                                        </span>
                                    </div>
                                    <h3 className="text-gray-100 font-medium mb-4 leading-relaxed">{task.task}</h3>
                                    <button
                                        onClick={() => handleCompleteTask(task.id)}
                                        className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg border border-[#2a2e37] text-gray-400 hover:text-emerald-400 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-colors"
                                    >
                                        <Circle size={18} className="group-hover:hidden" />
                                        <CheckCircle size={18} className="hidden group-hover:block" />
                                        <span>Mark as Complete</span>
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Completed Tasks Column */}
                <div className="flex flex-col bg-[#121418] rounded-2xl border border-[#2a2e37] overflow-hidden">
                    <div className="p-4 border-b border-[#2a2e37] bg-[#181a20] flex justify-between items-center">
                        <h2 className="text-lg font-bold text-gray-200">Completed</h2>
                        <span className="bg-emerald-500 bg-opacity-20 text-emerald-400 text-xs px-3 py-1 rounded-full font-bold">
                            {completedTasks.length}
                        </span>
                    </div>
                    <div className="p-4 overflow-y-auto flex-1 space-y-4">
                        {completedTasks.length === 0 ? (
                            <div className="text-center p-10 text-gray-500">
                                <p>No completed tasks yet.</p>
                            </div>
                        ) : (
                            completedTasks.slice(0).reverse().map((task) => (
                                <div key={task.id} className="bg-[#0f1115] p-5 rounded-xl border border-[#1f2229] opacity-70">
                                    <div className="flex justify-between items-center mb-3">
                                        <span className="inline-block bg-gray-500/10 text-gray-400 text-xs px-2 py-1 rounded-md">
                                            {task.skill}
                                        </span>
                                        <CheckCircle size={16} className="text-emerald-500" />
                                    </div>
                                    <h3 className="text-gray-500 line-through text-sm">{task.task}</h3>
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
