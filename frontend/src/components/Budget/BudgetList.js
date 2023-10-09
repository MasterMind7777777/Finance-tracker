import React, { useEffect, useState } from 'react';
import ListRenderer from '../Common/Lists/ListBase';
import { getBudgetList } from '../../api/budget';
import AuthService from '../../services/authService';

const BudgetList = () => {
  const [budgets, setBudgets] = useState([]);
  const [budgetTitles, setBudgetTitles] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      console.log('Fetching budget list...');
      getBudgetList(token)
        .then((data) => {
          console.log('Received data:', data);
          setBudgets(data);

          // Generate titles for each budget item, similar to transactions
          const titles = data.map(
            (budget) => `Budget for category: ${budget.category}`,
          );
          setBudgetTitles(titles);
        })
        .catch((err) => {
          console.error('Error fetching data:', err);
        });
    }
  }, []);

  const contentConfig = {
    title: 'category',
    paragraphs: [
      {
        label: 'Limit',
        key: 'budget_limit',
      },
    ],
    links: [
      {
        link: 'id',
        linkPrefix: '/budgets/',
        linkText: 'View Details',
      },
    ],
  };

  return (
    <div>
      <h1>Budget List</h1>
      <ListRenderer
        items={budgets}
        itemTitles={budgetTitles}
        keyExtractor={(item, index) => `${item.id}-${index}`}
        title="Budgets"
        contentConfig={contentConfig}
      />
    </div>
  );
};

export default BudgetList;
