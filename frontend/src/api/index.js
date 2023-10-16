import axios from 'axios';
import AuthService from '../services/authService';
// import { logMessage } from './loging';

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
        Authorization: `Bearer ${token}`,
      },
    })
      .then((response) => {
        // logMessage(
        //   'info',
        //   `Request to ${url} successful.`,
        //   'authenticatedRequest',
        // ); // Success log
        return response.data;
      })
      .catch((error) => {
        // logMessage(
        //   'error',
        //   `Request to ${url} failed. Error: ${error}`,
        //   'authenticatedRequest',
        // ); // Error log
        throw error;
      });
  } else {
    // logMessage(
    //   'warn',
    //   'No access token available. Request failed.',
    //   'authenticatedRequest',
    // ); // Warning log
    throw new Error('No access token available');
  }
};

export default instance;
