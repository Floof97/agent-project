'use client'
import { useState } from 'react'
import { supabase } from '@/utils/supabaseClient'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const handleSignIn = async () => {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) alert(error.message)
        else window.location.href = '/'
    }

    const handleSignUp = async () => {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) alert(error.message)
        else alert('Check your email for the confirmation link!')
    }

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-emerald-50">
            <div className="bg-white p-8 rounded-2xl shadow-2xl w-96 border border-emerald-100">
                <h2 className="text-2xl font-bold mb-6 text-slate-800 text-center">Welcome to Raguard.ai</h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Email Address</label>
                        <input
                            type="email"
                            placeholder="name@example.com"
                            className="w-full p-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 transition-all"
                            onChange={e => setEmail(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            className="w-full p-3 bg-slate-50 border-2 border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 transition-all"
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>
                </div>

                <button
                    onClick={handleSignIn}
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white p-3 rounded-xl mt-6 mb-3 font-bold shadow-lg shadow-emerald-200 transition-colors"
                >
                    Sign In
                </button>

                <button
                    onClick={handleSignUp}
                    className="w-full text-emerald-700 hover:text-emerald-800 p-3 text-sm font-semibold transition-colors"
                >
                    Create Account
                </button>
            </div>
        </div>
    )
}