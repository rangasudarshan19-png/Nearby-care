import React from 'react';
import { Navigate } from 'react-router-dom';
import { getAuthToken, getStoredUser } from '../utils/authStorage';

// Admin Route Guard
export const AdminRoute = ({ children }) => {
  const token = getAuthToken();
  const user = getStoredUser() || {};
  
  if (!token || !user.role || user.role !== 'admin') {
    return <Navigate to="/login" />;
  }
  
  return children;
};
