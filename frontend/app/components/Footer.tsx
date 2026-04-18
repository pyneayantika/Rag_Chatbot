'use client'
export default function Footer() {
  return (
    <footer className="py-4 px-6" style={{ backgroundColor: 'var(--bg-card)', borderTop: '1px solid var(--border-color)' }}>
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-3">
        <p className="text-xs hidden md:block" style={{ color: 'var(--text-muted)' }}>
          &copy; 2026 HDFC MF FAQ &middot; Powered by Groww
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
            🛡 SEBI Registered
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
            ✓ AMFI Compliant
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium" style={{ backgroundColor: 'var(--bg-chip)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
            🔒 Data Protected
          </span>
        </div>
        <p className="text-xs hidden md:block" style={{ color: 'var(--text-muted)' }}>
          Facts-only. No investment advice.
        </p>
      </div>
    </footer>
  )
}
