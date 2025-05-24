import { defineStore } from 'pinia';
import { login, refreshToken } from '../api';
import type { User } from '../types/index';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refresh_token'),
    user: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  
  actions: {
    async login(username: string, password: string) {
      try {
        const response = await login(username, password);
        this.token = response.data.access;
        this.refreshToken = response.data.refresh;
        
        // 存储token到localStorage
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        return true;
      } catch (error) {
        console.error('登录失败:', error);
        return false;
      }
    },
    
    async refresh() {
      if (!this.refreshToken) return false;
      
      try {
        const response = await refreshToken(this.refreshToken);
        this.token = response.data.access;
        
        // 更新localStorage中的token
        localStorage.setItem('token', response.data.access);
        
        return true;
      } catch (error) {
        console.error('刷新token失败:', error);
        this.logout();
        return false;
      }
    },
    
    logout() {
      this.token = null;
      this.refreshToken = null;
      this.user = null;
      
      // 清除localStorage中的token
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
    }
  }
});