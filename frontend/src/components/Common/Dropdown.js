import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';
import { logMessage } from '../../api/loging'; // Importing logMessage function

const Dropdown = ({ route, title, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleMouseOver = () => {
    setIsOpen(true);
    logMessage('info', `Dropdown ${title} opened`, 'Dropdown'); // Log dropdown open
  };

  const handleMouseOut = () => {
    setIsOpen(false);
    logMessage('info', `Dropdown ${title} closed`, 'Dropdown'); // Log dropdown close
  };

  return (
    <div onMouseOver={handleMouseOver} onMouseOut={handleMouseOut}>
      <Link to={route} className="navbar-link">
        {title}
      </Link>
      {isOpen && (
        <div className="dropdown-menu">
          {React.Children.map(children, (child) =>
            React.cloneElement(child, { className: 'dropdown-link' }),
          )}
        </div>
      )}
    </div>
  );
};

// Define the prop types
Dropdown.propTypes = {
  route: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node,
};

export default Dropdown;
