import React, { useState, useEffect } from 'react';
import { API_URL } from '../config';

function SearchHistory({ onLocationSelect }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/search-history?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading search history...</p>
      </div>
    );
  }

  return (
    <div className="hospitals-list">
      <h2>Recent Searches ({history.length})</h2>
      
      {history.length === 0 ? (
        <div className="info">
          <p>No search history yet. Start searching for hospitals!</p>
        </div>
      ) : (
        history.map((item) => (
          <div key={item.id} className="hospital-card">
            <h3>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{verticalAlign: 'middle', marginRight: '4px'}}>
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {item.location}
            </h3>
            <p>Coordinates: {item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}</p>
            <p className="hospital-address">
              Searched: {new Date(item.search_date).toLocaleString()}
            </p>
            
            <div className="card-actions">
              <button 
                className="btn-directions"
                onClick={() => onLocationSelect(item.location)}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
                Search Again
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default SearchHistory;
