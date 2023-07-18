import instance from './index.js';

export const getBudgetAlerts = () => instance.get(`/budgets/alerts/`);
export const getBudgetList = () => instance.get(`/budgets/`);
export const getBudgetDetail = (id) => instance.get(`/budgets/${id}/`);
export const createCustomAlert = (id, data) => instance.post(`/budgets/${id}/create_custom_alert/`, data);
