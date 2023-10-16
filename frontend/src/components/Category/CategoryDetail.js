import { DetailComponent } from '../Common/Detail/DetailBase';
import React from 'react';
import {
  getCategoryDetail,
  deleteCategory as apiDeleteCategory,
} from '../../api/category';
import { useParams } from 'react-router-dom';
import { logMessage } from '../../api/loging'; // Import centralized logging function

export const CategoryDetail = () => {
  const { id } = useParams();

  const fetchDetail = async (id) => {
    try {
      const response = await getCategoryDetail(id);
      logMessage(
        'info',
        `Fetched detail for category with ID: ${id}`,
        'CategoryDetail',
      );
      return response;
    } catch (error) {
      logMessage(
        'error',
        `Failed to fetch detail for category with ID: ${id}. Error: ${error.message}`,
        'CategoryDetail',
      );
      console.error(error);
    }
  };

  const handleDeleteAction = async () => {
    try {
      await apiDeleteCategory(id);
      logMessage(
        'info',
        `Successfully deleted category with ID: ${id}`,
        'CategoryDetail',
      );
    } catch (error) {
      logMessage(
        'error',
        `Failed to delete category with ID: ${id}. Error: ${error.message}`,
        'CategoryDetail',
      );
      console.error(error);
    }
  };

  const detailFields = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'type', label: 'Type' },
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
