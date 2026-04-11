import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

const Chat = () => {
    const [messages, setMessages] = useState([
        { id: 1, sender: 'bot', text: 'Hello! I am your AI Career Mentor. I can help you plan your career, review your resume, or suggest new technologies to learn. What would you like to focus on today?' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { id: Date.now(), sender: 'user', text: input.trim() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        // Mock response
        setTimeout(() => {
            setIsTyping(false);
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                sender: 'bot',
                text: `That's an interesting question about "${userMessage.text}". Let's add examining this topic to your task board for your next planning session!`
            }]);
        }, 1500);
    };

    return (
        <div className="p-8 max-w-4xl mx-auto w-full h-full flex flex-col animate-fade-in pb-10">
            <header className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 flex items-center">
                        <Sparkles size={24} className="text-blue-500 mr-2" /> Mentor Chat
                    </h1>
                    <p className="text-gray-400">Ask questions and get advice tailored to your career roadmap.</p>
                </div>
            </header>

            <div className="flex-1 bg-[#121418] rounded-2xl border border-[#2a2e37] flex flex-col overflow-hidden relative shadow-lg">

                {/* Messages Display */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg) => (
                        <div key={msg.id} className={clsx("flex font-sans", msg.sender === 'user' ? "justify-end" : "justify-start")}>
                            <div className={clsx(
                                "max-w-[75%] rounded-2xl px-5 py-3.5 shadow-sm text-sm leading-relaxed",
                                msg.sender === 'user'
                                    ? "bg-blue-600 text-white rounded-br-none"
                                    : "bg-[#1f2229] border border-[#2a2e37] text-gray-200 rounded-bl-none"
                            )}>
                                <div className="flex items-center space-x-2 mb-1.5 opacity-50">
                                    {msg.sender === 'user' ? <User size={12} /> : <Bot size={12} />}
                                    <span className="text-[10px] uppercase font-bold tracking-wider">
                                        {msg.sender === 'user' ? 'You' : 'AI Mentor'}
                                    </span>
                                </div>
                                {msg.text}
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex justify-start">
                            <div className="bg-[#1f2229] border border-[#2a2e37] text-gray-200 rounded-2xl rounded-bl-none px-5 py-4 w-auto flex space-x-1.5 items-center">
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-[#181a20] border-t border-[#2a2e37]">
                    <form onSubmit={handleSend} className="relative flex items-center">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask for career advice..."
                            className="w-full bg-[#0f1115] border border-[#2a2e37] text-gray-200 text-sm rounded-xl py-3.5 pl-4 pr-12 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder-gray-600 shadow-inner"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim()}
                            className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 text-white rounded-lg transition-colors shadow-md"
                        >
                            <Send size={16} className="-ml-0.5 mt-0.5" />
                        </button>
                    </form>
                    <div className="text-center mt-2">
                        <span className="text-[10px] text-gray-600 font-medium">AI generated responses. Verify before making life-changing decisions.</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Chat;
