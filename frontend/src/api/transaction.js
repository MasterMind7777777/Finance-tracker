import instance from './index.js';

export const getTransactionRecommendations = () => instance.get(`/transactions/recommendations/`);
export const getSavingsOpportunities = (categoryId) => instance.get(`/transactions/savings_opportunities/${categoryId}`);
export const assignCategory = (transactionId, data) => instance.post(`/transactions/${transactionId}/assign_category`, data);
export const acceptTransactionSplit = (id) => instance.post(`/transaction_splits/${id}/accept/`);
export const declineTransactionSplit = (id) => instance.post(`/transaction_splits/${id}/decline/`);
export const getTransactionList = () => instance.get(`/transactions/`);
export const getTransactionDetail = (id) => instance.get(`/transactions/${id}/`);
export const bulkUploadTransactions = (data) => instance.post(`/transactions/bulk_upload/`, data);
export const forecastExpenses = () => instance.get(`/transactions/forecast_expenses/`);
export const splitTransaction = (id, data) => instance.post(`/transactions/${id}/split_transaction/`, data);
