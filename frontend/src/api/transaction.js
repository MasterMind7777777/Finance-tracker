import { authenticatedRequest } from './index.js';

export const getTransactionRecommendations = () =>
  authenticatedRequest('get', '/transactions/recommendations/');
export const getSavingsOpportunities = (categoryId) =>
  authenticatedRequest(
    'get',
    `/transactions/savings_opportunities/${categoryId}`,
  );
export const assignCategory = (transactionId, data) =>
  authenticatedRequest(
    'post',
    `/transactions/${transactionId}/assign_category`,
    data,
  );
export const getSplitTransactions = () =>
  authenticatedRequest('get', `/transaction_splits/`);
export const splitTransaction = (id, data) =>
  authenticatedRequest('post', `/transactions/${id}/split_transaction/`, data);
export const acceptTransactionSplit = (id) =>
  authenticatedRequest('put', `/transaction_splits/${id}/accept/`);
export const declineTransactionSplit = (id) =>
  authenticatedRequest('put', `/transaction_splits/${id}/decline/`);
export const getTransactionList = () =>
  authenticatedRequest('get', '/transactions/');
export const createTransaction = (data) =>
  authenticatedRequest('post', '/transactions/', data);
export const getTransactionDetail = (id) =>
  authenticatedRequest('get', `/transactions/${id}/`);
export const deleteTransaction = (id) =>
  authenticatedRequest('Delete', `/transactions/${id}/`);
export const updateTransaction = (id, data) =>
  authenticatedRequest('put', `/transactions/${id}/`, data);
export const bulkUploadTransactions = async (file) => {
  const url = '/transactions/bulk_upload/';
  const formData = new FormData();
  formData.append('file', file);

  const response = await authenticatedRequest('post', url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response;
};
export const forecastExpenses = () =>
  authenticatedRequest('get', '/transactions/forecast_expenses/');
