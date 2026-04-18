import axios from 'axios'
import { ChatResponse } from '../types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 
                'http://localhost:8000'

export async function sendMessage(
  query: string, 
  sessionId: string
): Promise<ChatResponse> {
  try {
    const response = await axios.post(
      `${API_URL}/api/chat`,
      { query, session_id: sessionId },
      { 
        timeout: 60000,
        headers: { 'Content-Type': 'application/json' }
      }
    )
    return response.data
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. Please try again.')
      }
      if (error.response?.status === 500) {
        throw new Error('Server error. Please try again.')
      }
      throw new Error(
        error.response?.data?.detail || 
        'Failed to get response. Please try again.'
      )
    }
    throw new Error('Failed to get response. Please try again.')
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    const response = await fetch(`${API_URL}/health`, {
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    if (!response.ok) return false
    const data = await response.json()
    return data.status === 'ok'
  } catch {
    return false
  }
}
