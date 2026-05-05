'use client'
import { useState } from 'react'
import { supabase } from '@/utils/supabaseClient'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const handleSignIn = async () => {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) alert(error.message)
        else window.location.href = '/' // Go to the chat page
    }

    const handleSignUp = async () => {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) alert(error.message)
        else alert('Check your email for the confirmation link!')
    }

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-emerald-50">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-96">
                <h2 className="text-2xl font-bold mb-6 text-slate-800">Welcome to Raguard</h2>
                <input type="email" placeholder="Email" className="w-full p-3 mb-4 border rounded-xl" onChange={e => setEmail(e.target.value)} />
                <input type="password" placeholder="Password" className="w-full p-3 mb-6 border rounded-xl" onChange={e => setPassword(e.target.value)} />
                <button onClick={handleSignIn} className="w-full bg-emerald-500 text-white p-3 rounded-xl mb-3 font-bold">Sign In</button>
                <button onClick={handleSignUp} className="w-full text-emerald-600 p-3 text-sm">Create Account</button>
            </div>
        </div>
    )
}