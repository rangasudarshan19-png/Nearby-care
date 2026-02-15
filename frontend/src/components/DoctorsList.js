import React, { useState, useEffect } from 'react';
import { API_URL } from '../config';
import AppointmentBooking from './AppointmentBooking';

function DoctorsList() {
  const [doctors, setDoctors] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [showBooking, setShowBooking] = useState(false);

  useEffect(() => {
    fetchSpecialties();
    fetchDoctors();
  }, []);

  useEffect(() => {
    fetchDoctors();
  }, [selectedSpecialty]);

  const fetchSpecialties = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/api/specialties`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSpecialties(data.specialties || []);
      }
    } catch (error) {
      console.error('Error fetching specialties:', error);
    }
  };

  const fetchDoctors = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    let url = `${API_URL}/api/doctors`;
    if (selectedSpecialty) {
      url += `?specialty=${encodeURIComponent(selectedSpecialty)}`;
    }

    try {
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setDoctors(data.doctors || []);
      } else {
        setError('Failed to load doctors');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleBookAppointment = (doctor) => {
    setSelectedDoctor(doctor);
    setShowBooking(true);
  };

  const handleBookingSuccess = () => {
    fetchDoctors(); // Refresh list
  };

  if (loading) {
    return <div className="loading">Loading doctors...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="doctors-list-container">
      <div className="doctors-header">
        <h2>Find a Doctor</h2>
        <div className="specialty-filter">
          <label htmlFor="specialty">Filter by Specialty:</label>
          <select 
            id="specialty"
            value={selectedSpecialty} 
            onChange={(e) => setSelectedSpecialty(e.target.value)}
          >
            <option value="">All Specialties</option>
            {specialties.map(specialty => (
              <option key={specialty} value={specialty}>
                {specialty}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="doctors-count">
        Found {doctors.length} doctor{doctors.length !== 1 ? 's' : ''}
        {selectedSpecialty && ` in ${selectedSpecialty}`}
      </div>

      {doctors.length === 0 ? (
        <div className="no-doctors">
          <p>No doctors found.</p>
        </div>
      ) : (
        <div className="doctors-grid">
          {doctors.map(doctor => (
            <div key={doctor.id} className="doctor-card-detailed">
              <div className="doctor-card-header">
                <div className="doctor-avatar">
                  {doctor.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="doctor-info">
                  <h3>{doctor.name}</h3>
                  <span className="specialty-badge">{doctor.specialty}</span>
                </div>
              </div>

              <div className="doctor-card-body">
                <p className="qualifications">
                  <strong>Qualifications:</strong> {doctor.qualifications || 'N/A'}
                </p>
                <p className="experience">
                  <strong>Experience:</strong> {doctor.experience_years} years
                </p>
                <p className="hospital">
                  <strong>Hospital:</strong> {doctor.hospital_name}
                </p>
                <p className="fee">
                  <strong>Consultation Fee:</strong> ₹{doctor.consultation_fee}
                </p>
                {doctor.rating > 0 && (
                  <p className="rating">
                    <strong>Rating:</strong> <svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1" style={{verticalAlign:'middle'}}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg> {doctor.rating}/5.0
                  </p>
                )}
                {doctor.bio && (
                  <p className="bio">{doctor.bio}</p>
                )}
                {doctor.available_days && doctor.available_days.length > 0 && (
                  <p className="availability">
                    <strong>Available:</strong> {doctor.available_days.join(', ')}
                  </p>
                )}
                {doctor.available_hours && (
                  <p className="hours">
                    <strong>Hours:</strong> {doctor.available_hours}
                  </p>
                )}
              </div>

              <div className="doctor-card-footer">
                <button 
                  className="btn btn-primary"
                  onClick={() => handleBookAppointment(doctor)}
                >
                  Book Appointment
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showBooking && selectedDoctor && (
        <AppointmentBooking
          doctor={selectedDoctor}
          onClose={() => {
            setShowBooking(false);
            setSelectedDoctor(null);
          }}
          onSuccess={handleBookingSuccess}
        />
      )}
    </div>
  );
}

export default DoctorsList;
