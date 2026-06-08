import React, { useState } from 'react';

function SearchForm({ onSearch, loading }) {
  const [location, setLocation] = useState('');
  // Store radius in kilometers to match backend expectation
  const [radius, setRadius] = useState('5');
  const [sortBy, setSortBy] = useState('nearby');
  const [coords, setCoords] = useState(null);
  const [geoError, setGeoError] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hospitalType, setHospitalType] = useState('');
  const [emergencyOnly, setEmergencyOnly] = useState(false);
  const [minRating, setMinRating] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [amenities, setAmenities] = useState([]);
  const [ownership, setOwnership] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { radius: parseFloat(radius), sortBy };
    if (hospitalType) payload.hospitalType = hospitalType;
    if (emergencyOnly) payload.emergencyOnly = true;
    if (minRating) payload.minRating = parseFloat(minRating);
    if (specialty) payload.specialty = specialty;
    if (amenities.length > 0) payload.amenities = amenities;
    if (ownership) payload.ownership = ownership;
    if (coords) {
      payload.lat = coords.lat;
      payload.lon = coords.lon;
      payload.location = location || 'My location';
    } else if (location.trim()) {
      payload.location = location.trim();
    }
    if (!payload.location) return; // require either coords or location
    onSearch(payload);
  };

  const useMyLocation = () => {
    setGeoError(null);
    if (!navigator.geolocation) {
      setGeoError('Geolocation not supported');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setCoords({ lat: latitude, lon: longitude });
        if (!location) setLocation('My location');
      },
      (err) => {
        setGeoError(err.message || 'Failed to get location');
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
    );
  };

  return (
    <div className="search-section">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-row">
          <div className="form-group full-width">
            <label htmlFor="location">Location / Area Name</label>
            <div className="input-with-button">
              <input
                type="text"
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., New York, Manhattan, or 10001"
                required={!coords}
              />
              <button type="button" className="btn-location" onClick={useMyLocation} title="Use my current location" aria-label="Use my current location">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="10" r="3"></circle>
                  <path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"></path>
                </svg>
              </button>
            </div>
            {coords && <div className="hint">Using GPS: {coords.lat.toFixed(4)}, {coords.lon.toFixed(4)}</div>}
            {geoError && <div className="error">{geoError}</div>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="radius">Search Radius</label>
            <select
              id="radius"
              value={radius}
              onChange={(e) => setRadius(e.target.value)}
            >
              <option value="1">1 km</option>
              <option value="2">2 km</option>
              <option value="5">5 km</option>
              <option value="10">10 km</option>
              <option value="20">20 km</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="sortBy">Sort By</label>
            <select
              id="sortBy"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="nearby">Nearby (Distance)</option>
              <option value="rating">Rating (High to Low)</option>
              <option value="name">Hospital Name (A-Z)</option>
            </select>
          </div>
        </div>

        <div className="advanced-filters-toggle">
          <button 
            type="button" 
            className="btn-link"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
        </div>

        {showAdvanced && (
          <div className="advanced-filters">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="hospitalType">Hospital Type</label>
                <select
                  id="hospitalType"
                  value={hospitalType}
                  onChange={(e) => setHospitalType(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="hospital">Hospital</option>
                  <option value="clinic">Clinic</option>
                  <option value="doctors">Medical Center</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="minRating">Minimum Rating</label>
                <select
                  id="minRating"
                  value={minRating}
                  onChange={(e) => setMinRating(e.target.value)}
                >
                  <option value="">Any Rating</option>
                  <option value="3">3+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                  <option value="4">4+ Stars</option>
                  <option value="4.5">4.5+ Stars</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="specialty">Medical Specialty</label>
                <select
                  id="specialty"
                  value={specialty}
                  onChange={(e) => setSpecialty(e.target.value)}
                >
                  <option value="">All Specialties</option>
                  <option value="cardiac">Cardiac/Cardiology</option>
                  <option value="orthopedic">Orthopedics</option>
                  <option value="dental">Dental</option>
                  <option value="pediatric">Pediatrics</option>
                  <option value="maternity">Maternity/Obstetrics</option>
                  <option value="neurology">Neurology</option>
                  <option value="oncology">Oncology/Cancer</option>
                  <option value="ophthalmology">Ophthalmology/Eye</option>
                  <option value="ent">ENT</option>
                  <option value="dermatology">Dermatology</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="ownership">Hospital Ownership</label>
                <select
                  id="ownership"
                  value={ownership}
                  onChange={(e) => setOwnership(e.target.value)}
                >
                  <option value="">All (Government & Private)</option>
                  <option value="government">Government</option>
                  <option value="private">Private</option>
                  <option value="multispecialty">Multispecialty</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Required Amenities</label>
                <div className="checkbox-grid">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      value="icu"
                      checked={amenities.includes('icu')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setAmenities([...amenities, 'icu']);
                        } else {
                          setAmenities(amenities.filter(a => a !== 'icu'));
                        }
                      }}
                    />
                    <span>ICU</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      value="lab"
                      checked={amenities.includes('lab')}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setAmenities([...amenities, 'lab']);
                        } else {
                          setAmenities(amenities.filter(a => a !== 'lab'));
                        }
                      }}
                    />
                    <span>Lab/Diagnostics</span>
                  </label>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={emergencyOnly}
                    onChange={(e) => setEmergencyOnly(e.target.checked)}
                  />
                  <span>Emergency Services Only (24/7)</span>
                </label>
              </div>
            </div>
          </div>
        )}

        <button type="submit" className="btn btn-search-submit" disabled={loading}>
          {loading ? (
            <>
              <div className="spinner" style={{width: 18, height: 18, borderWidth: 2, margin: 0}}></div>
              Searching...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              Search Hospitals
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default SearchForm;
