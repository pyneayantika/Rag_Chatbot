'use client'
import { useState } from 'react'

export default function Disclaimer() {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  return (
    <div className="rounded-xl p-4 relative" style={{ backgroundColor: 'var(--bg-disclaimer)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
      <button
        onClick={() => setVisible(false)}
        className="absolute top-3 right-3 text-lg leading-none"
        style={{ color: 'var(--text-muted)' }}
        aria-label="Close disclaimer"
      >
        ×
      </button>
      <div className="flex items-start gap-3 pr-6">
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-blue-500 text-sm">ℹ</span>
        </div>
        <div className="space-y-2">
          <p className="text-sm" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
            Facts-only Advisory
          </p>
          <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            No investment advice provided. All data sourced exclusively from HDFC AMC, AMFI and SEBI official pages. No personal data stored or processed.
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            <span className="inline-flex items-center gap-1 font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', borderRadius: '20px', padding: '3px 10px', fontSize: '11px', color: 'var(--text-primary)' }}>
              🛡 SEBI Compliant
            </span>
            <span className="inline-flex items-center gap-1 font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', borderRadius: '20px', padding: '3px 10px', fontSize: '11px', color: 'var(--text-primary)' }}>
              ✓ AMFI Registered
            </span>
            <span className="inline-flex items-center gap-1 font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', borderRadius: '20px', padding: '3px 10px', fontSize: '11px', color: 'var(--text-primary)' }}>
              🔒 No PII Stored
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
