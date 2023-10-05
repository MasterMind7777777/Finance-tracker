import instance from './index.js';

export const getSavingGoalList = () => instance.get(`/saving_goals/`);
export const getSavingGoalDetail = (id) => instance.get(`/saving_goals/${id}/`);
export const addCategories = (id, data) =>
  instance.post(`/saving_goals/${id}/add_categories/`, data);
export const addUsers = (id, data) =>
  instance.post(`/saving_goals/${id}/add_users/`, data);
export const removeCategories = (id, data) =>
  instance.post(`/saving_goals/${id}/remove_categories/`, data);
export const removeUsers = (id, data) =>
  instance.post(`/saving_goals/${id}/remove_users/`, data);
