import { authenticatedRequest } from './index.js';

export const getBudgetAlerts = () => authenticatedRequest('get', '/budgets/alerts/');
export const getBudgetList = () => authenticatedRequest('get', '/budgets/');
export const createBudget = (data) => authenticatedRequest('post', '/budgets/', data); //TODO
export const getBudgetDetail = (id) => authenticatedRequest('get', `/budgets/${id}/`);
export const updateBudget = (id, data) => authenticatedRequest('put', `/budgets/${id}/`, data); //TODO
export const createCustomAlert = (id, data) => authenticatedRequest('post', `/budgets/${id}/create_custom_alert/`, data);
