import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Dropdown = ({ route, title, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleMouseOver = () => {
    setIsOpen(true);
  };

  const handleMouseOut = () => {
    setIsOpen(false);
  };

  return (
    <div onMouseOver={handleMouseOver} onMouseOut={handleMouseOut}>
      <Link to={route} className="navbar-link">
        {title}
      </Link>
      {isOpen && <div className="dropdown-menu">{React.Children.map(children, child => React.cloneElement(child, { className: 'dropdown-link' }))}</div>}
    </div>
  );
};

export default Dropdown;
