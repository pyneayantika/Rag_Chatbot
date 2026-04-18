'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import Header from './components/Header'
import Disclaimer from './components/Disclaimer'
import ChatMessage from './components/ChatMessage'
import TypingIndicator from './components/TypingIndicator'
import ChatInput from './components/ChatInput'
import StatusBanner from './components/StatusBanner'
import Footer from './components/Footer'
import BackgroundChart from './components/BackgroundChart'
import { sendMessage, checkHealth } from './api/chat'
import { Message } from './types'

const SIDEBAR_QUESTIONS = [
  { text: 'What is the expense ratio of HDFC Mid Cap?', icon: '$', color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400' },
  { text: 'What is exit load of HDFC Small Cap?', icon: '%', color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/40 dark:text-purple-400' },
  { text: 'What is ELSS lock-in period?', icon: '↗', color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/40 dark:text-purple-400' },
  { text: 'What is minimum SIP for HDFC Flexi Cap?', icon: '◕', color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/40 dark:text-orange-400' },
  { text: 'What is benchmark of HDFC Large Cap?', icon: '▦', color: 'bg-violet-100 text-violet-600 dark:bg-violet-900/40 dark:text-violet-400' },
  { text: 'How to download capital gains statement?', icon: 'i', color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400' },
]

const FUND_CARDS = [
  { name: 'HDFC Mid Cap', icon: '📈', tag: 'Mid Cap · Very High Risk', accent: '#00D09C' },
  { name: 'HDFC Flexi Cap', icon: '🔄', tag: 'Flexi Cap · Very High Risk', accent: '#6366F1' },
  { name: 'HDFC ELSS Tax Saver', icon: '🔒', tag: 'ELSS · 3yr Lock-in', accent: '#F59E0B' },
  { name: 'HDFC Large Cap', icon: '🏢', tag: 'Large Cap · Very High Risk', accent: '#3B82F6' },
  { name: 'HDFC Small Cap', icon: '💎', tag: 'Small Cap · Very High Risk', accent: '#EC4899' },
]

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => uuidv4())
  const [isOnline, setIsOnline] = useState(true)
  const [isChecking, setIsChecking] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const checkDark = () => setIsDark(
      document.documentElement.classList.contains('dark')
    )
    checkDark()
    const observer = new MutationObserver(checkDark)
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const check = async () => {
      const online = await checkHealth()
      setIsOnline(online)
      setIsChecking(false)
    }
    check()
    const interval = setInterval(check, 60000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const addMessage = useCallback((msg: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages(prev => [...prev, {
      ...msg,
      id: uuidv4(),
      timestamp: new Date()
    }])
  }, [])

  const handleSend = useCallback(async (query: string) => {
    if (!query.trim() || isLoading) return
    addMessage({ role: 'user', content: query })
    setIsLoading(true)
    try {
      const response = await sendMessage(query, sessionId)
      addMessage({
        role: 'assistant',
        content: response.answer,
        source_url: response.source_url,
        last_updated: response.last_updated,
        is_refusal: response.is_refusal,
        is_pii: response.is_pii,
      })
    } catch (error: any) {
      addMessage({
        role: 'assistant',
        content: error.message || 'Something went wrong. Please try again.',
        is_refusal: true,
      })
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, sessionId, addMessage])

  const handleClearChat = useCallback(() => {
    setMessages([])
  }, [])

  return (
    <>
      <BackgroundChart />
      <div className="relative z-10 min-h-screen flex flex-col" style={{ backgroundColor: 'transparent' }}>

      <Header />

      {/* Stats Bar */}
      <div className="py-2 px-4" style={{ backgroundColor: 'var(--bg-stats)', borderBottom: '1px solid var(--border-color)' }}>
        <p className="text-center text-xs flex flex-wrap justify-center items-center gap-x-2 gap-y-1" style={{ color: 'var(--text-muted)' }}>
          <span>📊 5 Schemes Covered</span>
          <span className="hidden sm:inline">·</span>
          <span>📁 20 Verified Sources</span>
          <span className="hidden sm:inline">·</span>
          <span>🔄 Updated Daily at 9:15 AM IST</span>
          <span className="hidden sm:inline">·</span>
          <span>🛡 SEBI & AMFI Compliant</span>
        </p>
      </div>

      {/* Mobile quick questions — horizontal scroll chips (visible < md) */}
      <div className="md:hidden px-4 py-3 overflow-x-auto hide-scrollbar">
        <div className="flex gap-2 w-max">
          {SIDEBAR_QUESTIONS.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q.text)}
              disabled={isLoading}
              className="flex items-center gap-2 px-3 py-2 rounded-full text-xs whitespace-nowrap hover:border-groww-green disabled:opacity-50 shadow-sm"
              style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }}
            >
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${q.color}`}>{q.icon}</span>
              <span className="truncate max-w-[180px]">{q.text}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main two-column layout */}
      <div className="flex-1 flex max-w-7xl mx-auto w-full">
        {/* LEFT SIDEBAR (hidden on mobile) */}
        <aside className="hidden md:flex flex-col w-[280px] flex-shrink-0 p-4 gap-3" style={{ background: isDark ? 'rgba(15,23,42,0.85)' : 'rgba(255,255,255,0.7)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)', borderRight: isDark ? '1px solid rgba(139,92,246,0.2)' : '1px solid rgba(139,92,246,0.1)' }}>
          <h2 className="px-1" style={{ color: isDark ? '#C4B5FD' : '#7C3AED', fontWeight: '600', fontSize: '13px', letterSpacing: '0.05em', textTransform: 'uppercase' as const, marginBottom: '12px' }}>Quick Questions</h2>
          <div className="flex flex-col gap-2 overflow-y-auto flex-1">
            {SIDEBAR_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q.text)}
                disabled={isLoading}
                className="flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed text-left group hover:translate-x-1"
                style={{ background: isDark ? 'linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(30,41,59,0.9) 100%)' : 'linear-gradient(135deg, rgba(139,92,246,0.06) 0%, rgba(255,255,255,0.95) 100%)', border: isDark ? '1px solid rgba(139,92,246,0.3)' : '1px solid rgba(139,92,246,0.15)', borderRadius: '12px', padding: '12px 14px', cursor: 'pointer', backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)', boxShadow: isDark ? '0 4px 16px rgba(139,92,246,0.15)' : '0 2px 8px rgba(139,92,246,0.08)', transition: 'all 0.2s ease' }}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0 ${q.color}`} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
                  {q.icon}
                </div>
                <p className="group-hover:text-[#8B5CF6]" style={{ color: isDark ? '#E2D9F3' : '#2D2D2D', fontSize: '13px', fontWeight: '500', lineHeight: '1.4' }}>
                  {q.text}
                </p>
              </button>
            ))}
          </div>
        </aside>

        {/* RIGHT MAIN AREA */}
        <main className="flex-1 flex flex-col p-4 gap-4 min-w-0">
          <StatusBanner isOnline={isOnline} isChecking={isChecking} />
          <Disclaimer />

          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>HDFC Mutual Fund FAQ</h2>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Ask factual questions about 5 HDFC schemes</p>
            </div>
            {messages.length > 0 && (
              <button
                onClick={handleClearChat}
                className="text-xs hover:text-groww-red px-3 py-1.5 rounded-lg hover:bg-red-50 border border-transparent hover:border-red-200"
                style={{ color: 'var(--text-muted)' }}
              >
                Clear chat
              </button>
            )}
          </div>

          {/* Fund scheme cards (only when no messages) */}
          {messages.length === 0 && (
            <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-1">
              {FUND_CARDS.map((fund, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(`Tell me about ${fund.name}`)}
                  disabled={isLoading}
                  className="flex-shrink-0 overflow-hidden hover:-translate-y-1 disabled:opacity-50 cursor-pointer text-left"
                  style={{ background: isDark ? 'linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(30,41,59,0.9) 100%)' : 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(245,243,255,0.8) 100%)', border: isDark ? '1px solid rgba(139,92,246,0.25)' : '1px solid rgba(139,92,246,0.12)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', borderRadius: '16px', padding: '16px', boxShadow: isDark ? '0 4px 20px rgba(139,92,246,0.15)' : '0 4px 16px rgba(139,92,246,0.08)', transition: 'all 0.25s ease', minWidth: '160px', borderTopColor: fund.accent, borderTopWidth: '4px' }}
                >
                  <div className="space-y-1.5">
                    <span className="text-2xl">{fund.icon}</span>
                    <p className="leading-tight" style={{ color: isDark ? '#F1F5F9' : '#1E293B', fontWeight: '600', fontSize: '14px' }}>{fund.name}</p>
                    <p style={{ color: isDark ? '#94A3B8' : '#767676', fontSize: '11px' }}>{fund.tag}</p>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Chat container */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-hidden flex flex-col"
            style={{ background: isDark ? 'rgba(15,23,42,0.75)' : 'rgba(255,255,255,0.65)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)', border: isDark ? '1px solid rgba(139,92,246,0.15)' : '1px solid rgba(255,255,255,0.6)', borderRadius: '20px', boxShadow: isDark ? '0 4px 24px rgba(0,0,0,0.2)' : '0 4px 24px rgba(0,0,0,0.06)', minHeight: '55vh', maxHeight: '62vh' }}
          >
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Empty state */}
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center gap-5 py-12">
                  <div className="w-16 h-16 bg-groww-light rounded-2xl flex items-center justify-center">
                    <span className="text-4xl">🤖</span>
                  </div>
                  <div className="text-center space-y-1">
                    <h3 className="font-semibold text-xl" style={{ color: 'var(--text-primary)' }}>Start a conversation</h3>
                    <p className="text-sm max-w-sm" style={{ color: 'var(--text-muted)' }}>Ask me anything about HDFC mutual funds</p>
                  </div>
                </div>
              )}

              {messages.map(message => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>

            <div className="flex overflow-x-auto scrollbar-hide gap-2 py-2 px-4" style={{ borderTop: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)' }}>
              {['Check exit load', 'What is ELSS?', 'Minimum SIP amount?', 'Tax saving tips', 'Fund manager details', 'Riskometer rating?'].map((chip) => (
                <button
                  key={chip}
                  onClick={() => handleSend(chip)}
                  disabled={isLoading || !isOnline}
                  className="whitespace-nowrap text-[13px] px-3.5 py-1.5 rounded-[20px] cursor-pointer flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed hover:border-groww-green hover:text-groww-green hover:bg-[#F0FDF9]"
                  style={{ backgroundColor: 'var(--bg-chip)', border: '1.5px solid var(--border-color)', color: 'var(--text-primary)' }}
                >
                  {chip}
                </button>
              ))}
            </div>

            <div className="p-4" style={{ borderTop: '1px solid var(--border-color)' }}>
              <ChatInput onSend={handleSend} disabled={isLoading || !isOnline} />
            </div>
          </div>
        </main>
      </div>

      <Footer />
      </div>
    </>
  )
}
