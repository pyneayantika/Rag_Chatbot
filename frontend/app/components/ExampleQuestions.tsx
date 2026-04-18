'use client'

interface Props {
  onSelect: (question: string) => void
  disabled: boolean
}

const QUESTIONS = [
  { 
    text: 'Expense ratio of HDFC Mid Cap?',
    icon: '📊'
  },
  { 
    text: 'ELSS lock-in period?',
    icon: '🔒'
  },
  { 
    text: 'How to download capital gains statement?',
    icon: '📥'
  },
]

export default function ExampleQuestions({ 
  onSelect, disabled 
}: Props) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-groww-muted 
                    uppercase tracking-wider">
        Try asking
      </p>
      <div className="flex flex-wrap gap-2">
        {QUESTIONS.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q.text)}
            disabled={disabled}
            className="flex items-center gap-2 px-4 py-2 
                       bg-white border border-groww-border 
                       rounded-full text-sm text-groww-text 
                       hover:border-groww-green 
                       hover:bg-groww-light 
                       hover:text-groww-green
                       disabled:opacity-50 
                       disabled:cursor-not-allowed
                       transition-all duration-200 
                       shadow-sm hover:shadow-card
                       font-medium"
          >
            <span>{q.icon}</span>
            <span>{q.text}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
