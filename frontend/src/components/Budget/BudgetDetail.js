import { DetailComponent } from '../Common/Detail/DetailBase'; // Import generalized DetailComponent
import React from 'react';
import { getBudgetDetail } from '../../api/budget';

const BudgetDetail = () => {
  const fetchDetail = async (id) => {
    try {
      const response = await getBudgetDetail(id);
      return response;
    } catch (error) {
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
