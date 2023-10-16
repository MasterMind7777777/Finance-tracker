import React, { useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../../context/AuthContext';
import Dropdown from './Dropdown';
import '../../styles/Common/Navbar.css';
import { logMessage } from '../../api/loging'; // Importing logMessage function

const Navbar = () => {
  const { user } = useContext(AuthContext);

  // Log when the component mounts and unmounts
  useEffect(() => {
    logMessage('info', 'Navbar component mounted', 'Navbar');

    return () => {
      logMessage('info', 'Navbar component unmounted', 'Navbar');
    };
  }, []);

  // Log when the user's authentication status changes
  useEffect(() => {
    if (user) {
      logMessage('info', 'User is authenticated', 'Navbar');
    } else {
      logMessage('info', 'User is not authenticated', 'Navbar');
    }
  }, [user]);

  return (
    <nav className="navbar">
      <ul className="navbar-list">
        <li className="navbar-item">
          <Dropdown route="/" title="Home"></Dropdown>
        </li>
        <li className="navbar-item">
          <Dropdown route="/friends" title="Friends">
            {/* Add more links here */}
          </Dropdown>
        </li>
        <li className="navbar-item">
          <Dropdown route="/transactions" title="Transactions">
            <Link to="/transactions/bulk-upload">Import transactions</Link>
            <Link to="transactions/recommendations">
              Recommended Transactions
            </Link>
            {/* Add more links here */}
          </Dropdown>
        </li>
        <li className="navbar-item">
          <Dropdown route="/budgets" title="Budgets">
            {/* Add more links here */}
          </Dropdown>
        </li>
        <li className="navbar-item">
          <Dropdown route="/categories" title="Categories">
            {/* Add more links here */}
          </Dropdown>
        </li>
        {user ? (
          <li className="navbar-item">
            <Link to="/logout" className="navbar-link">
              Logout
            </Link>
          </li>
        ) : (
          <li className="navbar-item">
            <Link to="/login" className="navbar-link">
              Login
            </Link>
          </li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
