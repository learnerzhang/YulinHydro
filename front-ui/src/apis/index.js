import axios from 'axios'
import errorHandler from '@/utils/errorHandler';
// import { create, get, update } from 'lodash'
const api = axios.create({
  baseURL: '/xapi',
  timeout: 10000
});

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
api.interceptors.response.use(
  response => response,
  async error => {
    // 处理其他错误
    errorHandler.handleApiError(error);
    return Promise.reject(error);
  }
);
export default {
  getNewsTags: () => api.get('/api/tagapi/tags/'),
  getPdfDetail: (id) => api.get(`/api/documentapi/documents/${id}`),
  getEsSearch: (query, taglist, start_date, end_date, page, pageSize) => 
    api.post('/api/documentapi/es_search_related', {
      "query": query,
      "page_size": pageSize,
      "page_number": page,
      "search_in": [
        "fragments.content",
        "document.content"
      ]
    }),
  getDefaultSearch: (query, page, pageSize) => 
    api.get('/api/documentapi/default_search', {
      params: { 
        query: query, 
        page_number: page,
        page_size: pageSize
      }
    }),
}