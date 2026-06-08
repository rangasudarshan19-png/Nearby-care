import React, { useState, useEffect } from 'react';
import { apiDelete, apiGet } from '../utils/apiClient';
import { Alert, EmptyState, Spinner } from './ui';

function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    setError('');
    try {
      const data = await apiGet('/api/favorites');
      setFavorites(data);
    } catch (error) {
      setError(error.message || 'Failed to load favorites.');
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (id) => {
    setError('');
    try {
      await apiDelete(`/api/favorites/${id}`);
      setFavorites(favorites.filter(fav => fav.id !== id));
    } catch (error) {
      setError(error.message || 'Failed to remove favorite.');
    }
  };

  if (loading) {
    return (
      <Spinner label="Loading favorites..." />
    );
  }

  return (
    <div className="hospitals-list">
      <h2 className="results-heading">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
        My Favorites ({favorites.length})
      </h2>
      <Alert type="error">{error}</Alert>
      
      {favorites.length === 0 ? (
        <EmptyState
          title="No favorite hospitals yet"
          description="Add hospitals from your search results and they will appear here."
        />
      ) : (
        favorites.map((favorite) => (
          <div key={favorite.id} className="hospital-card">
            <h3>{favorite.hospital_name}</h3>
            <p className="hospital-address">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {favorite.hospital_address}
            </p>
            <p className="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              Added: {new Date(favorite.added_date).toLocaleDateString()}
            </p>
            
            <div className="card-actions">
              <button 
                className="btn-small btn-danger"
                onClick={() => handleRemove(favorite.id)}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                Remove
              </button>
              <button 
                className="btn-small btn-directions"
                onClick={() => {
                  window.open(
                    `https://www.google.com/maps/dir/?api=1&destination=${favorite.latitude},${favorite.longitude}`,
                    '_blank'
                  );
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                Directions
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default Favorites;
