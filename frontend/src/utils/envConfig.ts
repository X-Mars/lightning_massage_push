/**
 * 环境配置工具类
 */
export class EnvConfig {
  // 基础环境信息
  static get nodeEnv(): string {
    return import.meta.env.VITE_NODE_ENV || 'development';
  }

  static get envName(): string {
    return import.meta.env.VITE_ENV_NAME || 'development';
  }

  static get envDisplayName(): string {
    return import.meta.env.VITE_ENV_DISPLAY_NAME || '开发环境';
  }

  static get appTitle(): string {
    return import.meta.env.VITE_APP_TITLE || '闪电推送系统';
  }

  static get appVersion(): string {
    return import.meta.env.VITE_APP_VERSION || '1.0.0';
  }

  // API 配置
  static get apiBaseUrl(): string {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }

  static get wsBaseUrl(): string {
    return import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
  }

  static get apiTimeout(): number {
    return parseInt(import.meta.env.VITE_API_TIMEOUT || '10000');
  }

  // 功能开关
  static get isDebug(): boolean {
    return import.meta.env.VITE_DEBUG === 'true';
  }

  static get useMock(): boolean {
    return import.meta.env.VITE_USE_MOCK === 'true';
  }

  static get showEnvTag(): boolean {
    return import.meta.env.VITE_SHOW_ENV_TAG === 'true';
  }

  static get devTools(): boolean {
    return import.meta.env.VITE_DEV_TOOLS === 'true';
  }

  static get enablePerformance(): boolean {
    return import.meta.env.VITE_ENABLE_PERFORMANCE === 'true';
  }

  static get enableErrorReporting(): boolean {
    return import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true';
  }

  static get enableAnalytics(): boolean {
    return import.meta.env.VITE_ENABLE_ANALYTICS === 'true';
  }

  // 其他配置
  static get logLevel(): 'debug' | 'info' | 'warn' | 'error' {
    const level = import.meta.env.VITE_LOG_LEVEL;
    if (['debug', 'info', 'warn', 'error'].includes(level)) {
      return level as 'debug' | 'info' | 'warn' | 'error';
    }
    return 'info';
  }

  static get uploadSizeLimit(): number {
    return parseInt(import.meta.env.VITE_UPLOAD_SIZE_LIMIT || '10');
  }

  static get cdnUrl(): string {
    return import.meta.env.VITE_CDN_URL || '';
  }

  static get sentryDsn(): string {
    return import.meta.env.VITE_SENTRY_DSN || '';
  }

  // 环境判断
  static get isDevelopment(): boolean {
    return this.nodeEnv === 'development';
  }

  static get isTest(): boolean {
    return this.nodeEnv === 'test';
  }

  static get isStaging(): boolean {
    return this.nodeEnv === 'staging';
  }

  static get isProduction(): boolean {
    return this.nodeEnv === 'production';
  }

  static get testMode(): boolean {
    return import.meta.env.VITE_TEST_MODE === 'true';
  }

  // 获取完整的环境信息
  static getEnvInfo() {
    return {
      nodeEnv: this.nodeEnv,
      envName: this.envName,
      envDisplayName: this.envDisplayName,
      appTitle: this.appTitle,
      appVersion: this.appVersion,
      apiBaseUrl: this.apiBaseUrl,
      wsBaseUrl: this.wsBaseUrl,
      isDebug: this.isDebug,
      buildTime: __BUILD_TIME__,
      logLevel: this.logLevel,
    };
  }

  // 打印环境信息到控制台
  static printEnvInfo() {
    if (this.isDebug) {
      console.group('🌍 环境配置信息');
      console.table(this.getEnvInfo());
      console.groupEnd();
    }
  }
}
