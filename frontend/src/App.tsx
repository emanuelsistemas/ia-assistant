import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

function App() {
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [lastError, setLastError] = useState<string | null>(null)

  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch('http://5.161.236.34:8000/health')
        if (response.ok) {
          const data = await response.json()
          if (data.status === 'healthy') {
            setServerStatus('online')
            setLastError(null)
          } else {
            setServerStatus('offline')
            setLastError(`Server status: ${data.status}. OpenAI client: ${data.openai_client}`)
          }
        } else {
          setServerStatus('offline')
          setLastError('Server responded with error')
        }
      } catch (error) {
        setServerStatus('offline')
        setLastError('Could not connect to server. Please check if the server is running.')
      }
    }

    checkServerStatus()
    const interval = setInterval(checkServerStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const testLLM = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://5.161.236.34:8000/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ message: 'Test message: Please respond with "LLM API is working correctly!"' })
      })

      if (!response.ok) {
        const errorData = await response.text()
        console.error('API Test Error:', errorData)
        setLastError(`API Test Failed: ${errorData}`)
        throw new Error(`Failed to test API: ${errorData}`)
      }

      const data = await response.json()
      console.log('API Test Response:', data)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'LLM API Test Result: ' + data.response 
      }])
      setLastError(null)
    } catch (error) {
      console.error('Test Error:', error)
      setLastError(error instanceof Error ? error.message : 'Unknown error during test')
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'LLM API Test Failed. Check console for details.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user' as const, content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://5.161.236.34:8000/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ message: input })
      })

      if (!response.ok) {
        const errorData = await response.text()
        console.error('API Error:', errorData)
        setLastError(`API Error: ${errorData}`)
        throw new Error(`Failed to get response: ${errorData}`)
      }

      const data = await response.json()
      console.log('API Response:', data)
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      setLastError(null)
    } catch (error) {
      console.error('Error:', error)
      setLastError(error instanceof Error ? error.message : 'Unknown error')
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8 relative">
          <div className="absolute left-0 top-0 flex items-center space-x-2">
            <div className={`h-3 w-3 rounded-full ${
              serverStatus === 'online' ? 'bg-green-500' :
              serverStatus === 'offline' ? 'bg-red-500' :
              'bg-yellow-500 animate-pulse'
            }`} />
            <span className="text-sm">{serverStatus.charAt(0).toUpperCase() + serverStatus.slice(1)}</span>
          </div>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={testLLM}
              disabled={isLoading || serverStatus === 'offline'}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Test LLM API
            </button>
          </div>

          {lastError && (
            <div className="text-red-400 text-sm mt-2 max-w-md mx-auto">
              {lastError}
              {lastError.includes('OpenAI client: not initialized') && (
                <div className="mt-1 text-xs">
                  Please check if the OpenAI API key is configured correctly in the server settings.
                </div>
              )}
            </div>
          )}
        </header>

        <div className="bg-gray-800 rounded-lg p-4 mb-4 h-[60vh] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <p>Start a conversation by sending a message below.</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
              >
                <div
                  className={`inline-block p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}`}
                >
                  {message.role === 'assistant' ? (
                    <div className="prose prose-invert max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  ) : (
                    message.content
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="text-left mb-4">
              <div className="inline-block p-3 rounded-lg bg-gray-700">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-3 rounded-lg bg-gray-800 text-white border border-gray-700 focus:outline-none focus:border-blue-500 transition-colors"
            disabled={isLoading || serverStatus === 'offline'}
          />
          <button
            type="submit"
            disabled={isLoading || serverStatus === 'offline'}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
