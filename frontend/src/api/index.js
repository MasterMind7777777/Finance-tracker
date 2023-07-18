import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api_v1';

const instance = axios.create({
    baseURL: API_URL,
  });
  
  export default instance;