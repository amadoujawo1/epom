import axios from 'axios';

// Create axios instance with dynamic base URL
const getBackendUrl = () => {
  if (import.meta.env.PROD) {
    // Use the correct Railway deployment URL
    return 'https://epom.up.railway.app';
  }
  return 'http://127.0.0.1:5007'; // In development, use local backend
};

const api = axios.create({
  baseURL: getBackendUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Log detailed error information for debugging Railway issues
    if (import.meta.env.PROD) {
      console.error('Railway API Error:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: error.response?.data,
        baseURL: api.defaults.baseURL,
        url: error.config?.url
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
