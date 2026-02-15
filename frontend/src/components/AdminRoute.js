import React from 'react';
import { Navigate } from 'react-router-dom';

// Admin Route Guard
export const AdminRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  if (!token || !user.role || user.role !== 'admin') {
    return <Navigate to="/login" />;
  }
  
  return children;
};
