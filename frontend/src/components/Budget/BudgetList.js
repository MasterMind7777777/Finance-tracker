import React, { useEffect, useState } from 'react';
import ListRenderer from '../Common/Lists/ListBase';
import { getBudgetList } from '../../api/budget';
import AuthService from '../../services/authService';
import { logMessage } from '../../api/loging'; // Import the logMessage function

const BudgetList = () => {
  const [budgets, setBudgets] = useState([]);
  const [budgetTitles, setBudgetTitles] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      logMessage('info', 'Attempting to fetch budget list.', 'BudgetList');
      getBudgetList(token)
        .then((data) => {
          logMessage('info', 'Successfully fetched budget list.', 'BudgetList');
          setBudgets(data);

          // Generate titles for each budget item, similar to transactions
          const titles = data.map(
            (budget) => `Budget for category: ${budget.category}`,
          );
          setBudgetTitles(titles);
        })
        .catch((err) => {
          logMessage(
            'error',
            `Failed to fetch budget list. Error: ${err}`,
            'BudgetList',
          );
          console.error('Error fetching data:', err);
        });
    } else {
      logMessage(
        'warn',
        'User is not authenticated. Skipping budget list fetching.',
        'BudgetList',
      );
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
