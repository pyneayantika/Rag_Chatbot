import type { Config } from 'tailwindcss'
const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'groww-green': '#00D09C',
        'groww-dark': '#1A1A2E',
        'groww-navy': '#16213E',
        'groww-card': '#F7F8FA',
        'groww-text': '#2D2D2D',
        'groww-muted': '#767676',
        'groww-light': '#E8FDF7',
        'groww-border': '#E0E0E0',
        'groww-red': '#FF6B6B',
        'groww-yellow': '#FFB800',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 12px rgba(0,0,0,0.08)',
        'card-hover': '0 4px 20px rgba(0,0,0,0.12)',
        'green': '0 4px 15px rgba(0,208,156,0.3)',
      },
      borderRadius: {
        'xl2': '16px',
        'xl3': '20px',
        'xl4': '24px',
      }
    },
  },
  plugins: [],
}
export default config
