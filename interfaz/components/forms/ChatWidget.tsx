import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader2, Settings } from 'lucide-react'
import { Button } from '../ui/button'
import { useChat } from '../../context/ChatContext'
import { QueryType } from '../../types'

// Using Message type from context instead of local interface

const suggestionChips = [
  { text: "Show me sales trends for Q4", type: 'general' as QueryType },
  { text: "What's our top performing product?", type: 'general' as QueryType },
  { text: "Explain quantum computing principles", type: 'scientific' as QueryType },
  { text: "Brainstorm innovative product ideas", type: 'creative' as QueryType }
]

export default function ChatWidget() {
  const { messages, isLoading, sendMessage } = useChat()
  const [inputValue, setInputValue] = useState('')
  const [charCount, setCharCount] = useState(0)
  const [queryType, setQueryType] = useState<QueryType>('general')
  const [customTemperature, setCustomTemperature] = useState<number | undefined>(undefined)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const maxChars = 500

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSubmit = async (messageText?: string): Promise<void> => {
    const text = messageText || inputValue.trim()
    if (!text || isLoading) return

    try {
      await sendMessage(text, queryType, customTemperature)
      setInputValue('')
      setCharCount(0)
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }

  const handleSuggestionClick = (suggestion: { text: string; type: QueryType }) => {
    setQueryType(suggestion.type)
    handleSubmit(suggestion.text)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    const value = e.target.value
    if (value.length <= maxChars) {
      setInputValue(value)
      setCharCount(value.length)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const formatMessage = (content: string): JSX.Element[] => {
    return content.split('\n').map((line: string, index: number) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-brand-blue to-brand-teal p-6 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Jarvis Analyst</h3>
            <p className="text-white/80 text-sm">AI Data Assistant</p>
          </div>
          <div className="ml-auto">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-[80%] ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user' 
                    ? 'bg-brand-blue text-white' 
                    : message.role === 'assistant'
                    ? 'bg-brand-teal text-white'
                    : 'bg-gray-400 text-white'
                }`}>
                  {message.role === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : message.role === 'assistant' ? (
                    <Bot className="h-4 w-4" />
                  ) : (
                    <span className="text-xs">!</span>
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-brand-blue text-white'
                    : message.role === 'assistant'
                    ? 'bg-white border border-gray-200 text-gray-800'
                    : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                }`}>
                  <div className="text-sm leading-relaxed">
                    {formatMessage(message.content)}
                  </div>
                  <div className={`text-xs mt-2 opacity-70 ${
                    message.role === 'user' ? 'text-white/70' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-brand-teal rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin text-brand-teal" />
                  <span className="text-sm text-gray-600">Analyzing your data...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      {messages.length === 1 && (
        <div className="px-6 py-4 bg-white border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestionChips.map((suggestion, index) => (
              <motion.button
                key={index}
                className="px-3 py-2 bg-gray-100 hover:bg-brand-blue hover:text-white text-sm rounded-full transition-colors duration-200"
                onClick={() => handleSuggestionClick(suggestion)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {suggestion.text}
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Query Type Selection */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Query Type:</span>
            <select
              value={queryType}
              onChange={(e) => setQueryType(e.target.value as QueryType)}
              className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-brand-teal focus:border-transparent"
            >
              <option value="general">General (Temp: 0.7)</option>
              <option value="scientific">Scientific (Temp: 0.1)</option>
              <option value="creative">Creative (Temp: 1.3)</option>
            </select>
          </div>
          
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-1 text-sm text-gray-600 hover:text-brand-teal transition-colors"
          >
            <Settings className="h-4 w-4" />
            <span>Advanced</span>
          </button>
        </div>
        
        {showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 pt-3 border-t border-gray-200"
          >
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Custom Temperature:</label>
              <input
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={customTemperature || ''}
                onChange={(e) => setCustomTemperature(e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="0.0 - 2.0"
                className="text-sm border border-gray-300 rounded-lg px-3 py-1 w-24 focus:outline-none focus:ring-2 focus:ring-brand-teal focus:border-transparent"
              />
              <span className="text-xs text-gray-500">Leave empty to use query type default</span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-gray-200">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your data..."
              className="w-full resize-none border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-brand-teal focus:border-transparent transition-all duration-200"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
              disabled={isLoading}
            />
            <div className="flex justify-between items-center mt-2">
              <span className={`text-xs ${
                charCount > maxChars * 0.8 ? 'text-red-500' : 'text-gray-400'
              }`}>
                {charCount}/{maxChars}
              </span>
              <span className="text-xs text-gray-400">
                Press Enter to send, Shift+Enter for new line
              </span>
            </div>
          </div>
          
          <Button
            onClick={() => handleSubmit()}
            disabled={!inputValue.trim() || isLoading}
            className="bg-brand-teal hover:bg-brand-teal/90 text-white p-3 rounded-xl transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}