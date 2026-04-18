'use client'

interface Props {
  isOnline: boolean
  isChecking: boolean
}

export default function StatusBanner({ 
  isOnline, isChecking 
}: Props) {
  if (isChecking) return null
  if (isOnline) return null

  return (
    <div className="rounded-xl px-4 py-3 flex items-center gap-2 status-banner-error" style={{ backgroundColor: 'var(--bg-status-error, #FEF2F2)', border: '1px solid var(--border-status-error, #FECACA)' }}>
      <div className="w-2 h-2 bg-groww-red rounded-full"/>
      <p className="text-sm font-medium" style={{ color: 'var(--text-status-error, #FF6B6B)' }}>
        Cannot connect to server. 
        Please start the API backend and refresh.
      </p>
    </div>
  )
}
