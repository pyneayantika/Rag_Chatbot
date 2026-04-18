'use client'
import { useState, useRef, KeyboardEvent } from 'react'

interface Props {
  onSend: (message: string) => void
  disabled: boolean
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }

  return (
    <div className="flex items-end gap-2 focus-within:border-groww-green" style={{ backgroundColor: 'var(--bg-input)', borderRadius: '50px', border: '1.5px solid var(--border-color)', padding: '8px 8px 8px 20px' }}>
      <textarea
        ref={textareaRef}
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        disabled={disabled}
        placeholder="Ask about HDFC Mutual Fund schemes..."
        rows={1}
        className="flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none py-2 max-h-[120px] disabled:opacity-50"
        style={{ color: 'var(--text-primary)' }}
      />
      <button
        className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-200 hover:scale-105 active:scale-95"
        style={{ background: '#00D09C', boxShadow: '0 2px 8px rgba(0,208,156,0.4)' }}
        onMouseEnter={e => (e.currentTarget.style.background = '#00B589')}
        onMouseLeave={e => (e.currentTarget.style.background = '#00D09C')}
        aria-label="Voice input"
        type="button"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="1" width="6" height="11" rx="3"/>
          <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      </button>
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="w-11 h-11 bg-groww-green rounded-xl flex items-center justify-center flex-shrink-0 shadow-green hover:bg-green-400 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none transition-all duration-200 active:scale-95"
        aria-label="Send message"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" 
             fill="none" stroke="white" 
             strokeWidth="2.5" strokeLinecap="round" 
             strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  )
}
