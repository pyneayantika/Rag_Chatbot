'use client'
import { useEffect, useState } from 'react'
import { Message } from '../types'

interface Props {
  message: Message
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

function truncateUrl(url: string): string {
  try {
    const u = new URL(url)
    return u.hostname + u.pathname.slice(0, 30) + 
           (u.pathname.length > 30 ? '...' : '')
  } catch {
    return url.slice(0, 50) + '...'
  }
}

export default function ChatMessage({ message }: Props) {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const check = () => setIsDark(
      document.documentElement.classList.contains('dark')
    )
    check()
    const observer = new MutationObserver(check)
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    })
    return () => observer.disconnect()
  }, [])

  if (message.role === 'user') {
    return (
      <div className="flex justify-end items-end gap-2 chat-bubble-user">
        <div className="max-w-[80%] md:max-w-[70%]">
          <div className="bg-groww-green text-white px-4 py-3 rounded-2xl rounded-br-sm shadow-green">
            <p className="text-sm leading-relaxed">
              {message.content}
            </p>
          </div>
          <p className="text-xs mt-1 text-right pr-1" style={{ color: 'var(--text-muted)' }}>
            {formatTime(message.timestamp)}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center flex-shrink-0 mb-6">
          <span className="text-white text-xs font-bold">U</span>
        </div>
      </div>
    )
  }

  const isRefusal = message.is_refusal || message.is_pii

  return (
    <div className="flex justify-start items-end gap-2 chat-bubble-bot">
      <div
        className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 mb-6"
        style={isRefusal
          ? { backgroundColor: '#FEF2F2', border: '1px solid #FECACA' }
          : { backgroundColor: 'var(--bg-bubble-bot)', border: '1px solid var(--border-bot-bubble)' }
        }
      >
        <span className="text-xl">{isRefusal ? '⚠' : '🤖'}</span>
      </div>
      <div className="max-w-[85%] md:max-w-[75%]">
        <div
          className="overflow-hidden"
          style={isRefusal
            ? { borderRadius: '18px 18px 18px 4px', padding: '12px 16px', background: '#FEF2F2', border: '1px solid #FECACA', borderLeft: '3px solid #FF6B6B' }
            : isDark
              ? { borderRadius: '18px 18px 18px 4px', padding: '12px 16px', background: 'rgba(30, 58, 95, 0.75)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', border: '1px solid rgba(255, 255, 255, 0.1)', borderLeft: '4px solid #00D09C', boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)' }
              : { borderRadius: '18px 18px 18px 4px', padding: '12px 16px', background: 'rgba(255, 255, 255, 0.75)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', border: '1px solid rgba(255, 255, 255, 0.5)', borderLeft: '4px solid #00D09C', boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)' }
          }
        >
          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-primary)' }}>
            {message.content}
          </p>

          {!isRefusal && (
            <span className="inline-flex items-center gap-1 mt-3 px-2.5 py-0.5 rounded-full text-xs font-medium" style={{ background: 'linear-gradient(135deg, #F0FDF9, #F5F3FF)', border: '1px solid #8B5CF6', color: '#6D28D9' }}>
              ✓ Verified Source · Official data only
            </span>
          )}

          {message.source_url && 
           !isRefusal && 
           message.source_url.length > 0 && (
            <div className="mt-3 pt-3 space-y-1" style={{ borderTop: '1px solid var(--border-color)' }}>
              <div className="flex items-center gap-1.5">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Source:</span>
                <a
                  href={message.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-groww-green hover:underline font-medium truncate max-w-[250px]"
                  title={message.source_url}
                >
                  {truncateUrl(message.source_url)}
                </a>
                <span className="text-groww-green text-xs">↗</span>
              </div>
              {message.last_updated && (
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Last updated: {message.last_updated}
                </p>
              )}
            </div>
          )}
        </div>
        <p className="text-xs mt-1 pl-1" style={{ color: 'var(--text-muted)' }}>
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
