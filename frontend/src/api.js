import axios from 'axios';
import { decryptData } from './utils/encryption';

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

// Sunucudan gelen yanıtları işler (Şifreli veriler otomatik çözülür)
api.interceptors.response.use(async (response) => {
  if (response.data && response.data.is_encrypted && response.data.encrypted_data) {
    try {
      const decrypted = await decryptData(response.data);
      response.data = decrypted;
    } catch (e) {
      console.error("Yanıt şifresi çözülemedi:", e);
    }
  }
  return response;
}, (error) => {
  return Promise.reject(error);
});

export default api;