// Emergency numbers by country/region with geolocation detection

export const EMERGENCY_NUMBERS = {
  IN: {
    country: 'India',
    ambulance: '108',
    police: '112',
    fire: '101',
    women: '1091',
    child: '1098',
    primary: '108',
    secondary: '102',
    label: 'Ambulance / Medical Emergency'
  },
  US: {
    country: 'United States',
    emergency: '911',
    primary: '911',
    label: 'Emergency Services'
  },
  GB: {
    country: 'United Kingdom',
    emergency: '999',
    alternate: '112',
    primary: '999',
    label: 'Emergency Services'
  },
  CA: {
    country: 'Canada',
    emergency: '911',
    primary: '911',
    label: 'Emergency Services'
  },
  AU: {
    country: 'Australia',
    emergency: '000',
    alternate: '112',
    primary: '000',
    label: 'Emergency Services'
  },
  EU: {
    country: 'Europe (EU)',
    emergency: '112',
    primary: '112',
    label: 'Emergency Services'
  },
  DEFAULT: {
    country: 'International',
    emergency: '112',
    primary: '112',
    label: 'Emergency Services (International)'
  }
};

// Get emergency numbers based on user's location
export async function getEmergencyNumbersByLocation() {
  try {
    // Try to get country code from geolocation
    if (navigator.geolocation) {
      return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const { latitude, longitude } = position.coords;
            
            // Use reverse geocoding to get country
            try {
              const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=en`
              );
              const data = await response.json();
              const countryCode = data.address?.country_code?.toUpperCase();
              
              if (countryCode && EMERGENCY_NUMBERS[countryCode]) {
                resolve(EMERGENCY_NUMBERS[countryCode]);
              } else {
                resolve(EMERGENCY_NUMBERS.DEFAULT);
              }
            } catch (error) {
              console.error('Reverse geocoding failed:', error);
              resolve(EMERGENCY_NUMBERS.DEFAULT);
            }
          },
          (error) => {
            console.error('Geolocation error:', error);
            // Fallback to browser locale
            resolve(getEmergencyNumbersByLocale());
          },
          { timeout: 5000 }
        );
      });
    }
    
    // Fallback to browser locale
    return getEmergencyNumbersByLocale();
  } catch (error) {
    console.error('Error getting emergency numbers:', error);
    return EMERGENCY_NUMBERS.DEFAULT;
  }
}

// Fallback: Get emergency numbers based on browser locale
function getEmergencyNumbersByLocale() {
  const locale = navigator.language || navigator.userLanguage || 'en-US';
  const countryCode = locale.split('-')[1]?.toUpperCase();
  
  if (countryCode && EMERGENCY_NUMBERS[countryCode]) {
    return EMERGENCY_NUMBERS[countryCode];
  }
  
  // European countries default to 112
  const europeanCountries = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'PT', 'GR', 'SE', 'NO', 'DK', 'FI'];
  if (countryCode && europeanCountries.includes(countryCode)) {
    return EMERGENCY_NUMBERS.EU;
  }
  
  return EMERGENCY_NUMBERS.DEFAULT;
}

// Get formatted emergency display
export function formatEmergencyInfo(emergencyData) {
  const lines = [];
  
  if (emergencyData.ambulance) {
    lines.push({ label: 'Ambulance', number: emergencyData.ambulance });
  }
  if (emergencyData.police) {
    lines.push({ label: 'Police', number: emergencyData.police });
  }
  if (emergencyData.fire) {
    lines.push({ label: 'Fire', number: emergencyData.fire });
  }
  if (emergencyData.emergency) {
    lines.push({ label: emergencyData.label || 'Emergency', number: emergencyData.emergency });
  }
  
  return lines;
}
