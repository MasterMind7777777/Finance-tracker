import React, { useState, useEffect } from 'react';
import { getBudgetDetail, updateBudget } from '../../api/budget';
import { useParams, useNavigate } from 'react-router-dom';

const UpdateBudget = ({ match }) => {
  const [name, setName] = useState('');
  const [amount, setAmount] = useState(0);
  const [category, setCategory] = useState('');
  const { id } = useParams();

  useEffect(() => {
    const fetchBudget = async () => {
      const budget = await getBudgetDetail(id);
      setName(budget.name);
      setAmount(budget.amount);
      setCategory(budget.category);
    };

    fetchBudget();
  }, [id]);

  const handleSubmit = (event) => {
    event.preventDefault();

    updateBudget(id, { name, amount, category })
      .then((data) => {
        // You can handle success message here
      })
      .catch((error) => {
        // Handle the error here
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="number" placeholder="Amount" value={amount} onChange={e => setAmount(e.target.value)} required />
      <button type="submit">Update Budget</button>
    </form>
  );
};

export default UpdateBudget;
