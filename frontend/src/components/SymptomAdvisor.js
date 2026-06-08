import React, { useState, useEffect, useRef } from 'react';
import { apiPost } from '../utils/apiClient';

function SymptomAdvisor() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI Health Assistant. Please describe your symptoms, and I\'ll help you understand what might be going on and suggest the best course of action. Would you like to share your location so I can recommend nearby hospitals if needed?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);
  const [locationPermission, setLocationPermission] = useState('prompt');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const requestLocation = () => {
    if (navigator.geolocation) {
      setLocationPermission('requesting');
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          setLocation(coords);
          setLocationPermission('granted');
          setMessages(prev => [...prev, {
            role: 'system',
            content: 'Location access granted. I can now suggest nearby hospitals if needed.'
          }]);
        },
        (error) => {
          setLocationPermission('denied');
          setMessages(prev => [...prev, {
            role: 'system',
            content: 'Location access denied. I can still help with symptom analysis, but will not be able to suggest nearby hospitals.'
          }]);
        }
      );
    } else {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Geolocation is not supported by your browser.'
      }]);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
      const data = await apiPost('/api/symptom-chat', {
        message: userMessage,
        location: location,
        chat_history: messages.filter(m => m.role !== 'system')
      }, { signal: controller.signal });

      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }]);

      // If AI suggests hospitals and location is available, add them
      if (data.suggested_hospitals && data.suggested_hospitals.length > 0) {
        setMessages(prev => [...prev, {
          role: 'hospitals',
          hospitals: data.suggested_hospitals
        }]);
      }

    } catch (error) {
      const message = error.name === 'AbortError'
        ? 'The assistant is taking too long to respond. Please try again in a moment.'
        : error.message;
      setMessages(prev => [...prev, {
        role: 'error',
        content: message
      }]);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Chat cleared. How can I help you today?'
    }]);
  };

  return (
    <div className="symptom-advisor-chat">
      <div className="chat-header">
        <div className="header-content">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <h2>AI Health Assistant</h2>
        </div>
        <div className="header-actions">
          {locationPermission === 'prompt' && (
            <button onClick={requestLocation} className="btn-location" title="Share Location">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              Share Location
            </button>
          )}
          {locationPermission === 'granted' && (
            <span className="location-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              Location Active
            </span>
          )}
          <button onClick={clearChat} className="btn-clear" title="Clear Chat">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message message-${message.role}`}>
            {message.role === 'assistant' && (
              <div className="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5"></path>
                  <path d="M2 12l10 5 10-5"></path>
                </svg>
              </div>
            )}
            {message.role === 'user' && (
              <div className="message-avatar user-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            )}
            <div className="message-content">
              {message.role === 'hospitals' ? (
                <div className="hospital-suggestions">
                  <h4>Recommended Nearby Hospitals:</h4>
                  {message.hospitals.map((hospital, idx) => (
                    <div key={idx} className="hospital-card-mini">
                      <div className="hospital-info">
                        <strong>{hospital.name}</strong>
                        <p>{hospital.address}</p>
                        <span className="distance">{hospital.distance}</span>
                      </div>
                      <div className="hospital-actions">
                        <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-mini"
                        >
                          Directions
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message message-assistant">
            <div className="message-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              </svg>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your symptoms... (e.g., I have a headache and fever)"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} className="btn-send">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>

      <div className="chat-disclaimer">
        This AI assistant provides general information only. Always consult a healthcare professional for medical advice.
      </div>
    </div>
  );
}

export default SymptomAdvisor;
