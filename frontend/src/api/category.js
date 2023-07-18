import instance from './index.js';

export const getCategoryList = () => instance.get(`/categories/`);
export const getCategoryDetail = (id) => instance.get(`/categories/${id}/`);
export const compareSpending = (id, data) => instance.get(`/categories/${id}/compare_spending/`, data);
