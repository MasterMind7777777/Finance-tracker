import React, { useState, useEffect } from 'react';
import Routes from './Router';
import AuthContext from './context/AuthContext';
import authService from './services/authService';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <div className="App">
        <ToastContainer />
        <Routes />
      </div>
    </AuthContext.Provider>
  );
};

export default App;
