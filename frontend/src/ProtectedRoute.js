import React from 'react';
import PropTypes from 'prop-types'; // Import PropTypes
import { Navigate } from 'react-router-dom';
import AuthService from './services/authService';

const ProtectedRoute = ({ children }) => {
  const currentUser = AuthService.getCurrentUser();
  return currentUser ? children : <Navigate to="/login" replace />;
};

// Define PropTypes for the component
ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired, // If children can be null/undefined, remove isRequired.
};

export default ProtectedRoute;
