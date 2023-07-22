import axios from 'axios';
import AuthService from '../services/authService';

const API_URL = 'http://127.0.0.1:8000/api_v1';

const instance = axios.create({
    baseURL: API_URL,
  });
  

export const authenticatedRequest = (method, url, data = null) => {
  const token = AuthService.getCurrentUser()?.access_token;
  if (token) {
    return instance({
      method,
      url,
      data,
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(response => response.data)
    .catch(error => { throw error });
  } else {
    throw new Error('No access token available');
  }
};

export default instance;