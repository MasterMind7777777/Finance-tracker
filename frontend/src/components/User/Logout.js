import { useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';
import AuthContext from '../../context/AuthContext';
import { logMessage } from '../../api/loging';

const Logout = () => {
  const navigate = useNavigate();
  const { setUser } = useContext(AuthContext);

  useEffect(() => {
    logMessage('info', 'Logout initiated.', 'Logout');
    authService.logout();
    logMessage('info', 'User logged out successfully.', 'Logout'); // Log successful logout

    setUser(null);
    navigate('/login');
  }, [navigate]);

  return null;
};

export default Logout;
