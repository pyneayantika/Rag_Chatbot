import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'HDFC MF FAQ Assistant | Powered by Groww',
  description: 'Facts-only mutual fund FAQ chatbot. ' +
    'Get verified information about HDFC Mutual Fund schemes. ' +
    'No investment advice.',
  keywords: 'HDFC mutual fund, FAQ, expense ratio, ' +
    'exit load, ELSS, SIP, facts only',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-groww-card">
        {children}
      </body>
    </html>
  )
}
