import React, { useState, useEffect } from 'react'; // Added useEffect
import { logMessage } from '../../api/loging'; // Importing logMessage function

const WithFormVisibility = (FormComponent) => {
  const ComponentWithVisibility = (props) => {
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
      if (showForm) {
        logMessage('info', 'Form is now visible', 'WithFormVisibility');
      } else {
        logMessage('info', 'Form is now hidden', 'WithFormVisibility');
      }
    }, [showForm]);

    if (!showForm) {
      return <button onClick={() => setShowForm(true)}>Add New</button>;
    }

    return (
      <div>
        <FormComponent {...props} onFormSubmit={() => setShowForm(false)} />
        <button onClick={() => setShowForm(false)}>Cancel</button>
      </div>
    );
  };

  return ComponentWithVisibility;
};

export default WithFormVisibility;
