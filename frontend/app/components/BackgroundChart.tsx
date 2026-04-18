'use client'
import { useEffect, useState } from 'react'

export default function BackgroundChart() {
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

  return (
    <div
      className="fixed inset-0 pointer-events-none overflow-hidden z-0"
      style={{ opacity: isDark ? 0.4 : 0.85 }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Green gradient for left chart */}
          <linearGradient id="greenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#00D09C" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#00D09C" stopOpacity="0" />
          </linearGradient>

          {/* Purple gradient for right chart */}
          <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.12" />
            <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0" />
          </linearGradient>

          {/* Background gradient */}
          <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F0FDF9" stopOpacity="1" />
            <stop offset="50%" stopColor="#FAFAFA" stopOpacity="1" />
            <stop offset="100%" stopColor="#F5F3FF" stopOpacity="1" />
          </linearGradient>

          {/* Large circle gradient top right */}
          <radialGradient id="circleGrad1" cx="50%" cy="50%">
            <stop offset="0%" stopColor="#00D09C" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#00D09C" stopOpacity="0" />
          </radialGradient>

          {/* Large circle gradient bottom left */}
          <radialGradient id="circleGrad2" cx="50%" cy="50%">
            <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.06" />
            <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Base background */}
        <rect width="1440" height="900" fill="url(#bgGrad)" />

        {/* Large decorative circles */}
        <circle cx="200" cy="800" r="350" fill="url(#circleGrad1)" />
        <circle cx="1300" cy="100" r="300" fill="url(#circleGrad2)" />

        {/* ── DOT GRID PATTERN ── */}
        {Array.from({ length: 20 }).map((_, row) =>
          Array.from({ length: 15 }).map((_, col) => (
            <circle
              key={`dot-${row}-${col}`}
              cx={580 + col * 35}
              cy={200 + row * 35}
              r="1.5"
              fill="#94A3B8"
              opacity="0.25"
            />
          ))
        )}

        {/* ── GREEN LINE CHART (LEFT SIDE) ── */}
        {/* Area fill under green line */}
        <path
          d="M -50 700 L 50 650 L 150 680 L 220 600 L 320 560 L 420 500 L 480 480 L 560 400 L 580 700 Z"
          fill="url(#greenGrad)"
        />
        {/* Green line */}
        <path
          d="M -50 700 L 50 650 L 150 680 L 220 600 L 320 560 L 420 500 L 480 480 L 560 400"
          fill="none"
          stroke="#00D09C"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.7"
        />
        {/* Green line data points */}
        {[
          [50, 650], [150, 680], [220, 600],
          [320, 560], [420, 500], [480, 480], [560, 400]
        ].map(([x, y], i) => (
          <circle
            key={`gp-${i}`}
            cx={x} cy={y} r="5"
            fill="#00D09C" opacity="0.8"
            stroke="white" strokeWidth="2"
          />
        ))}

        {/* ── BAR CHART (BOTTOM LEFT) ── */}
        {[80, 120, 70, 100, 85, 110, 95, 130].map((h, i) => (
          <rect
            key={`bar-${i}`}
            x={30 + i * 55}
            y={820 - h}
            width="35"
            height={h}
            fill="#00D09C"
            opacity="0.15"
            rx="4"
          />
        ))}

        {/* ── PURPLE LINE CHART (RIGHT SIDE) ── */}
        {/* Area fill under purple line */}
        <path
          d="M 860 850 L 920 780 L 1020 750 L 1120 680 L 1200 620 L 1300 540 L 1400 480 L 1500 400 L 1500 850 Z"
          fill="url(#purpleGrad)"
        />
        {/* Purple line */}
        <path
          d="M 860 850 L 920 780 L 1020 750 L 1120 680 L 1200 620 L 1300 540 L 1400 480 L 1500 400"
          fill="none"
          stroke="#8B5CF6"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.6"
        />
        {/* Purple line data points */}
        {[
          [920, 780], [1020, 750], [1120, 680],
          [1200, 620], [1300, 540], [1400, 480]
        ].map(([x, y], i) => (
          <circle
            key={`pp-${i}`}
            cx={x} cy={y} r="5"
            fill="#8B5CF6" opacity="0.7"
            stroke="white" strokeWidth="2"
          />
        ))}

        {/* ── BAR CHART (BOTTOM RIGHT) ── */}
        {[60, 90, 110, 75, 130, 85, 100, 120, 70, 95].map((h, i) => (
          <rect
            key={`rbar-${i}`}
            x={920 + i * 52}
            y={820 - h}
            width="35"
            height={h}
            fill="#8B5CF6"
            opacity="0.12"
            rx="4"
          />
        ))}

        {/* ── DONUT CHART (TOP RIGHT) ── */}
        {/* Background circle */}
        <circle
          cx="1180" cy="160" r="80"
          fill="none" stroke="#E5E7EB"
          strokeWidth="28" opacity="0.5"
        />
        {/* Green segment 65% */}
        <circle
          cx="1180" cy="160" r="80"
          fill="none"
          stroke="#00D09C"
          strokeWidth="28"
          strokeDasharray="327 503"
          strokeDashoffset="0"
          opacity="0.5"
          transform="rotate(-90 1180 160)"
        />
        {/* Purple segment 25% */}
        <circle
          cx="1180" cy="160" r="80"
          fill="none"
          stroke="#8B5CF6"
          strokeWidth="28"
          strokeDasharray="126 503"
          strokeDashoffset="-327"
          opacity="0.4"
          transform="rotate(-90 1180 160)"
        />

        {/* Donut legend */}
        <circle cx="1290" cy="120" r="5" fill="#00D09C" opacity="0.7" />
        <text x="1302" y="125" fontSize="11" fill="#64748B" opacity="0.8">
          Equity Funds 65%
        </text>
        <circle cx="1290" cy="145" r="5" fill="#8B5CF6" opacity="0.7" />
        <text x="1302" y="150" fontSize="11" fill="#64748B" opacity="0.8">
          Debt Funds 25%
        </text>
        <circle cx="1290" cy="170" r="5" fill="#A78BFA" opacity="0.7" />
        <text x="1302" y="175" fontSize="11" fill="#64748B" opacity="0.8">
          Hybrid Funds 10%
        </text>

        {/* ── FLOATING STAT CARD 1 — SIP Growth ── */}
        <rect
          x="30" y="240" width="200" height="90"
          rx="16" fill="white" opacity="0.85"
          filter="drop-shadow(0 4px 12px rgba(0,0,0,0.08))"
        />
        {/* Green icon box */}
        <rect x="50" y="258" width="36" height="36" rx="8" fill="#E8FDF7" />
        {/* Chart icon lines */}
        <path
          d="M 58 285 L 62 278 L 67 282 L 72 272 L 77 276"
          stroke="#00D09C" strokeWidth="2"
          fill="none" strokeLinecap="round"
        />
        {/* SIP Growth text */}
        <text x="96" y="272" fontSize="11" fill="#767676" fontWeight="500">
          SIP Growth
        </text>
        <text x="96" y="292" fontSize="20" fill="#00D09C" fontWeight="700">
          +18.6%
        </text>
        {/* Arrow */}
        <text x="166" y="292" fontSize="16" fill="#00D09C">↗</text>
        <text x="96" y="312" fontSize="10" fill="#94A3B8">
          1Y Return
        </text>

        {/* ── FLOATING STAT CARD 2 — Market Index ── */}
        <rect
          x="1160" y="560" width="220" height="100"
          rx="16" fill="white" opacity="0.85"
          filter="drop-shadow(0 4px 12px rgba(0,0,0,0.08))"
        />
        {/* Purple icon box */}
        <rect x="1178" y="578" width="36" height="36" rx="8" fill="#F5F3FF" />
        {/* Trend icon */}
        <text x="1187" y="601" fontSize="18">📈</text>
        {/* Market Index text */}
        <text x="1224" y="592" fontSize="11" fill="#767676" fontWeight="500">
          Market Index
        </text>
        <text x="1224" y="615" fontSize="20" fill="#8B5CF6" fontWeight="700">
          +12.4%
        </text>
        {/* Arrow */}
        <text x="1310" y="615" fontSize="16" fill="#8B5CF6">↗</text>
        <text x="1224" y="638" fontSize="10" fill="#94A3B8">
          Nifty 50 (1Y)
        </text>
      </svg>
    </div>
  )
}
