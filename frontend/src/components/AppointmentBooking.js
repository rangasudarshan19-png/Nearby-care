import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { apiGet, apiPost } from '../utils/apiClient';
import { Alert, Spinner } from './ui';

function AppointmentBooking({ doctor, onClose, onSuccess }) {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [notes, setNotes] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [slotMessage, setSlotMessage] = useState('');
  const [success, setSuccess] = useState(false);

  const availableDays = useMemo(() => doctor.available_days || [], [doctor.available_days]);

  const getDateDay = useCallback((dateValue) => {
    if (!dateValue) return '';
    return new Date(`${dateValue}T00:00:00`).toLocaleDateString('en-US', { weekday: 'short' });
  }, []);

  const isDateAvailable = useCallback((dateValue) => {
    if (!dateValue || availableDays.length === 0) return true;
    const selectedDay = getDateDay(dateValue);
    return availableDays.some(day => day.slice(0, 3).toLowerCase() === selectedDay.toLowerCase());
  }, [availableDays, getDateDay]);

  const selectedDateUnavailable = selectedDate && !isDateAvailable(selectedDate);

  const fetchAvailableSlots = useCallback(async () => {
    if (!isDateAvailable(selectedDate)) {
      setAvailableSlots([]);
      setSelectedTime('');
      setSlotMessage(`Doctor is not available on ${new Date(`${selectedDate}T00:00:00`).toLocaleDateString('en-US', { weekday: 'long' })}`);
      return;
    }

    try {
      const data = await apiGet(`/api/doctors/${doctor.id}/available-slots?date=${selectedDate}`);
      setAvailableSlots(data.slots || []);
      setSlotMessage(data.message || '');
      if (!(data.slots || []).includes(selectedTime)) {
        setSelectedTime('');
      }
    } catch (error) {
      setAvailableSlots([]);
      setSlotMessage(error.message || 'Failed to load available slots.');
    }
  }, [doctor.id, isDateAvailable, selectedDate, selectedTime]);

  useEffect(() => {
    if (selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedDate, fetchAvailableSlots]);

  const handleDateChange = (dateValue) => {
    setSelectedDate(dateValue);
    setSelectedTime('');
    setAvailableSlots([]);
    setSlotMessage('');
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!isDateAvailable(selectedDate)) {
      setError(`Doctor is not available on ${new Date(`${selectedDate}T00:00:00`).toLocaleDateString('en-US', { weekday: 'long' })}`);
      setLoading(false);
      return;
    }

    try {
      await apiPost('/api/appointments', {
        doctor_id: doctor.id,
        appointment_date: selectedDate,
        appointment_time: selectedTime,
        symptoms,
        notes
      });
      setSuccess(true);
      setTimeout(() => {
        onSuccess && onSuccess();
        onClose();
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to book appointment. Please try again.');
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
            <Alert type="error">{error}</Alert>

            <div className="form-group">
              <label htmlFor="date">Select Date *</label>
              <input
                type="date"
                id="date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
                min={getMinDate()}
                max={getMaxDate()}
                required
              />
              {doctor.available_days && doctor.available_days.length > 0 && (
                <small className="help-text">
                  Available on: {doctor.available_days.join(', ')}
                </small>
              )}
              {selectedDateUnavailable && (
                <small className="error-text">
                  Doctor is not available on {new Date(`${selectedDate}T00:00:00`).toLocaleDateString('en-US', { weekday: 'long' })}
                </small>
              )}
            </div>

            {selectedDate && (
              <div className="form-group">
                <label htmlFor="time">Select Time Slot *</label>
                {availableSlots.length === 0 ? (
                  <p className="no-slots">{slotMessage || 'No available slots for this date'}</p>
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
                disabled={loading || !selectedDate || !selectedTime || selectedDateUnavailable}
              >
                {loading ? <Spinner label="Booking..." inline /> : 'Confirm Booking'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default AppointmentBooking;
