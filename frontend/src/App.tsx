
import { useState, type FormEvent } from 'react'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  status?: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! I can help you manage your AWS ECS service. Try asking me to scale your service, change CPU or memory, or update its image version.',
    },
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const message = input.trim()
    if (!message || loading) return

    setMessages((previous) => [
      ...previous,
      { role: 'user', content: message },
    ])

    setInput('')
    setLoading(true)

    try {
      const response = await fetch('/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed.')
      }

      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content: data.response,
          status: data.status,
        },
      ])
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content:
            error instanceof Error
              ? error.message
              : 'Something went wrong. Please try again.',
          status: 'failed',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-container">
      <header className="header">
        <div>
          <h1>Cloud Control</h1>
          <p>Manage your AWS ECS infrastructure using plain English.</p>
        </div>
        <span className="status-indicator">● ECS Manager</span>
      </header>

      <section className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-role">
                {message.role === 'user' ? 'You' : 'Assistant'}
              </div>

              <div className="message-content">
                {message.content}
              </div>

              {message.status && (
                <span className={`message-status ${message.status}`}>
                  {message.status}
                </span>
              )}
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-role">Assistant</div>
              <div className="message-content">Processing your request...</div>
            </div>
          )}
        </div>

        <form className="chat-input" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="e.g. Run 3 containers"
            disabled={loading}
          />

          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>

        <p className="hint">
          Example: "Scale the service to 2 tasks"
        </p>
      </section>
    </main>
  )
}

export default App
