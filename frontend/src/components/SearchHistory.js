import React, { useState, useEffect } from 'react';
import { apiGet } from '../utils/apiClient';
import { Alert, EmptyState, Spinner } from './ui';

function SearchHistory({ onLocationSelect }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setError('');
    try {
      const data = await apiGet('/api/search-history?limit=20');
      setHistory(data);
    } catch (error) {
      setError(error.message || 'Failed to load search history.');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Spinner label="Loading search history..." />
    );
  }

  return (
    <div className="hospitals-list">
      <h2>Recent Searches ({history.length})</h2>
      <Alert type="error">{error}</Alert>
      
      {history.length === 0 ? (
        <EmptyState
          title="No search history yet"
          description="Start searching for hospitals and your recent searches will appear here."
        />
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
