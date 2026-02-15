import React, { useState, useEffect } from 'react';
import { API_URL } from '../config';

function AppointmentBooking({ doctor, onClose, onSuccess }) {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [notes, setNotes] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedDate]);

  const fetchAvailableSlots = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(
        `${API_URL}/api/doctors/${doctor.id}/available-slots?date=${selectedDate}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data.slots || []);
      }
    } catch (error) {
      console.error('Error fetching slots:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_URL}/api/appointments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          doctor_id: doctor.id,
          appointment_date: selectedDate,
          appointment_time: selectedTime,
          symptoms,
          notes
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          onSuccess && onSuccess();
          onClose();
        }, 2000);
      } else {
        setError(data.error || 'Failed to book appointment');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30); // 30 days ahead
    return maxDate.toISOString().split('T')[0];
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content appointment-booking" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <h2>Book Appointment</h2>
        
        <div className="doctor-info-summary">
          <h3>{doctor.name}</h3>
          <p className="specialty">{doctor.specialty}</p>
          <p className="hospital">{doctor.hospital_name}</p>
          <p className="fee">Consultation Fee: ₹{doctor.consultation_fee}</p>
        </div>

        {success ? (
          <div className="success-message">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <h3>Appointment Booked Successfully!</h3>
            <p>A confirmation email has been sent to you.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="appointment-form">
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label htmlFor="date">Select Date *</label>
              <input
                type="date"
                id="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={getMinDate()}
                max={getMaxDate()}
                required
              />
              {doctor.available_days && doctor.available_days.length > 0 && (
                <small className="help-text">
                  Available on: {doctor.available_days.join(', ')}
                </small>
              )}
            </div>

            {selectedDate && (
              <div className="form-group">
                <label htmlFor="time">Select Time Slot *</label>
                {availableSlots.length === 0 ? (
                  <p className="no-slots">No available slots for this date</p>
                ) : (
                  <div className="time-slots">
                    {availableSlots.map(slot => (
                      <button
                        key={slot}
                        type="button"
                        className={`time-slot ${selectedTime === slot ? 'selected' : ''}`}
                        onClick={() => setSelectedTime(slot)}
                      >
                        {slot}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="symptoms">Symptoms / Reason for Visit</label>
              <textarea
                id="symptoms"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                rows="3"
                placeholder="Describe your symptoms or reason for consultation..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="notes">Additional Notes (Optional)</label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows="2"
                placeholder="Any additional information..."
              />
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading || !selectedDate || !selectedTime}
              >
                {loading ? 'Booking...' : 'Confirm Booking'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default AppointmentBooking;
