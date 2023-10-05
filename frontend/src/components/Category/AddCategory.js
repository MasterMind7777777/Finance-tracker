import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCategory } from '../../api/category';
import FormComponent from '../Common/forms/FormComponent.js';

export const CategoryCreate = () => {
  const [name, setName] = useState('');
  const [type, setType] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();

    createCategory({ name, type })
      .then(() => {
        navigate('/categories');
      })
      .catch((error) => console.error(error));
  };

  return (
    <div>
      <h2>Create Category</h2>
      <FormComponent
        formClassName="create-category-form"
        buttonText="Create"
        onSubmit={handleSubmit}
        fields={[
          {
            label: 'Name',
            type: 'text',
            props: {
              value: name,
              onChange: (e) => setName(e.target.value),
            },
          },
          {
            label: 'Type',
            type: 'text',
            props: {
              value: type,
              onChange: (e) => setType(e.target.value),
            },
          },
        ]}
      />
    </div>
  );
};

export default CategoryCreate;
