// Common types for the application

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

export interface Feature {
  icon: React.ComponentType<any>
  title: string
  description: string
}

export interface Stat {
  value: string
  label: string
}

export interface ThemeContextType {
  isDark: boolean
  toggleDark: () => void
}

export type QueryType = 'scientific' | 'creative' | 'general'

export interface ChatContextType {
  messages: Message[]
  isLoading: boolean
  sendMessage: (content: string, queryType?: QueryType, temperature?: number) => Promise<void>
  clearMessages: () => void
}