import React, { useState, useEffect } from 'react';
import { API_URL } from '../config';

function MyAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, scheduled, cancelled, completed

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_URL}/api/appointments`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAppointments(data.appointments || []);
      } else {
        setError('Failed to load appointments');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) {
      return;
    }

    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_URL}/api/appointments/${appointmentId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchAppointments(); // Refresh list
      } else {
        alert('Failed to cancel appointment');
      }
    } catch (err) {
      alert('Network error');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return '#10b981'; // green
      case 'cancelled':
        return '#ef4444'; // red
      case 'completed':
        return '#6b7280'; // gray
      default:
        return '#0ea5e9'; // blue
    }
  };

  const filteredAppointments = appointments.filter(apt => {
    if (filter === 'all') return true;
    return apt.status === filter;
  });

  const upcomingCount = appointments.filter(a => a.status === 'scheduled').length;
  const pastCount = appointments.filter(a => a.status === 'completed').length;
  const cancelledCount = appointments.filter(a => a.status === 'cancelled').length;

  if (loading) {
    return <div className="loading">Loading appointments...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="my-appointments">
      <div className="appointments-header">
        <h2>My Appointments</h2>
        <div className="appointments-stats">
          <span className="stat">
            <strong>{upcomingCount}</strong> Upcoming
          </span>
          <span className="stat">
            <strong>{pastCount}</strong> Completed
          </span>
          <span className="stat">
            <strong>{cancelledCount}</strong> Cancelled
          </span>
        </div>
      </div>

      <div className="filter-buttons">
        <button 
          className={filter === 'all' ? 'active' : ''} 
          onClick={() => setFilter('all')}
        >
          All ({appointments.length})
        </button>
        <button 
          className={filter === 'scheduled' ? 'active' : ''} 
          onClick={() => setFilter('scheduled')}
        >
          Upcoming ({upcomingCount})
        </button>
        <button 
          className={filter === 'completed' ? 'active' : ''} 
          onClick={() => setFilter('completed')}
        >
          Completed ({pastCount})
        </button>
        <button 
          className={filter === 'cancelled' ? 'active' : ''} 
          onClick={() => setFilter('cancelled')}
        >
          Cancelled ({cancelledCount})
        </button>
      </div>

      {filteredAppointments.length === 0 ? (
        <div className="no-appointments">
          <p>No {filter !== 'all' ? filter : ''} appointments found.</p>
          <p>Book your first appointment from the search results!</p>
        </div>
      ) : (
        <div className="appointments-list">
          {filteredAppointments.map(appointment => (
            <div key={appointment.id} className="appointment-card">
              <div className="appointment-header">
                <div>
                  <h3>{appointment.doctor_name}</h3>
                  <span className="specialty">{appointment.doctor_specialty}</span>
                </div>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(appointment.status) }}
                >
                  {appointment.status}
                </span>
              </div>

              <div className="appointment-details">
                <p>
                  <strong>Hospital:</strong> {appointment.hospital_name}
                </p>
                <p>
                  <strong>Date:</strong> {formatDate(appointment.appointment_date)}
                </p>
                <p>
                  <strong>Time:</strong> {appointment.appointment_time}
                </p>
                {appointment.symptoms && (
                  <p>
                    <strong>Symptoms:</strong> {appointment.symptoms}
                  </p>
                )}
                {appointment.notes && (
                  <p>
                    <strong>Notes:</strong> {appointment.notes}
                  </p>
                )}
              </div>

              <div className="appointment-actions">
                {appointment.status === 'scheduled' && (
                  <>
                    <button 
                      className="btn btn-danger btn-small"
                      onClick={() => handleCancel(appointment.id)}
                    >
                      Cancel Appointment
                    </button>
                  </>
                )}
                <small className="booked-date">
                  Booked on {new Date(appointment.created_at).toLocaleDateString()}
                </small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyAppointments;
