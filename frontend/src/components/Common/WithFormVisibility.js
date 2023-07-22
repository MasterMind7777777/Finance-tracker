import React, { useState } from 'react';

const WithFormVisibility = (FormComponent) => {
  const ComponentWithVisibility = (props) => {
    const [showForm, setShowForm] = useState(false);

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
