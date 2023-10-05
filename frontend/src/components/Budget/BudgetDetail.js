import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getBudgetDetail } from '../../api/budget';

const BudgetDetail = () => {
  const [budget, setBudget] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchBudget = async () => {
      const response = await getBudgetDetail(id);
      setBudget(response);
    };

    fetchBudget();
  }, [id]);

  return budget ? (
    <div>
      <h2>{budget.id}</h2>
      <p>{budget.category}</p>
      {/* Render other budget properties */}
    </div>
  ) : (
    <p>Loading...</p>
  );
};

export default BudgetDetail;
