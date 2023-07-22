import { authenticatedRequest } from './index.js';

export const getCategoryList = () => authenticatedRequest('get', '/categories/');
export const createCategory = (data) => authenticatedRequest('post', '/categories/', data);
export const getCategoryDetail = (id) => authenticatedRequest('get', `/categories/${id}/`);
export const updateCategory = (id, data) => authenticatedRequest('put', `/categories/${id}/`, data);
export const deleteCategory = (id) => authenticatedRequest('delete', `/categories/${id}/`);
export const compareSpending = (id, data) => authenticatedRequest('get', `/categories/${id}/compare_spending/`, data);
