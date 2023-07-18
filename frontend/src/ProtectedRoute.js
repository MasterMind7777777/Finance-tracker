import React from 'react';
import { Route, Navigate } from 'react-router-dom';
import AuthService from './services/authService';

const ProtectedRoute = ({ children }) => {
  const currentUser = AuthService.getCurrentUser();
  return currentUser ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
