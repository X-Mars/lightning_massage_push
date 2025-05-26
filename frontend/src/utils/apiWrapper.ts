/**
 * API请求包装器
 * 为所有API请求添加统一的错误处理
 */
import { handleApiError } from '../utils/errorHandler';

/**
 * 包装API调用，添加统一的错误处理
 * @param apiCall API调用函数
 * @param errorMessage 错误消息
 * @returns API调用结果
 */
export async function withErrorHandling<T>(
  apiCall: () => Promise<T>, 
  errorMessage: string = '请求失败'
): Promise<T | { error: true, message: string }> {
  try {
    return await apiCall();
  } catch (error: any) {
    // 使用错误处理工具处理错误
    const message = handleApiError(error, errorMessage);
    return {
      error: true,
      message
    };
  }
}

/**
 * 使用示例:
 * 
 * // 原始API调用
 * try {
 *   const result = await api.getData();
 *   // 处理结果
 * } catch (error) {
 *   // 处理错误
 * }
 * 
 * // 使用包装器
 * const result = await withErrorHandling(() => api.getData(), '获取数据失败');
 * if (!result.error) {
 *   // 处理成功结果
 * }
 */
