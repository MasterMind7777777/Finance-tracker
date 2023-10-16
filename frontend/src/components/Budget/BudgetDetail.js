import { DetailComponent } from '../Common/Detail/DetailBase'; // Import generalized DetailComponent
import React from 'react';
import { getBudgetDetail } from '../../api/budget';
import { logMessage } from '../../api/loging'; // Import the logMessage function

const BudgetDetail = () => {
  const fetchDetail = async (id) => {
    try {
      logMessage(
        'info',
        `Fetching budget details for ID: ${id}`,
        'BudgetDetail',
      );
      const response = await getBudgetDetail(id);
      logMessage(
        'info',
        `Successfully fetched budget details for ID: ${id}`,
        'BudgetDetail',
      );
      return response;
    } catch (error) {
      logMessage(
        'error',
        `Error fetching budget details for ID: ${id}. Error: ${error}`,
        'BudgetDetail',
      );
      console.error(error);
    }
  };

  const detailFields = [
    { key: 'id', label: 'ID' },
    { key: 'category', label: 'Category' },
    { key: 'budget_limit', label: 'Limit' },
    // ... other budget properties you want to display
  ];

  return (
    <DetailComponent
      fetchDetail={fetchDetail}
      detailFields={detailFields}
      entityTitle="Budget Detail"
    />
  );
};

export default BudgetDetail;
