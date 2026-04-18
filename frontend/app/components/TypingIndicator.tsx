'use client'
export default function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="rounded-2xl rounded-bl-sm shadow-card border-l-4 border-groww-green px-4 py-3" style={{ backgroundColor: 'var(--bg-card)' }}>
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-6 rounded-full bg-groww-light 
                          flex items-center justify-center 
                          text-xs font-bold text-groww-green 
                          flex-shrink-0">
            AI
          </div>
          <div className="flex items-center gap-1 px-2">
            {[0,1,2].map(i => (
              <div
                key={i}
                className="w-2 h-2 bg-groww-green rounded-full 
                           typing-dot"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
