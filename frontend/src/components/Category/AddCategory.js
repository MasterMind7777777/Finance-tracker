import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCategory } from '../../api/category';
import FormComponent from '../Common/forms/FormComponent.js';

export const CategoryCreate = () => {
  const CATEGORY_TYPES = [
    { value: 'expense', label: 'Expense' },
    { value: 'income', label: 'Income' },
    { value: 'saving', label: 'Saving' },
    { value: 'investment', label: 'Investment' },
  ];

  const [name, setName] = useState('');
  const [type, setType] = useState(CATEGORY_TYPES[0].value);
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
            type: 'select',
            props: {
              value: type,
              onChange: (e) => {
                setType(e.target.value);
              },
            },
            options: CATEGORY_TYPES.map((categoryType) => ({
              value: categoryType.value,
              label: categoryType.label,
            })),
          },
        ]}
      />
    </div>
  );
};

export default CategoryCreate;
