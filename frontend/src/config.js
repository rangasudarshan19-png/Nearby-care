// Centralized API base URL for frontend
// In development, point directly to backend server
// In production, set REACT_APP_API_URL environment variable to your backend URL
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
