'use client'
import { useState, useEffect } from 'react'

export default function Header() {
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('theme')
    if (stored === 'dark') {
      setDark(true)
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleDark = () => {
    const next = !dark
    setDark(next)
    if (next) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return (
    <header className="shadow-lg border-b border-[#2A2A4A]" style={{ backgroundColor: 'var(--bg-header)' }}>
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-groww-green rounded-xl flex items-center justify-center text-white shadow-green">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div>
            <h1 className="text-white font-semibold text-lg leading-tight">
              HDFC MF AI Assistant
            </h1>
            <p className="text-gray-400 text-xs">
              Powered by Groww · Facts only
            </p>
          </div>
        </div>

        <div className="hidden lg:flex items-center gap-2 border border-groww-green/30 bg-groww-green/10 px-3 py-1.5 rounded-full">
          <span className="text-xs text-groww-green font-medium">
            🛡 Verified data from AMFI, SEBI
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleDark}
            className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center text-gray-300 hover:text-white transition-all duration-200"
            aria-label="Toggle dark mode"
          >
            {dark ? '☀' : '🌙'}
          </button>
          <div className="hidden md:flex items-center gap-2 bg-groww-navy px-3 py-1.5 rounded-full">
            <div className="w-2 h-2 bg-groww-green rounded-full animate-pulse"/>
            <span className="text-gray-300 text-xs font-medium">Live</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="w-9 h-9 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center transition-colors duration-200"
              aria-label="Notifications"
            >
              <span className="text-sm">🔔</span>
            </button>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center ring-2 ring-white/20">
              <span className="text-white font-semibold text-sm">HM</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
