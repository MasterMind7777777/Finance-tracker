import React, { useState } from 'react';
import { createBudget } from '../../api/budget';

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
      <form onSubmit={handleSubmit}>
        <input type="number" placeholder="Budget Limit" value={budgetLimit} onChange={e => setBudgetLimit(e.target.value)} required />
        <input type="text" placeholder="Category" value={category} onChange={e => setCategory(e.target.value)} required />
        <button type="submit">Create Budget</button>
      </form>
    );
  };

export default CreateBudget;
