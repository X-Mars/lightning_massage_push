/**
 * 全局错误处理工具
 */
import { ElMessage } from 'element-plus';

interface FormattedError {
  formattedMessage: string;
}

interface ApiError extends Error {
  response?: {
    status: number;
    data: unknown;
  };
  request?: unknown;
}

function isFormattedError(error: unknown): error is FormattedError {
  return error !== null && typeof error === 'object' && 'formattedMessage' in error;
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof Error;
}

/**
 * 处理API错误并显示友好的错误消息
 * @param error 错误对象
 * @param defaultMessage 默认错误消息
 */
export function handleApiError(error: unknown, defaultMessage = '操作失败'): string {
  // console.error('API请求错误:', error);

  // 优先使用经过拦截器处理的格式化消息
  if (isFormattedError(error)) {
    ElMessage.error(error.formattedMessage);
    return error.formattedMessage;
  }

  // 尝试从响应中提取错误信息
  if (isApiError(error) && error.response) {
    const { status, data } = error.response;

    // 处理不同的HTTP状态码
    switch (status) {
      case 400: // Bad Request
        if (data) {
          if (typeof data === 'object') {
            // 尝试提取字段错误信息
            const errorMessages = [];
            for (const [field, messages] of Object.entries(data)) {
              if (Array.isArray(messages)) {
                errorMessages.push(`${field}: ${messages.join(', ')}`);
              } else if (typeof messages === 'string') {
                errorMessages.push(`${field}: ${messages}`);
              }
            }

            if (errorMessages.length > 0) {
              const message = errorMessages.join('\n');
              ElMessage.error(message);
              return message;
            }
          } else if (typeof data === 'string') {
            ElMessage.error(data);
            return data;
          }
        }
        ElMessage.error('请求参数错误');
        return '请求参数错误';

      case 401: // Unauthorized
        ElMessage.error('未授权，请重新登录');
        return '未授权，请重新登录';

      case 403: // Forbidden
        ElMessage.error('没有权限执行此操作');
        return '没有权限执行此操作';

      case 404: // Not Found
        ElMessage.error('请求的资源不存在');
        return '请求的资源不存在';

      case 409: // Conflict
        ElMessage.error('操作冲突，可能是数据已被修改');
        return '操作冲突，可能是数据已被修改';

      case 422: // Unprocessable Entity
        ElMessage.error('请求参数验证失败');
        return '请求参数验证失败';

      case 429: // Too Many Requests
        ElMessage.error('请求过于频繁，请稍后再试');
        return '请求过于频繁，请稍后再试';

      case 500: // Internal Server Error
        ElMessage.error('服务器内部错误');
        return '服务器内部错误';

      default:
        ElMessage.error(`请求失败 (${status})`);
        return `请求失败 (${status})`;
    }
  }

  // 网络错误和超时错误处理
  if (isApiError(error)) {
    if (error.message && error.message.includes('Network Error')) {
      ElMessage.error('网络错误，请检查您的网络连接');
      return '网络错误，请检查您的网络连接';
    }

    if (error.message && error.message.includes('timeout')) {
      ElMessage.error('请求超时，请稍后再试');
      return '请求超时，请稍后再试';
    }
  }

  // 使用默认错误消息
  ElMessage.error(defaultMessage);
  return defaultMessage;
}

/**
 * 从错误对象中提取特定字段的错误信息
 * @param error 错误对象
 * @param fieldName 字段名称
 * @returns 字段的错误信息或null
 */
export function getFieldError(error: unknown, fieldName: string): string | null {
  if (
    isApiError(error) &&
    error.response &&
    error.response.data &&
    typeof error.response.data === 'object' &&
    error.response.data !== null &&
    fieldName in error.response.data
  ) {
    const fieldErrors = (error.response.data as Record<string, unknown>)[fieldName];
    if (Array.isArray(fieldErrors)) {
      return fieldErrors.join(', ');
    }
    return String(fieldErrors);
  }
  return null;
}

/**
 * 检查是否是特定字段的错误
 * @param error Axios错误对象
 * @param fieldName 字段名称
 * @returns 是否是该字段的错误
 */
export function isFieldError(error: unknown, fieldName: string): boolean {
  return getFieldError(error, fieldName) !== null;
}
