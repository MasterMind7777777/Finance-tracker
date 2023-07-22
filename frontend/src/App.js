import React, { useState, useEffect } from 'react';
import Routes from './Router';
import AuthContext from './context/AuthContext';
import authService from './services/authService';

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    setUser(currentUser);
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <div className="App">
        <Routes />
      </div>
    </AuthContext.Provider>
  );
};

export default App;
