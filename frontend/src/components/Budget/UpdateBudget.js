import React, { useState, useEffect } from 'react';
import { getBudgetDetail, updateBudget } from '../../api/budget';
import { useParams } from 'react-router-dom';
import { logMessage } from '../../api/loging'; // Import centralized logging function

const UpdateBudget = () => {
  const [name, setName] = useState('');
  const [amount, setAmount] = useState(0);
  const [category, setCategory] = useState('');
  const { id } = useParams();

  useEffect(() => {
    const fetchBudget = async () => {
      try {
        logMessage(
          'info',
          `Attempting to fetch budget details for ID: ${id}`,
          'UpdateBudget',
        );
        const budget = await getBudgetDetail(id);
        setName(budget.name);
        setAmount(budget.amount);
        setCategory(budget.category);
        logMessage(
          'info',
          'Successfully fetched budget details.',
          'UpdateBudget',
        );
      } catch (error) {
        logMessage(
          'error',
          `Failed to fetch budget details: ${error}`,
          'UpdateBudget',
        );
      }
    };

    fetchBudget();
  }, [id]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      logMessage('info', 'Attempting to update budget.', 'UpdateBudget');
      await updateBudget(id, { name, amount, category });
      logMessage('info', 'Successfully updated budget.', 'UpdateBudget');
    } catch (error) {
      logMessage('error', `Failed to update budget: ${error}`, 'UpdateBudget');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />
      <button type="submit">Update Budget</button>
    </form>
  );
};

export default UpdateBudget;
