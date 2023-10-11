import { DetailComponent } from '../Common/Detail/DetailBase'; // Import generalized DetailComponent
import React from 'react';
import {
  getCategoryDetail,
  deleteCategory as apiDeleteCategory,
} from '../../api/category';
import { useParams } from 'react-router-dom';

export const CategoryDetail = () => {
  const { id } = useParams();

  const fetchDetail = async (id) => {
    try {
      const response = await getCategoryDetail(id);
      return response;
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteAction = async () => {
    try {
      await apiDeleteCategory(id);
    } catch (error) {
      console.error(error);
    }
  };

  const detailFields = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'type', label: 'Type' },
    // ... other category properties you want to display
  ];
  const actionConfigs = [
    {
      type: 'button',
      Component: {
        label: 'Delete',
        execute: handleDeleteAction,
        navigate: '/categories',
      },
    },
    {
      type: 'link',
      Component: {
        label: 'View saving opportunities',
        navigate: `/categories/${id}/savings_opportunities`,
      },
    },
    // ... additional actions
  ];

  return (
    <DetailComponent
      fetchDetail={fetchDetail}
      detailFields={detailFields}
      actionConfigs={actionConfigs}
      entityTitle="Category Detail"
    />
  );
};

export default CategoryDetail;
