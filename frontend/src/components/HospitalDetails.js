import React, { useState, useEffect } from 'react';
import { API_URL } from '../config';
import Reviews from './Reviews';

function HospitalDetails({ hospital, onClose, onBookAppointment }) {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    if (hospital && activeTab === 'doctors') {
      fetchDoctors();
    }
  }, [hospital, activeTab]);

  const fetchDoctors = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/doctors?hospital_id=${hospital.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setDoctors(data.doctors);
      }
    } catch (error) {
      console.error('Error fetching doctors:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!hospital) return null;

  const openInMaps = () => {
    const url = `https://www.google.com/maps/search/?api=1&query=${hospital.latitude},${hospital.longitude}`;
    window.open(url, '_blank');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content hospital-details" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="hospital-header">
          <h2>{hospital.name}</h2>
          {hospital.ai_score && (
            <span className="ai-badge">
              {Math.round(hospital.ai_score * 100)}% AI Match
            </span>
          )}
        </div>

        <div className="details-tabs">
          <button 
            className={activeTab === 'info' ? 'active' : ''} 
            onClick={() => setActiveTab('info')}
          >
            Information
          </button>
          <button 
            className={activeTab === 'doctors' ? 'active' : ''} 
            onClick={() => setActiveTab('doctors')}
          >
            Doctors ({doctors.length})
          </button>
          <button 
            className={activeTab === 'reviews' ? 'active' : ''} 
            onClick={() => setActiveTab('reviews')}
          >
            Reviews
          </button>
        </div>

        <div className="details-content">
          {activeTab === 'info' && (
            <div className="info-section">
              <div className="info-item">
                <strong>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                  </svg>
                  Address:
                </strong>
                <p>{hospital.address || 'Address not available'}</p>
              </div>

              {hospital.phone && (
                <div className="info-item">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"></path>
                    </svg>
                    Phone:
                  </strong>
                  <p>{hospital.phone}</p>
                </div>
              )}

              {hospital.website && (
                <div className="info-item">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="2" y1="12" x2="22" y2="12"></line>
                      <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"></path>
                    </svg>
                    Website:
                  </strong>
                  <p>
                    <a href={hospital.website} target="_blank" rel="noopener noreferrer">
                      Visit Website
                    </a>
                  </p>
                </div>
              )}

              {hospital.opening_hours && (
                <div className="info-item">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    Hours:
                  </strong>
                  <p>{hospital.opening_hours}</p>
                </div>
              )}

              {hospital.emergency && (
                <div className="info-item">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    Emergency Services:
                  </strong>
                  <p>{hospital.emergency === 'yes' ? 'Available 24/7' : 'Not available'}</p>
                </div>
              )}

              {hospital.beds && (
                <div className="info-item">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                      <path d="M7 11V7a2 2 0 012-2h2"></path>
                    </svg>
                    Beds:
                  </strong>
                  <p>{hospital.beds}</p>
                </div>
              )}

              {hospital.ai_reason && (
                <div className="info-item ai-reason">
                  <strong>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"></path>
                      <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    AI Recommendation:
                  </strong>
                  <p>{hospital.ai_reason}</p>
                </div>
              )}

              <div className="action-buttons">
                <button className="btn" onClick={openInMaps}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
                    <line x1="8" y1="2" x2="8" y2="18"></line>
                    <line x1="16" y1="6" x2="16" y2="22"></line>
                  </svg>
                  Get Directions
                </button>
                <button className="btn btn-primary" onClick={() => setActiveTab('doctors')}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  View Doctors
                </button>
              </div>
            </div>
          )}

          {activeTab === 'doctors' && (
            <div className="doctors-section">
              {loading ? (
                <p>Loading doctors...</p>
              ) : doctors.length === 0 ? (
                <p>No doctors available for this hospital yet.</p>
              ) : (
                <div className="doctors-list">
                  {doctors.map(doctor => (
                    <div key={doctor.id} className="doctor-card">
                      <div className="doctor-header">
                        <h3>{doctor.name}</h3>
                        <span className="specialty-badge">{doctor.specialty}</span>
                      </div>
                      <p className="qualifications">{doctor.qualifications}</p>
                      <p className="experience">
                        {doctor.experience_years} years experience
                      </p>
                      <p className="fee">Consultation: ₹{doctor.consultation_fee}</p>
                      {doctor.rating > 0 && (
                        <p className="rating">Rating: {doctor.rating}/5.0</p>
                      )}
                      {doctor.bio && <p className="bio">{doctor.bio}</p>}
                      {doctor.available_days && doctor.available_days.length > 0 && (
                        <p className="availability">
                          Available: {doctor.available_days.join(', ')}
                        </p>
                      )}
                      <button 
                        className="btn btn-small"
                        onClick={() => onBookAppointment && onBookAppointment(doctor)}
                      >
                        Book Appointment
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'reviews' && (
            <Reviews hospital={hospital} />
          )}
        </div>
      </div>
    </div>
  );
}

export default HospitalDetails;
