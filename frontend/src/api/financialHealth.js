import instance from './index.js';

export const getFinancialHealth = () => instance.get(`/financial-health/`);
