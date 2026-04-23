import axios from 'axios';

// Create axios instance with dynamic base URL
const getBackendUrl = () => {
  if (import.meta.env.PROD) {
    // Try multiple possible Railway URLs
    const possibleUrls = [
      'https://epom-production.up.railway.app',
      'https://epom.up.railway.app',
      'https://epom-backend.up.railway.app',
      // Fallback to current origin if backend is served with frontend
      window.location.origin
    ];
    return possibleUrls[0]; // Default to first option
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

// Add response interceptor to handle errors and fallback URLs
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // If we get a network error or CORS error in production, try fallback URLs
    if (import.meta.env.PROD && (error.code === 'NETWORK_ERROR' || error.code === 'ERR_NETWORK' || error.message?.includes('CORS'))) {
      const possibleUrls = [
        'https://epom-production.up.railway.app',
        'https://epom.up.railway.app',
        'https://epom-backend.up.railway.app',
        window.location.origin
      ];
      
      // Try next URL if available
      const currentUrl = api.defaults.baseURL;
      const currentIndex = currentUrl ? possibleUrls.indexOf(currentUrl) : -1;
      
      if (currentIndex < possibleUrls.length - 1) {
        const nextUrl = possibleUrls[currentIndex + 1];
        api.defaults.baseURL = nextUrl;
        
        // Retry the original request with new URL
        if (error.config) {
          console.log(`Retrying request with fallback URL: ${nextUrl}`);
          return api.request(error.config);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
