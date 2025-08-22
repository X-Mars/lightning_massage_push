import { defineStore } from 'pinia';
import type { MessageLog, PushMessageParams } from '../types/index';
import { logApi, pushApi } from '../api';
import { ElMessage } from 'element-plus';

interface MessageState {
  logs: MessageLog[];
  loading: boolean;
  pagination: {
    page: number;
    size: number;
    total: number;
  };
}

export const useMessageStore = defineStore('message', {
  state: (): MessageState => ({
    logs: [],
    loading: false,
    pagination: {
      page: 1,
      size: 10,
      total: 0,
    },
  }),

  actions: {
    async fetchLogs(page = 1, size = 10, extraParams = {}) {
      this.loading = true;
      try {
        // 合并页码参数和额外查询参数
        const params = { page, size, ...extraParams };
        // console.log('【Store】发送API请求参数:', params);

        const response = await logApi.getLogs(params);
        // console.log('【Store】API响应原始数据:', response);

        if (!response || !response.data) {
          // console.error('【Store】API响应缺少data属性');
          return { results: [], count: 0 };
        }

        // console.log('【Store】API响应数据:', response.data);

        // 检查响应数据格式
        if (!response.data.results && Array.isArray(response.data)) {
          // 如果response.data本身就是数组，可能是后端直接返回了结果数组
          // console.warn('【Store】API返回的是数组而非分页对象，尝试适配');
          this.logs = response.data;
          this.pagination = {
            page,
            size,
            total: response.data.length,
          };
          return { results: response.data, count: response.data.length };
        } else {
          // 标准响应结构
          this.logs = response.data.results || [];
          this.pagination = {
            page,
            size,
            total: response.data.count || 0,
          };
          return response.data;
        }
      } catch (_error) {
        // console.error('获取消息日志失败:', error);
        ElMessage.error('获取消息日志失败');
        return null;
      } finally {
        this.loading = false;
      }
    },

    async fetchLogById(id: number) {
      this.loading = true;
      try {
        const response = await logApi.getLog(id);
        return response.data;
      } catch (_error) {
        // console.error(`获取消息日志[ID=${id}]失败:`, error);
        ElMessage.error('获取消息日志详情失败');
        return null;
      } finally {
        this.loading = false;
      }
    },

    async pushMessage(params: PushMessageParams) {
      this.loading = true;
      try {
        const response = await pushApi.push(params);
        ElMessage.success('消息推送成功');
        return response.data;
      } catch (_error) {
        // console.error('消息推送失败:', error);
        ElMessage.error('消息推送失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
  },
});
