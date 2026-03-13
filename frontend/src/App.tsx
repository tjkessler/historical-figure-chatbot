
import React, { useEffect, useState, useRef } from 'react';
import { Persona, ChatMessage } from './types';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API_BASE}/personas/`)
      .then(res => res.json())
      .then(setPersonas)
      .catch(() => setPersonas([]));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handlePersonaSelect = (persona: Persona) => {
    setSelectedPersona(persona);
    setMessages([]);
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || !selectedPersona) return;
    const userMsg: ChatMessage = { role: 'user', message: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: String(selectedPersona.id),
          message: input,
          history: messages.map(m => ({ role: m.role, message: m.message }))
        })
      });
      const data = await resp.json();
      setMessages(prev => [...prev, { role: 'bot', message: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', message: '[Error contacting server]' }]);
    }
    setLoading(false);
  };

  return (
    <div className="App" style={{ maxWidth: 900, margin: '2rem auto', fontFamily: 'sans-serif', background: '#f5f7fa', borderRadius: 16, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', padding: 32 }}>
      <h1 style={{ textAlign: 'center', marginBottom: 32, letterSpacing: 1 }}>Historical Figure Chatbot</h1>
      {!selectedPersona ? (
        <div>
          <h2 style={{ textAlign: 'center', marginBottom: 24 }}>Select a Historical Figure</h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 24,
            justifyItems: 'center',
            alignItems: 'stretch',
            margin: '0 auto',
            maxWidth: 800
          }}>
            {personas.map(p => (
              <button
                key={p.id}
                onClick={() => handlePersonaSelect(p)}
                style={{
                  padding: '1.5rem 1rem',
                  borderRadius: 14,
                  border: '1px solid #d1d5db',
                  background: '#fff',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  cursor: 'pointer',
                  transition: 'box-shadow 0.2s, border 0.2s, transform 0.18s cubic-bezier(.4,1.5,.5,1)',
                  minHeight: 120,
                  width: '100%',
                  maxWidth: 260,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.1rem',
                  fontWeight: 500,
                  color: '#222',
                  outline: 'none',
                }}
                onMouseOver={e => {
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.13)';
                  e.currentTarget.style.transform = 'translateY(-3px)';
                }}
                onMouseOut={e => {
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
                  e.currentTarget.style.transform = 'none';
                }}
              >
                <span style={{ fontWeight: 700, fontSize: '1.2rem', marginBottom: 4 }}>{p.name}</span>
                <span style={{ color: '#666', fontSize: '1rem', marginBottom: 8 }}>({p.era})</span>
                <span style={{ color: '#888', fontSize: '0.95rem', fontStyle: 'italic', textAlign: 'center' }}>{p.bio?.slice(0, 80)}{p.bio && p.bio.length > 80 ? '...' : ''}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <button onClick={() => setSelectedPersona(null)} style={{ marginBottom: '1rem', background: 'none', border: 'none', color: '#0077cc', cursor: 'pointer', fontSize: '1rem' }}>← Change Persona</button>
          <h2 style={{ marginBottom: 8 }}>{selectedPersona.name} <span style={{ color: '#666', fontSize: '1rem' }}>({selectedPersona.era})</span></h2>
          <p style={{ fontStyle: 'italic', color: '#444', marginBottom: 20 }}>{selectedPersona.bio}</p>
          <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 16, minHeight: 200, background: '#fafafa', marginBottom: 16, maxHeight: 500, overflowY: 'auto' }}>
            {messages.length === 0 && <div style={{ color: '#888' }}>Start the conversation!</div>}
            {messages.map((msg, idx) => (
              <div key={idx} style={{ margin: '0.5rem 0', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                <span style={{
                  display: 'inline-block',
                  background: msg.role === 'user' ? '#d1e7dd' : '#e2e3e5',
                  color: '#222',
                  borderRadius: 12,
                  padding: '0.5rem 1rem',
                  maxWidth: '80%',
                  wordBreak: 'break-word',
                  boxShadow: msg.role === 'user' ? '0 1px 4px #b7e4c7' : '0 1px 4px #dee2e6',
                }}>
                  {msg.message}
                </span>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleSend} style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type your message..."
              style={{ flex: 1, padding: '0.5rem', borderRadius: 8, border: '1px solid #ccc', fontSize: '1.05rem' }}
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading || !input.trim()} style={{ padding: '0.5rem 1.2rem', borderRadius: 8, background: '#0077cc', color: '#fff', border: 'none', fontWeight: 600, fontSize: '1.05rem', cursor: loading ? 'not-allowed' : 'pointer', transition: 'background 0.2s' }}>
              {loading ? '...' : 'Send'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
