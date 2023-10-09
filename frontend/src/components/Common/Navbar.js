import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../../context/AuthContext';
import Dropdown from './Dropdown';
import '../../styles/Common/Navbar.css';

const Navbar = () => {
  const { user } = useContext(AuthContext);

  return (
    <nav className="navbar">
      <ul className="navbar-list">
        <li className="navbar-item">
          <Link to="/" className="navbar-link">
            Home
          </Link>
        </li>
        <li className="navbar-item">
          <Dropdown route="/friends" title="Friends">
            {/* Add more links here */}
          </Dropdown>
        </li>
        <li className="navbar-item">
          <Dropdown route="/transactions" title="Transactions">
            <Link to="/transactions/splits">Splits</Link>
            <Link to="/transactions/bulk-upload">Import transactions</Link>
            <Link to="/transactions/splits">Splits</Link>
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
