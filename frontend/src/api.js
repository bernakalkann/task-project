import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
});

// Her istekten önce çalışır
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // Django'nun beklediği "Token <deger>" formatı
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;