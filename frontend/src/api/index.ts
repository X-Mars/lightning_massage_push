import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // token过期，清除token并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 登录API
export const login = (username: string, password: string) => {
  return apiClient.post('/token/', { username, password });
};

// 刷新Token
export const refreshToken = (refresh: string) => {
  return apiClient.post('/token/refresh/', { refresh });
};

// 模板相关API
export const templateApi = {
  getTemplates: (params?: any) => apiClient.get('/templates/', { params }),
  getTemplate: (id: number) => apiClient.get(`/templates/${id}/`),
  createTemplate: (data: any) => apiClient.post('/templates/', data),
  updateTemplate: (id: number, data: any) => apiClient.put(`/templates/${id}/`, data),
  deleteTemplate: (id: number) => apiClient.delete(`/templates/${id}/`),
};

// 机器人相关API
export const robotApi = {
  getRobots: (params?: any) => apiClient.get('/robots/', { params }),
  getRobot: (id: number) => apiClient.get(`/robots/${id}/`),
  createRobot: (data: any) => apiClient.post('/robots/', data),
  updateRobot: (id: number, data: any) => apiClient.put(`/robots/${id}/`, data),
  deleteRobot: (id: number) => apiClient.delete(`/robots/${id}/`),
};

// 消息日志相关API
export const logApi = {
  getLogs: (params?: any) => {
    console.log('调用日志API，参数:', params);
    return apiClient.get('/logs/', { params });
  },
  getLog: (id: number) => apiClient.get(`/logs/${id}/`),
};

// 消息推送API
export const pushApi = {
  push: (data: any) => apiClient.post('/push/', data),
};

// 仪表盘相关API
export const dashboardApi = {
  // 获取统计数据（模板总数、机器人总数、本月消息数）
  getStats: () => apiClient.get('/dashboard/stats/'),
  
  // 获取图表数据（趋势图、占比图）
  getCharts: (timeRange = 'week') => apiClient.get('/dashboard/charts/', { 
    params: { time_range: timeRange } 
  }),
  
  // 获取最近消息记录
  getRecentLogs: () => apiClient.get('/dashboard/recent-logs/'),
};

export default apiClient;
