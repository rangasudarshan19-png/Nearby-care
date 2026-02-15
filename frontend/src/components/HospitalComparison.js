import React, { useState } from 'react';

function HospitalComparison({ hospitals, onClose }) {
  const [selectedHospitals, setSelectedHospitals] = useState([]);

  const toggleHospital = (hospital) => {
    if (selectedHospitals.find(h => h.id === hospital.id)) {
      setSelectedHospitals(selectedHospitals.filter(h => h.id !== hospital.id));
    } else if (selectedHospitals.length < 3) {
      setSelectedHospitals([...selectedHospitals, hospital]);
    } else {
      alert('You can only compare up to 3 hospitals at a time');
    }
  };

  const isSelected = (hospital) => {
    return selectedHospitals.find(h => h.id === hospital.id);
  };

  const ComparisonTable = () => {
    if (selectedHospitals.length < 2) {
      return (
        <div className="comparison-placeholder">
          <p>Select at least 2 hospitals to compare</p>
          <p>Selected: {selectedHospitals.length}/3</p>
        </div>
      );
    }

    return (
      <div className="comparison-table-wrapper">
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Feature</th>
              {selectedHospitals.map(h => (
                <th key={h.id}>
                  {h.name}
                  <button 
                    className="remove-btn"
                    onClick={() => toggleHospital(h)}
                    title="Remove from comparison"
                  >
                    ×
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="feature-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                Address
              </td>
              {selectedHospitals.map(h => (
                <td key={h.id}>{h.address || 'N/A'}</td>
              ))}
            </tr>
            <tr>
              <td className="feature-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                Distance
              </td>
              {selectedHospitals.map(h => (
                <td key={h.id}>
                  {h.distance ? `${h.distance.toFixed(2)} km` : 'N/A'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="feature-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Rating
              </td>
              {selectedHospitals.map(h => (
                <td key={h.id}>
                  {h.rating ? `${h.rating}/5` : 'No ratings'}
                </td>
              ))}
            </tr>
            <tr>
              <td className="feature-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                Type
              </td>
              {selectedHospitals.map(h => (
                <td key={h.id}>{h.type || 'General'}</td>
              ))}
            </tr>
            <tr>
              <td className="feature-label">Actions</td>
              {selectedHospitals.map(h => (
                <td key={h.id}>
                  <button 
                    className="btn-directions"
                    onClick={() => {
                      window.open(
                        `https://www.google.com/maps/dir/?api=1&destination=${h.latitude},${h.longitude}`,
                        '_blank'
                      );
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                    Directions
                  </button>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content comparison-modal" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <h2>Compare Hospitals</h2>
        
        <div className="comparison-selector">
          <h3>Select hospitals to compare ({selectedHospitals.length}/3)</h3>
          <div className="hospital-selector-list">
            {hospitals.map(hospital => (
              <div 
                key={hospital.id}
                className={`hospital-selector-item ${isSelected(hospital) ? 'selected' : ''}`}
                onClick={() => toggleHospital(hospital)}
              >
                <input
                  type="checkbox"
                  checked={isSelected(hospital)}
                  onChange={() => {}}
                />
                <span className="hospital-name">{hospital.name}</span>
                {hospital.distance && (
                  <span className="hospital-distance">
                    {hospital.distance.toFixed(2)} km
                  </span>
                )}
                {hospital.ai_score > 0 && (
                  <span className="hospital-ai-score">
                    {(hospital.ai_score * 100).toFixed(0)}% match
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <ComparisonTable />

        {selectedHospitals.length >= 2 && (
          <div className="comparison-actions">
            <button 
              className="btn"
              onClick={() => setSelectedHospitals([])}
            >
              Clear Selection
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default HospitalComparison;
