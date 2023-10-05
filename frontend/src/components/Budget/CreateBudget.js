import React, { useState } from 'react';
import { createBudget } from '../../api/budget';
import FormComponent from '../Common/forms/FormComponent.js';

const CreateBudget = () => {
  const [budgetLimit, setBudgetLimit] = useState(0);
  const [category, setCategory] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();

    createBudget({ budget_limit: budgetLimit, category })
      .then((data) => {
        // Handle success message here
      })
      .catch((error) => {
        // Handle the error here
      });
  };

  return (
    <FormComponent
      formClassName="create-budget-form"
      buttonText="Create Budget"
      onSubmit={handleSubmit}
      fields={[
        {
          label: 'Budget Limit',
          type: 'number',
          props: {
            placeholder: 'Budget Limit',
            value: budgetLimit,
            onChange: (e) => setBudgetLimit(e.target.value),
            required: true,
          },
        },
        {
          label: 'Category',
          type: 'text',
          props: {
            placeholder: 'Category',
            value: category,
            onChange: (e) => setCategory(e.target.value),
            required: true,
          },
        },
      ]}
    />
  );
};

export default CreateBudget;
