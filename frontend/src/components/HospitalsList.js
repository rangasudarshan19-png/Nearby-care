import React from 'react';
import Reviews from './Reviews';

function HospitalsList({ hospitals, onAddFavorite, onViewDetails }) {
  return (
    <div className="hospitals-list">
      <h2 className="results-heading">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Found {hospitals.length} Hospital{hospitals.length !== 1 ? 's' : ''}
      </h2>
      
      {hospitals.map((hospital, index) => (
        <div key={hospital.id || index} className="hospital-card">
          <div className="hospital-card-top">
            <h3>
              {hospital.name}
              {hospital.ai_score > 0.4 && (
                <span className="recommended-badge">AI Recommended</span>
              )}
            </h3>
            {typeof hospital.rating === 'number' && hospital.rating > 0 && (
              <div className="rating-pill">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                {hospital.rating.toFixed(1)}
                {hospital.user_ratings_total > 0 && <span className="review-count">({hospital.user_ratings_total})</span>}
              </div>
            )}
          </div>
          <p className="hospital-address">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            {hospital.address || 'Address not available'}
          </p>
          
          <div className="hospital-meta">
            {hospital.distance && (
              <span className="meta-item distance-meta">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {hospital.distance.toFixed(2)} km
              </span>
            )}
            {hospital.phone && (
              <span className="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.44 2.1 1.22 4.1 2.81 5.63"/></svg>
                {hospital.phone}
              </span>
            )}
            {hospital.type && (
              <span className="meta-item type-meta">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                {hospital.type}
              </span>
            )}
            {hospital.website && (
              <a href={hospital.website} target="_blank" rel="noopener noreferrer" className="meta-item website-link">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
                Website
              </a>
            )}
          </div>
          
          {hospital.emergency === 'yes' && (
            <div className="emergency-tag">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              24/7 Emergency Services
            </div>
          )}
          
          <div className="card-actions">
            <button 
              className="btn-small btn-primary"
              onClick={() => onViewDetails && onViewDetails(hospital)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              View Details
            </button>
            <button 
              className="btn-small btn-fav"
              onClick={() => onAddFavorite(hospital)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
              Favorite
            </button>
            <button 
              className="btn-small btn-directions"
              onClick={() => {
                window.open(
                  `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`,
                  '_blank'
                );
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
              Directions
            </button>
          </div>

          <Reviews hospital={hospital} />
        </div>
      ))}
    </div>
  );
}

export default HospitalsList;
