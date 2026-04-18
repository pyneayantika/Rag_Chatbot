export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  source_url?: string
  last_updated?: string
  is_refusal?: boolean
  is_pii?: boolean
  timestamp: Date
}

export interface ChatResponse {
  answer: string
  source_url: string
  last_updated: string
  is_refusal: boolean
  is_pii: boolean
  session_id: string
  query_type: string
}

export interface ApiError {
  detail: string
}
