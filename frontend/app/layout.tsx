import type { Metadata } from 'next'
import './globals.css'

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
    <html lang="en">
      <head>
        <link rel="preconnect" 
              href="https://fonts.googleapis.com" />
        <link rel="preconnect" 
              href="https://fonts.gstatic.com" 
              crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-groww-card">
        {children}
      </body>
    </html>
  )
}
