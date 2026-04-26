'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ShieldCheck, Plus, FileText, Settings, Search } from 'lucide-react';

export default function LighterGreenAgent() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Welcome back. How can I assist you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    thread_id: "user_123" // You can hardcode this for now
                }),
            });

            const data = await response.json();

            if (data.response) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.response
                }]);
            }
        } catch (error) {
            console.error("Error calling AI:", error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Error: Could not connect to the local AI. Make sure the backend is running!"
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="flex h-screen bg-[#F7FBF9] font-sans text-slate-800">

            {/* SIDEBAR: Lighter Sage Theme */}
            <aside className="w-72 bg-white border-r border-emerald-100 flex flex-col p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-10 px-2">
                    <div className="bg-[#006e35] p-2 rounded-xl text-white shadow-lg shadow-emerald-200">
                        <ShieldCheck size={24} />
                    </div>
                    <h1 className="font-bold text-lg tracking-tight text-slate-800 text-[23px]">Raguard.ai <span className="text-slate-800 text-[10px] align-top">TM</span></h1>
                </div>

                <button className="flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 transition-all p-3 rounded-xl mb-8 text-sm font-semibold border border-emerald-200">
                    <Plus size={18} /> New Analysis
                </button>

                <div className="flex-1 overflow-y-auto">
                    <div className="flex items-center justify-between px-2 mb-4">
                        <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Active Documents</p>
                        <Search size={14} className="text-slate-300 cursor-pointer" />
                    </div>

                    <div className="space-y-2">
                        {['Safety_Regs_v2.pdf', 'Compliance_2026.pdf', 'Site_Specs.pdf'].map((doc, i) => (
                            <div key={i} className="flex items-center gap-3 p-3 hover:bg-emerald-50/50 rounded-xl cursor-pointer text-sm group transition-all">
                                <FileText size={18} className="text-emerald-300 group-hover:text-emerald-500" />
                                <span className="text-slate-600 group-hover:text-slate-900 truncate">{doc}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="pt-6 border-t border-slate-100 mt-auto flex flex-col gap-4">
                    <div className="flex items-center gap-3 px-2 text-xs font-medium text-emerald-600 bg-emerald-50/50 p-2 rounded-lg">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                        Local Gemma 4 • Ready
                    </div>
                    <button className="flex items-center gap-3 px-2 text-slate-400 hover:text-slate-600 text-sm transition-colors">
                        <Settings size={18} /> Settings
                    </button>
                </div>
            </aside>

            {/* MAIN CHAT: Clean & Airy */}
            <main className="flex-1 flex flex-col relative">

                {/* Header */}
                <header className="h-20 flex items-center px-10 bg-white/50 backdrop-blur-sm justify-between">
                    <div className="flex items-center gap-4">
                        <div className="bg-emerald-100 p-2 rounded-full">
                            <Bot size={20} className="text-emerald-600" />
                        </div>
                        <div>
                            <h2 className="font-bold text-slate-800">FAQ Assistant</h2>
                            <p className="text-[11px] text-emerald-500 font-medium">RAG Engine Mode Active</p>
                        </div>
                    </div>
                </header>

                {/* Messages Container */}
                <div ref={scrollRef} className="flex-1 overflow-y-auto p-10 space-y-8 pb-36">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[75%] gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>

                                {/* ICON LOGIC START */}
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm border ${msg.role === 'user'
                                        ? 'bg-emerald-50 border-emerald-200 text-emerald-600'
                                        : 'bg-white border-slate-100 text-slate-400'
                                    }`}>
                                    {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                                </div>
                                {/* ICON LOGIC END */}

                                <div className={`p-4 rounded-3xl text-[14px] leading-relaxed shadow-sm ${msg.role === 'user'
                                        ? 'bg-emerald-500 text-white rounded-tr-none'
                                        : 'bg-white text-slate-700 border border-emerald-50 rounded-tl-none'
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        </div>
                    ))}

                    
                    {isTyping && (
                        <div className="flex justify-start items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-white border border-slate-100 flex items-center justify-center shadow-sm">
                                <Bot size={20} className="text-slate-400" />
                            </div>
                            <div className="bg-white border border-emerald-50 p-4 rounded-3xl rounded-tl-none shadow-sm flex gap-1">
                                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce"></span>
                                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Floating Input Bar */}
                <div className="absolute bottom-8 left-0 w-full px-10">
                    <div className="max-w-4xl mx-auto">
                        <form onSubmit={handleSendMessage} className="relative flex items-center">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Type your question about business laws..."
                                className="w-full p-5 pr-16 rounded-2xl border border-emerald-100 focus:outline-none focus:ring-4 focus:ring-emerald-500/5 focus:border-emerald-300 transition-all shadow-xl shadow-emerald-500/5 bg-white text-slate-800 placeholder:text-slate-300"
                            />
                            <button
                                type="submit"
                                className="absolute right-3 p-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl transition-all shadow-lg shadow-emerald-200 active:scale-90"
                            >
                                <Send size={20} />
                            </button>
                        </form>
                    </div>
                </div>
            </main>
        </div>
    );
}