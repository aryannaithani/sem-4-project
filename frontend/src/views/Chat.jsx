import React, { useState, useEffect, useRef } from 'react';
import { sendMentorMessage, getMentorHistory, clearMentorHistory } from '../api';
import { Send, Bot, User, Trash2, Zap } from 'lucide-react';
import { clsx } from 'clsx';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const bottomRef = useRef(null);

    useEffect(() => {
        // Load initial history
        getMentorHistory().then(data => {
            if (data.history && data.history.length > 0) {
                setMessages(data.history);
            } else {
                setMessages([
                    { role: 'model', content: "Hi! I'm your AI Career Mentor. I have full context of your skills, your goal, and what's trending right now. What would you like to discuss? I can recommend a side project, explain a new concept, or give you interview tips." }
                ]);
            }
        });
    }, []);

    useEffect(() => {
        // Scroll to bottom when messages change
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, loading]);

    const handleSend = async (text = input) => {
        if (!text.trim()) return;

        const userMsg = { role: 'user', content: text };
        const newHistory = [...messages, userMsg];
        setMessages(newHistory);
        setInput("");
        setSuggestions([]);
        setLoading(true);

        try {
            const data = await sendMentorMessage(text, newHistory);
            setMessages(data.history || [...newHistory, { role: 'model', content: data.response }]);
            if (data.suggestions) {
                setSuggestions(data.suggestions.slice(0, 3));
            }
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'model', content: "**Error**: Failed to connect to mentor." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = async () => {
        await clearMentorHistory();
        setMessages([{ role: 'model', content: "Conversation cleared. How can I help you today?" }]);
        setSuggestions([]);
    };

    return (
        <div className="w-full h-full max-h-screen flex flex-col pt-8 px-8 pb-4 animate-fade-in max-w-6xl mx-auto">
            <header className="flex justify-between items-end mb-6 shrink-0">
                <div>
                    <h1 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
                        <Bot className="text-violet-500" size={32} />
                        Conversational Mentor
                    </h1>
                    <p className="text-slate-400">Ask your digital-twin-powered mentor anything.</p>
                </div>
                <button
                    onClick={handleClear}
                    className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-red-400 transition-colors uppercase tracking-wider"
                >
                    <Trash2 size={16} /> Clear History
                </button>
            </header>

            <div className="flex-1 card overflow-hidden flex flex-col shadow-lg border-white/5 relative">
                <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-area">
                    {messages.map((m, idx) => {
                        const isUser = m.role === 'user';
                        return (
                            <div key={idx} className={clsx("flex w-full", isUser ? "justify-end" : "justify-start")}>
                                <div className={clsx("flex gap-4 max-w-[80%]", isUser ? "flex-row-reverse" : "flex-row")}>
                                    <div className="shrink-0 mt-1">
                                        {isUser ? (
                                            <div className="w-8 h-8 rounded-full bg-violet-600 flex justify-center items-center">
                                                <User size={16} className="text-white" />
                                            </div>
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-[#1e293b] border border-white/10 flex justify-center items-center shadow-glow">
                                                <Bot size={16} className="text-violet-400" />
                                            </div>
                                        )}
                                    </div>
                                    <div className={clsx(
                                        "px-5 py-4 whitespace-pre-wrap leading-relaxed shadow-md",
                                        isUser ? "bg-violet-600/90 text-white rounded-2xl rounded-tr-sm" : "bg-[#182030] text-slate-200 border border-white/5 rounded-2xl rounded-tl-sm"
                                    )}>
                                        {m.content}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {loading && (
                        <div className="flex w-full justify-start">
                            <div className="flex gap-4 max-w-3xl">
                                <div className="shrink-0 mt-1">
                                    <div className="w-8 h-8 rounded-full bg-[#1e293b] border border-white/10 flex justify-center items-center shadow-glow">
                                        <Bot size={16} className="text-violet-400" />
                                    </div>
                                </div>
                                <div className="px-5 py-5 bg-[#182030] text-slate-200 border border-white/5 rounded-2xl rounded-tl-sm flex items-center gap-1.5 h-12">
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {suggestions.length > 0 && !loading && (
                    <div className="px-6 pb-2 pt-2 flex flex-wrap gap-2 animate-fade-up shrink-0">
                        <div className="flex items-center gap-2 w-full mb-1">
                            <Zap size={14} className="text-orange-400" />
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Suggestions</span>
                        </div>
                        {suggestions.map((sug, i) => (
                            <button
                                key={i}
                                onClick={() => handleSend(sug)}
                                className="px-4 py-2 bg-white/5 hover:bg-white/10 text-sm text-slate-300 rounded-full border border-white/10 transition-colors whitespace-nowrap overflow-hidden text-ellipsis max-w-full"
                            >
                                {sug}
                            </button>
                        ))}
                    </div>
                )}

                <div className="p-4 border-t border-white/5 bg-black/20 shrink-0">
                    <form
                        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                        className="flex gap-4 relative"
                    >
                        <input
                            type="text"
                            value={input}
                            autoFocus
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Message your mentor..."
                            className="input bg-[#111827] border-white/10 focus:border-violet-500/50 py-3 pl-4 pr-14 flex-1 shadow-inner text-base"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading}
                            className={clsx(
                                "absolute right-2 top-2 bottom-2 w-10 flex items-center justify-center rounded-lg transition-all",
                                input.trim() && !loading ? "bg-violet-600 text-white shadow-glow hover:bg-violet-500" : "bg-white/5 text-slate-500 cursor-not-allowed"
                            )}
                        >
                            <Send size={18} className={input.trim() ? "ml-1" : ""} />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Chat;
