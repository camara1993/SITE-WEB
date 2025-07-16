import axios from 'axios';
import { getAuthToken } from './auth';

const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth endpoints
export const login = (credentials) => api.post('/auth/login', credentials);
export const register = (userData) => api.post('/auth/register', userData);

// Article endpoints
export const getPublishedArticles = (page = 0, size = 10) => 
  api.get(`/articles/public?page=${page}&size=${size}`);
export const getArticle = (id) => api.get(`/articles/public/${id}`);
export const getArticlesByCategory = (categoryId, page = 0, size = 10) => 
  api.get(`/articles/public/category/${categoryId}?page=${page}&size=${size}`);
export const createArticle = (article) => api.post('/articles/editor', article);
export const updateArticle = (id, article) => api.put(`/articles/editor/${id}`, article);
export const deleteArticle = (id) => api.delete(`/articles/editor/${id}`);

// Category endpoints
export const getCategories = () => api.get('/categories');
export const createCategory = (category) => api.post('/categories/editor', category);
export const updateCategory = (id, category) => api.put(`/categories/editor/${id}`, category);
export const deleteCategory = (id) => api.delete(`/categories/editor/${id}`);

// User endpoints (admin only)
export const getUsers = () => api.get('/users');
export const createUser = (user) => api.post('/users', user);
export const updateUser = (id, user) => api.put(`/users/${id}`, user);
export const deleteUser = (id) => api.delete(`/users/${id}`);

// Token endpoints (admin only)
export const getTokens = () => api.get('/tokens');
export const createToken = (tokenData) => api.post('/tokens', tokenData);
export const revokeToken = (token) => api.delete(`/tokens/${token}`);

// REST API endpoints
export const getAllArticlesRest = (format = 'json') => 
  api.get('/rest/articles', {
    headers: { 'Accept': format === 'xml' ? 'application/xml' : 'application/json' }
  });
export const getArticlesGroupedRest = (format = 'json') => 
  api.get('/rest/articles/grouped', {
    headers: { 'Accept': format === 'xml' ? 'application/xml' : 'application/json' }
  });
export const getArticlesByCategoryRest = (categoryName, format = 'json') => 
  api.get(`/rest/articles/category/${categoryName}`, {
    headers: { 'Accept': format === 'xml' ? 'application/xml' : 'application/json' }
  });

export default api;