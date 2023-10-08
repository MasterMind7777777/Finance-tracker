import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createBudget } from '../../api/budget';
import { getCategoryList } from '../../api/category';
import FormComponent from '../Common/forms/FormComponent.js';

const CreateBudget = () => {
  const navigate = useNavigate();
  const [budgetLimit, setBudgetLimit] = useState(0);
  const [category, setCategory] = useState('');
  const [categoryOptions, setCategoryOptions] = useState([]); // State to store category options

  // Fetch category options when the component mounts
  useEffect(() => {
    async function fetchCategories() {
      try {
        const response = await getCategoryList();
        if (Array.isArray(response) && response.length > 0) {
          setCategoryOptions(response);
          setCategory(response[0].id); // Setting the initial category to the first element's ID
        } else {
          console.error('Response data is not an array or is empty');
        }
      } catch (error) {
        console.error('Error fetching categories: ', error);
      }
    }

    fetchCategories();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const newBudget = await createBudget({
        budget_limit: budgetLimit,
        category,
      });
      console.log(newBudget);
      navigate(`/budgets/${newBudget.id}`);
    } catch (error) {
      console.error('Error creating budget:', error);
      // Handle the error here
    }
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
          type: 'select',
          props: {
            value: category,
            onChange: (e) => setCategory(e.target.value),
            required: true,
          },
          options: categoryOptions
            ? categoryOptions.map((categoryOption) => {
                return {
                  value: categoryOption.id,
                  label: categoryOption.name,
                };
              })
            : [], // Default to an empty array if categoryOptions is not available
        },
      ]}
    />
  );
};

export default CreateBudget;
