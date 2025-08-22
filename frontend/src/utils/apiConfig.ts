import { EnvConfig } from './envConfig';

/**
 * API 配置工具
 */
export class ApiConfig {
  /**
   * 获取 API 基础地址
   * 开发环境使用相对路径通过代理，其他环境使用完整URL
   */
  static getBaseURL(): string {
    if (EnvConfig.isDevelopment) {
      return '/api'; // 开发环境使用代理
    }
    return `${EnvConfig.apiBaseUrl}/api`; // 其他环境使用完整URL
  }

  /**
   * 获取完整的 API 地址
   */
  static getFullURL(endpoint: string): string {
    const baseURL = this.getBaseURL();
    return `${baseURL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  }

  /**
   * 打印 API 配置信息
   */
  static printApiConfig(): void {
    if (EnvConfig.isDebug) {
      console.group('🔗 API 配置信息');
      console.log('环境:', EnvConfig.envDisplayName);
      console.log('Base URL:', this.getBaseURL());
      console.log('API 地址配置:', EnvConfig.apiBaseUrl);
      console.log('超时时间:', `${EnvConfig.apiTimeout}ms`);
      console.log('使用代理:', EnvConfig.isDevelopment ? '是' : '否');
      console.groupEnd();
    }
  }

  /**
   * 检查 API 连接
   */
  static async checkConnection(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(this.getFullURL('/health/'), {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.warn('API 连接检查失败:', error);
      return false;
    }
  }
}
