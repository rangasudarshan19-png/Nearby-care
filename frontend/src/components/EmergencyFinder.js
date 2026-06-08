import React, { useState, useEffect, useCallback } from 'react';
import { getEmergencyNumbersByLocation, formatEmergencyInfo } from '../utils/emergencyNumbers';
import { apiPost } from '../utils/apiClient';
import { Alert, Spinner } from './ui';

function EmergencyFinder({ onClose, onHospitalsFound }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [emergencyHospitals, setEmergencyHospitals] = useState([]);
  const [emergencyNumbers, setEmergencyNumbers] = useState(null);
  const [userCountry, setUserCountry] = useState('');

  const findEmergencyHospitals = useCallback(async () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocation not supported by your browser');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        try {
          const data = await apiPost('/api/search-hospitals-osm', {
            lat: latitude,
            lon: longitude,
            location: 'My Location',
            radius: 10,
            emergencyOnly: true,
            sortBy: 'nearby'
          });
          setEmergencyHospitals(data.hospitals || []);
          if (onHospitalsFound) {
            onHospitalsFound(data.hospitals || []);
          }
        } catch (err) {
          setError(err.message || 'Failed to find emergency hospitals');
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        setError(`Location error: ${err.message}`);
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [onHospitalsFound]);

  useEffect(() => {
    findEmergencyHospitals();
    
    // Get emergency numbers based on location
    getEmergencyNumbersByLocation().then(numbers => {
      setEmergencyNumbers(numbers);
      setUserCountry(numbers.country);
    });
  }, [findEmergencyHospitals]);

  const callEmergency = (phone) => {
    window.location.href = `tel:${phone}`;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content emergency-modal" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="emergency-header">
          <div className="emergency-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 11l3 3L22 4"></path>
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
            </svg>
          </div>
          <h2>Emergency Services</h2>
          {userCountry && <p className="emergency-country">{userCountry}</p>}
          <p className="emergency-subtitle">Finding nearest 24/7 hospitals...</p>
        </div>

        {loading && (
          <Spinner label="Locating emergency hospitals near you..." />
        )}

        {error && (
          <Alert type="error">
            <p>{error}</p>
            {emergencyNumbers && (
              <div className="emergency-numbers-list">
                <p className="urgent-text">Call Emergency Services:</p>
                {formatEmergencyInfo(emergencyNumbers).map((item, idx) => (
                  <a key={idx} href={`tel:${item.number}`} className="emergency-number-card">
                    <span className="label">{item.label}</span>
                    <span className="number">{item.number}</span>
                  </a>
                ))}
              </div>
            )}
          </Alert>
        )}

        {!loading && !error && emergencyHospitals.length === 0 && (
          <div className="no-emergency">
            <p>No emergency hospitals found within 10km radius.</p>
            {emergencyNumbers && (
              <div className="emergency-numbers-list">
                <p className="urgent-text">Call Emergency Services:</p>
                {formatEmergencyInfo(emergencyNumbers).map((item, idx) => (
                  <a key={idx} href={`tel:${item.number}`} className="emergency-number-card">
                    <span className="label">{item.label}</span>
                    <span className="number">{item.number}</span>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}

        {!loading && emergencyHospitals.length > 0 && (
          <div className="emergency-list">
            {emergencyNumbers && (
              <div className="emergency-actions">
                <a href={`tel:${emergencyNumbers.primary}`} className="btn btn-danger btn-large">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"></path>
                  </svg>
                  Call {emergencyNumbers.primary} ({emergencyNumbers.label})
                </a>
              </div>
            )}

            <h3>Nearest Emergency Hospitals ({emergencyHospitals.length})</h3>
            
            {emergencyHospitals.slice(0, 5).map((hospital, index) => (
              <div key={hospital.id || index} className="emergency-hospital-card">
                <div className="emergency-rank">{index + 1}</div>
                <div className="emergency-info">
                  <h4>{hospital.name}</h4>
                  <p className="address">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {hospital.address}
                  </p>
                  {hospital.distance && (
                    <p className="distance">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                        <polyline points="12 5 19 12 12 19"></polyline>
                      </svg>
                      {hospital.distance.toFixed(2)} km away
                    </p>
                  )}
                  {hospital.phone && (
                    <p className="phone">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"></path>
                      </svg>
                      {hospital.phone}
                    </p>
                  )}
                  <div className="emergency-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    24/7 Emergency Available
                  </div>
                </div>
                <div className="emergency-actions-inline">
                  {hospital.phone && (
                    <button 
                      className="btn btn-primary"
                      onClick={() => callEmergency(hospital.phone)}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"></path>
                      </svg>
                      Call Now
                    </button>
                  )}
                  <button 
                    className="btn"
                    onClick={() => {
                      window.open(
                        `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`,
                        '_blank'
                      );
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polygon points="3 11 22 2 13 21 11 13 3 11"></polygon>
                    </svg>
                    Get Directions
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default EmergencyFinder;
