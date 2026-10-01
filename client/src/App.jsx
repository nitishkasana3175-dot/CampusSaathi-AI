import React, { useState, useEffect } from 'react'

export default function App() {
  const [view, setView] = useState('home') // home | chat | login
  const [healthStatus, setHealthStatus] = useState('Checking backend...')
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! I am CampusSaathi AI. Ask me anything about ABES Engineering College fees, admissions, or campus facilities.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loginData, setLoginData] = useState({ email: '', password: '' })
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealthStatus(`Backend Online: ${data.status} (v${data.version})`))
      .catch(err => setHealthStatus('Backend Offline / RAG Unavailable'))
  }, [])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = { sender: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      })

      if (!res.ok) {
        throw new Error('RAG Service unavailable')
      }

      const data = await res.json()
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: data.answer || data.reply,
        sources: data.sources || []
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Error: Unable to connect to backend or RAG service. Please ensure server and FastAPI service are active.',
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleLoginSubmit = (e) => {
    e.preventDefault()
    if (loginData.email && loginData.password) {
      setUser({ email: loginData.email, role: 'student' })
      setView('chat')
    }
  }

  return (
    <div>
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="brand" onClick={() => setView('home')} style={{ cursor: 'pointer' }}>
          🎓 CampusSaathi AI
        </div>
        <ul className="nav-links">
          <li><a href="#home" onClick={(e) => { e.preventDefault(); setView('home') }}>Home</a></li>
          <li><a href="#features" onClick={(e) => { e.preventDefault(); setView('home'); setTimeout(() => document.getElementById('features')?.scrollIntoView({behavior: 'smooth'}), 100) }}>Features</a></li>
          {user ? (
            <li><span style={{ fontWeight: 600, color: 'var(--primary)' }}>👤 {user.email}</span></li>
          ) : (
            <li><a href="#login" onClick={(e) => { e.preventDefault(); setView('login') }}>Login</a></li>
          )}
          <li>
            <button className="btn-primary" onClick={() => setView('chat')}>
              Start Chatting 💬
            </button>
          </li>
        </ul>
      </nav>

      {/* Main Views */}
      {view === 'home' && (
        <main>
          <section className="hero" id="home">
            <span className="badge">✨ ABES Engineering College Assistant</span>
            <h1>Your Intelligent University Guide, <span>CampusSaathi AI</span></h1>
            <p>
              Get accurate, instant answers for courses, fee structures, admissions, placements, and campus guidelines grounded directly in official university documents.
            </p>
            <div className="hero-actions">
              <button className="btn-primary" onClick={() => setView('chat')}>Ask Question Now</button>
              <button className="btn-outline" onClick={() => setView('login')}>Student Login</button>
            </div>

            <div className="health-status">
              ⚙️ <strong>System Health:</strong> {healthStatus}
            </div>
          </section>

          <section className="features" id="features">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--primary)' }}>Why CampusSaathi AI?</h2>
            <div className="features-grid">
              <div className="feature-card">
                <h3>⚡ Real-Time RAG</h3>
                <p>Retrieves grounded context from official ABES FAQ PDFs using Google Gemini and FAISS.</p>
              </div>
              <div className="feature-card">
                <h3>📌 Source Verification</h3>
                <p>Provides exact PDF document citations and page references with every answer.</p>
              </div>
              <div className="feature-card">
                <h3>🔒 Secure & Reliable</h3>
                <p>Ensures zero hallucinated answers when document evidence is insufficient.</p>
              </div>
            </div>
          </section>
        </main>
      )}

      {view === 'login' && (
        <main style={{ padding: '4rem 1.5rem', display: 'flex', justifyContent: 'center' }}>
          <div style={{ background: 'white', padding: '2.5rem', borderRadius: '12px', border: '1px solid var(--border)', maxWidth: '400px', width: '100%' }}>
            <h2 style={{ color: 'var(--primary)', marginBottom: '1.5rem', textAlign: 'center' }}>CampusSaathi Login</h2>
            <form onSubmit={handleLoginSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', fontWeight: 600 }}>University Email</label>
                <input
                  type="email"
                  required
                  placeholder="student@abes.ac.in"
                  value={loginData.email}
                  onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '6px' }}
                />
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.4rem', fontWeight: 600 }}>Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  style={{ width: '100%', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '6px' }}
                />
              </div>
              <button type="submit" className="btn-primary" style={{ width: '100%' }}>Login</button>
            </form>
            <p style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Or <a href="#chat" onClick={() => setView('chat')} style={{ color: 'var(--primary)' }}>continue as Guest</a>
            </p>
          </div>
        </main>
      )}

      {view === 'chat' && (
        <main style={{ padding: '2rem 1rem' }}>
          <div className="chat-section">
            <div className="chat-header">
              <span style={{ fontWeight: 600 }}>CampusSaathi AI Assistant</span>
              <button className="btn-outline" style={{ color: 'white', borderColor: 'white', padding: '0.3rem 0.75rem', fontSize: '0.8rem' }} onClick={() => setView('home')}>Back to Home</button>
            </div>

            <div className="chat-box">
              {messages.map((m, idx) => (
                <div key={idx} className={`msg ${m.sender}`}>
                  <div>{m.text}</div>
                  {m.sources && m.sources.length > 0 && (
                    <div className="sources">
                      📚 Sources: {m.sources.join(', ')}
                    </div>
                  )}
                </div>
              ))}
              {loading && <div className="msg bot">Thinking & searching FAQ database... 🧠</div>}
            </div>

            <form className="chat-input-area" onSubmit={handleSendMessage}>
              <input
                type="text"
                placeholder="Ask about fees, courses, hostel rules..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button type="submit" className="btn-primary" disabled={loading}>Send</button>
            </form>
          </div>
        </main>
      )}
    </div>
  )
}
