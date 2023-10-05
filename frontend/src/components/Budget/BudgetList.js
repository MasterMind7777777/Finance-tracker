import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getBudgetList } from '../../api/budget';
import AuthService from '../../services/authService';

const BudgetList = () => {
  const [budgets, setBudgets] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      getBudgetList(token)
        .then((data) => setBudgets(data))
        .catch((err) => console.error(err));
    }
  }, []);

  return (
    <div>
      <h1>Budget List</h1>
      {budgets.map((budget) => (
        <div key={budget.id}>
          <Link to={`/budgets/${budget.id}`}>{budget.category}</Link>
          <p>{budget.budget_limit}</p>
        </div>
      ))}
    </div>
  );
};

export default BudgetList;
