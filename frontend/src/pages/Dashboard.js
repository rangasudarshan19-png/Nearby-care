import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchForm from '../components/SearchForm';
import HospitalsList from '../components/HospitalsList';
import HospitalDetails from '../components/HospitalDetails';
import HospitalComparison from '../components/HospitalComparison';
import EmergencyFinder from '../components/EmergencyFinder';
import MapView from '../components/MapView';
import Favorites from '../components/Favorites';
import SearchHistory from '../components/SearchHistory';
import SymptomAdvisor from '../components/SymptomAdvisor';
import DoctorsList from '../components/DoctorsList';
import MyAppointments from '../components/MyAppointments';
import AppointmentBooking from '../components/AppointmentBooking';
import UserProfile from '../components/UserProfile';
import '../styles/Dashboard.css';
import { apiPost } from '../utils/apiClient';
import { Alert } from '../components/ui';

function Dashboard({ user, onLogout }) {
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchLocation, setSearchLocation] = useState(null);
  const [activeTab, setActiveTab] = useState('search');
  const [message, setMessage] = useState(null);
  const [selectedHospital, setSelectedHospital] = useState(null);
  const [showHospitalDetails, setShowHospitalDetails] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const [showComparison, setShowComparison] = useState(false);
  const [showEmergency, setShowEmergency] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (searchData) => {
    setLoading(true);
    setError(null);
    setHospitals([]);

    try {
      const data = await apiPost('/api/search-hospitals-osm', searchData);
      // If AI scoring present, hospitals are already sorted
      setHospitals(data.hospitals || []);
      // Normalize backend coordinates (lat, lon -> lat, lng for Leaflet)
      if (data.coordinates) {
        setSearchLocation({
          lat: data.coordinates.lat,
          lng: data.coordinates.lon,
        });
      } else {
        setSearchLocation(null);
      }
      
      if ((data.hospitals || []).length === 0) {
        setMessage('No hospitals found in this area. Try a different location or increase the search radius.');
      } else {
        setMessage(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch hospitals');
    } finally {
      setLoading(false);
    }
  };

  const handleAddFavorite = async (hospital) => {
    try {
      await apiPost('/api/favorites', {
        hospital_name: hospital.name,
        hospital_address: hospital.address,
        place_id: hospital.id?.toString(),
        latitude: hospital.latitude,
        longitude: hospital.longitude,
      });
      setMessage('Hospital added to favorites!');
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setError(err.message || 'Failed to add to favorites');
    }
  };

  const handleViewDetails = (hospital) => {
    setSelectedHospital(hospital);
    setShowHospitalDetails(true);
  };

  const handleBookAppointment = (doctor) => {
    setSelectedDoctor(doctor);
    setShowBooking(true);
    setShowHospitalDetails(false);
  };

  const handleLogoutClick = () => {
    onLogout();
    navigate('/');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <h1>Nearby Care</h1>
          </div>
          <div className="user-info">
            <button 
              onClick={() => setShowEmergency(true)} 
              className="btn-emergency"
              title="Find nearest emergency hospital"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              Emergency
            </button>
            <span className="welcome-text">Welcome, {user?.username}!</span>
            <button onClick={handleLogoutClick} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-main">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="M21 21l-4.35-4.35"></path>
            </svg>
            Search Hospitals
          </button>
          <button 
            className={`tab ${activeTab === 'doctors' ? 'active' : ''}`}
            onClick={() => setActiveTab('doctors')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Find Doctors
          </button>
          <button 
            className={`tab ${activeTab === 'appointments' ? 'active' : ''}`}
            onClick={() => setActiveTab('appointments')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            My Appointments
          </button>
          <button 
            className={`tab ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorites')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"></path>
            </svg>
            Favorites
          </button>
          <button 
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"></path>
            </svg>
            Search History
          </button>
          <button 
            className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            My Profile
          </button>
          <button 
            className={`tab ${activeTab === 'advisor' ? 'active' : ''}`}
            onClick={() => setActiveTab('advisor')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3zM7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"></path>
            </svg>
            Symptom Advisor
          </button>
        </div>

        <Alert type="error">{error}</Alert>
        {message && <div className="success">{message}</div>}

        {activeTab === 'search' && (
          <>
            <SearchForm onSearch={handleSearch} loading={loading} />

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Searching for hospitals...</p>
              </div>
            )}

            {!loading && hospitals.length > 0 && (
              <>
                <div className="results-section">
                  <MapView 
                    hospitals={hospitals} 
                    center={searchLocation}
                  />
                  <HospitalsList 
                    hospitals={hospitals}
                    onAddFavorite={handleAddFavorite}
                    onViewDetails={handleViewDetails}
                  />
                </div>
                {hospitals.length >= 2 && (
                  <button 
                    className="btn btn-compare"
                    onClick={() => setShowComparison(true)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="20" x2="18" y2="10"></line>
                      <line x1="12" y1="20" x2="12" y2="4"></line>
                      <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                    Compare Hospitals ({hospitals.length} available)
                  </button>
                )}
              </>
            )}

            {!loading && hospitals.length === 0 && !message && (
              <div className="info">
                <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="1" style={{marginBottom: 16, opacity: 0.7}}>
                  <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                  <line x1="12" y1="8" x2="12" y2="10" stroke="#ef4444" strokeWidth="2"/>
                  <line x1="11" y1="9" x2="13" y2="9" stroke="#ef4444" strokeWidth="2"/>
                </svg>
                <h2>Find trusted care near you</h2>
                <p>Use your location or type a place, then add symptoms for smarter recommendations.</p>
              </div>
            )}

            {!loading && message && (
              <div className="info">
                <h2>{message}</h2>
              </div>
            )}
          </>
        )}

        {activeTab === 'doctors' && <DoctorsList />}
        {activeTab === 'appointments' && <MyAppointments />}
        {activeTab === 'favorites' && <Favorites />}
        {activeTab === 'history' && <SearchHistory />}
        {activeTab === 'profile' && <UserProfile />}
        {activeTab === 'advisor' && <SymptomAdvisor />}
      </div>

      {showHospitalDetails && selectedHospital && (
        <HospitalDetails
          hospital={selectedHospital}
          onClose={() => {
            setShowHospitalDetails(false);
            setSelectedHospital(null);
          }}
          onBookAppointment={handleBookAppointment}
        />
      )}

      {showBooking && selectedDoctor && (
        <AppointmentBooking
          doctor={selectedDoctor}
          onClose={() => {
            setShowBooking(false);
            setSelectedDoctor(null);
          }}
          onSuccess={() => {
            setMessage('Appointment booked successfully!');
            setTimeout(() => setMessage(null), 3000);
          }}
        />
      )}

      {showComparison && hospitals.length >= 2 && (
        <HospitalComparison
          hospitals={hospitals}
          onClose={() => setShowComparison(false)}
        />
      )}

      {showEmergency && (
        <EmergencyFinder 
          onClose={() => setShowEmergency(false)}
        />
      )}
    </div>
  );
}

export default Dashboard;
