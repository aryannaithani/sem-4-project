import { useState, useEffect, useRef } from 'react';
import { sendMentorMessage, getMentorHistory, clearMentorHistory } from '../api';
import { Send, Bot, User, Trash2 } from 'lucide-react';
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
        <div>
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-4 gap-4">
                <div>
                    <h1 className="title-xl flex items-center gap-3">
                        <Bot size={28} />
                        Conversational Mentor
                    </h1>
                    <p className="muted mt-2">Focused career guidance for advanced learners.</p>
                </div>
                <button
                    onClick={handleClear}
                    className="btn text-xs"
                >
                    <Trash2 size={16} /> Clear History
                </button>
            </header>

            <div className="panel overflow-hidden flex flex-col min-h-[70vh]">
                <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                    {messages.map((m, idx) => {
                        const isUser = m.role === 'user';
                        return (
                            <div key={idx} className={clsx("flex w-full", isUser ? "justify-end" : "justify-start")}>
                                <div className={clsx("flex gap-4 max-w-[80%]", isUser ? "flex-row-reverse" : "flex-row")}>
                                    <div className="shrink-0 mt-1">
                                        {isUser ? (
                                            <div className="w-8 h-8 rounded-full bg-white flex justify-center items-center">
                                                <User size={16} className="text-black" />
                                            </div>
                                        ) : (
                                            <div className="w-8 h-8 rounded-full bg-[#19191d] border border-[#2a2a30] flex justify-center items-center">
                                                <Bot size={16} className="text-white" />
                                            </div>
                                        )}
                                    </div>
                                    <div className={clsx(
                                        "px-5 py-4 whitespace-pre-wrap leading-relaxed",
                                        isUser ? "bg-white text-black rounded-2xl rounded-tr-sm" : "bg-[#111116] border border-[#28282e] rounded-2xl rounded-tl-sm"
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
                                    <div className="w-8 h-8 rounded-full bg-[#19191d] border border-[#2a2a30] flex justify-center items-center">
                                        <Bot size={16} className="text-white" />
                                    </div>
                                </div>
                                <div className="px-5 py-5 bg-[#111116] border border-[#28282e] rounded-2xl rounded-tl-sm flex items-center gap-1.5 h-12">
                                    <div className="w-2 h-2 rounded-full bg-white/60 animate-pulse"></div>
                                    <div className="w-2 h-2 rounded-full bg-white/60 animate-pulse"></div>
                                    <div className="w-2 h-2 rounded-full bg-white/60 animate-pulse"></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {suggestions.length > 0 && !loading && (
                    <div className="px-6 pb-2 pt-2 flex flex-wrap gap-2">
                        <span className="text-xs font-bold uppercase tracking-wider muted w-full">Suggestions</span>
                        {suggestions.map((sug, i) => (
                            <button
                                key={i}
                                onClick={() => handleSend(sug)}
                                className="chip"
                            >
                                {sug}
                            </button>
                        ))}
                    </div>
                )}

                <div className="p-4 sm:p-5 border-t border-[#232328] bg-[#0d0d10]">
                    <form
                        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                        className="flex gap-4 relative w-full items-center"
                    >
                        <div className="relative flex-1">
                            <input
                                type="text"
                                value={input}
                                autoFocus
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Message your mentor..."
                                className="w-full bg-[#17171b] border border-[#2a2a31] rounded-xl py-4 pl-5 pr-14 text-[15px] text-white transition-all outline-none"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || loading}
                                className={clsx(
                                    "absolute right-2 top-2 bottom-2 w-10 sm:w-12 flex items-center justify-center rounded-lg transition-all",
                                    input.trim() && !loading ? "bg-white text-black hover:bg-[#f1f1f1]" : "bg-[#232328] text-[#666] opacity-50 cursor-not-allowed"
                                )}
                            >
                                <Send size={18} className={input.trim() ? "ml-0.5" : ""} />
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Chat;
