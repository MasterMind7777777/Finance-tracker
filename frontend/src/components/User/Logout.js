import React, { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import AuthContext from '../../context/AuthContext';

const Logout = () => {
  const navigate = useNavigate();
  const { setUser } = useContext(AuthContext);

  useEffect(() => {
    authService.logout();
    setUser(null);
    navigate('/login');
  }, [navigate]);

  return null;
};

export default Logout;
