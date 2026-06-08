import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyOTP from './pages/VerifyOTP';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import './index.css';
import './styles/Polish.css';
import { apiGet } from './utils/apiClient';
import { Spinner } from './components/ui';
import {
  clearAuthSession,
  getAuthToken,
  setAuthSession,
  subscribeToLogout,
  updateStoredUser
} from './utils/authStorage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
    return subscribeToLogout(() => {
      setUser(null);
      setIsAuthenticated(false);
    });
  }, []);

  const checkAuth = async () => {
    const token = getAuthToken();
    if (token) {
      try {
        const data = await apiGet('/api/auth/me');
        setUser(data.user);
        updateStoredUser(data.user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        clearAuthSession({ broadcast: true });
      }
    }
    setLoading(false);
  };

  const handleLogin = (token, userData) => {
    setAuthSession(token, userData);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    clearAuthSession({ broadcast: true });
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return <Spinner />;
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route 
          path="/login" 
          element={
            isAuthenticated ? 
            <Navigate to={user?.role === 'admin' || user?.is_admin ? '/admin' : '/dashboard'} /> : 
            <Login onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/signup" 
          element={
            isAuthenticated ? 
            <Navigate to="/dashboard" /> : 
            <Signup />
          } 
        />
        <Route path="/verify-otp" element={<VerifyOTP onLogin={handleLogin} />} />
        <Route 
          path="/forgot-password" 
          element={
            isAuthenticated ? 
            <Navigate to={user?.role === 'admin' || user?.is_admin ? '/admin' : '/dashboard'} /> : 
            <ForgotPassword />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isAuthenticated ? 
            (user?.role === 'admin' ? 
              <Navigate to="/admin" /> : 
              <Dashboard user={user} onLogout={handleLogout} />) : 
            <Navigate to="/login" />
          } 
        />
        <Route 
          path="/admin" 
          element={
            isAuthenticated && (user?.is_admin || user?.role === 'admin') ? 
            <AdminPanel user={user} onLogout={handleLogout} /> : 
            <Navigate to="/login" />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
