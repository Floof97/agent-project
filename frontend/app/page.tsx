'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ShieldCheck, Plus, FileText, Settings, Search, Trash2, Upload, X, AlertTriangle } from 'lucide-react';

export default function LighterGreenAgent() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Welcome back. How can I assist you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [activeFiles, setActiveFiles] = useState<string[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [fileToDelete, setFileToDelete] = useState<string | null>(null);

    // 1. Fetch files on load
    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        const res = await fetch('http://127.0.0.1:8000/files');
        const data = await res.json();
        setActiveFiles(data.files || []);
    };

    // 2. Handle Upload
    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;
        const file = e.target.files[0];
        setIsUploading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            await fetch('http://127.0.0.1:8000/upload', { method: 'POST', body: formData });
            fetchFiles(); // Refresh list
        } catch (error) {
            console.error("Upload failed", error);
        } finally {
            setIsUploading(false);
            e.target.value = ''; // This clears the input so you can upload the same file again immediately, and not get frozen
        }
    };

    // 3. Handle Delete
    const openDeleteModal = (filename: string) => {
        setFileToDelete(filename);
    };

    const confirmDelete = async () => {
        if (!fileToDelete) return;
        await fetch(`http://127.0.0.1:8000/files/${fileToDelete}`, { method: 'DELETE' });
        setFileToDelete(null);
        fetchFiles();
    };

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
                {/* Header Section */}
                <div className="flex items-center gap-3 mb-10 px-2">
                    <div className="bg-[#4c6e77] p-2 rounded-xl text-white shadow-lg">
                        <ShieldCheck size={26} />
                    </div>
                    <h1 className="font-bold text-[23px]">Raguard.ai</h1>
                </div>

                {/* Upload Button */}
                <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf" />
                <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 transition-all p-3 rounded-xl mb-8 text-sm font-semibold border border-emerald-200"
                >
                    {isUploading ? "Processing..." : <><Plus size={18} /> Add Document</>}
                </button>

                {/* File List */}
                <div className="flex-1 overflow-y-auto">
                    <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4 px-2">Active Documents</p>

                    {activeFiles.length === 0 ? (
                        // SHOW THIS IF EMPTY
                        <div className="px-2 py-8 text-center border-2 border-dashed border-slate-50 rounded-2xl">
                            <p className="text-xs text-slate-400 italic font-medium">You have not uploaded anything yet! Add a PDF file to begin.</p>
                        </div>
                    ) : (
                        // SHOW THIS IF FILES EXIST
                        <div className="space-y-1">
                            {activeFiles.map((doc, i) => (
                                <div key={i} className="flex items-center justify-between p-3 hover:bg-emerald-50/50 rounded-xl group cursor-pointer transition-all">
                                    <div className="flex items-center gap-3 truncate flex-1" onClick={() => setSelectedFile(doc)}>
                                        <FileText size={18} className="text-emerald-400" />
                                        <span className="text-sm text-slate-600 truncate group-hover:text-slate-900">{doc}</span>
                                    </div>
                                    <button onClick={(e) => { e.stopPropagation(); openDeleteModal(doc); }}
                                        className="text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 p-1 transition-opacity">
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
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
                                placeholder="Type your question about anything..."
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

            {/* --- MODAL: PDF VIEWER --- */}
            {selectedFile && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-10">
                    <div className="bg-white w-full h-full max-w-6xl rounded-3xl overflow-hidden flex flex-col shadow-2xl">
                        <div className="p-4 border-b flex justify-between items-center bg-slate-50">
                            <h3 className="font-bold text-slate-700 flex items-center gap-2"><FileText size={20} /> {selectedFile}</h3>
                            <button onClick={() => setSelectedFile(null)} className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500"><X size={24} /></button>
                        </div>
                        <iframe src={`http://127.0.0.1:8000/view/${selectedFile}`} className="w-full h-full" title="PDF Viewer" />
                    </div>
                </div>
            )}

            {/* --- MODAL: DELETE CONFIRMATION --- */}
            {fileToDelete && (
                <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-[2px] z-[60] flex items-center justify-center p-4">
                    <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-red-50 text-center">
                        <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <AlertTriangle size={32} />
                        </div>
                        <h3 className="text-xl font-bold text-slate-800 mb-2">Delete Document?</h3>
                        <p className="text-sm text-slate-500 mb-6">Are you sure you want to remove <span className="font-bold text-slate-700">"{fileToDelete}"</span>? This will wipe its data from the AI's memory.</p>
                        <div className="flex gap-3">
                            <button onClick={() => setFileToDelete(null)} className="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold rounded-xl transition-colors">Cancel</button>
                            <button onClick={confirmDelete} className="flex-1 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-xl transition-colors shadow-lg">Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}