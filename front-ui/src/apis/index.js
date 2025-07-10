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
  getNewsTags: () => api.get('/api/documentapi/taglist'),
  searchDocList: (query, taglist, start_date, end_date, page, pageSize) => 
    api.get('/api/documentapi/list', {
      params: { 
        keyword: query, 
        taglist: Array.isArray(taglist) ? taglist.join(',') : '',
        startDate: start_date,
        endDate: end_date,
        page: page,
        pageSize: pageSize
      }
    }),
}