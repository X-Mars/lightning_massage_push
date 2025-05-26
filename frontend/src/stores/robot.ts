import { defineStore } from 'pinia';
import type { Robot } from '../types/index';
import { robotApi } from '../api';
import { ElMessage } from 'element-plus';

interface RobotState {
  robots: Robot[];
  currentRobot: Robot | null;
  loading: boolean;
}

export const useRobotStore = defineStore('robot', {
  state: (): RobotState => ({
    robots: [],
    currentRobot: null,
    loading: false
  }),
  
  actions: {
    async fetchRobots(params = {}) {
      this.loading = true;
      try {
        const response = await robotApi.getRobots(params);
        console.log('机器人API响应:', response);
        
        // 处理分页数据
        if (response.data && response.data.results && Array.isArray(response.data.results)) {
          // 后端启用了分页
          this.robots = response.data.results;
          console.log('已更新机器人列表:', this.robots);
          return {
            total: response.data.count,
            results: response.data.results
          };
        } else if (response.data && Array.isArray(response.data)) {
          // 如果后端没有分页，直接使用数据
          this.robots = response.data;
          console.log('已更新机器人列表:', this.robots);
          return {
            total: response.data.length,
            results: response.data
          };
        } else {
          console.error('机器人数据格式错误:', response.data);
          ElMessage.error('获取机器人列表失败: 返回数据格式错误');
          return { total: 0, results: [] };
        }
      } catch (error) {
        console.error('获取机器人列表失败:', error);
        ElMessage.error('获取机器人列表失败');
        return { total: 0, results: [] };
      } finally {
        this.loading = false;
      }
    },
    
    async fetchRobotById(id: number) {
      this.loading = true;
      try {
        const response = await robotApi.getRobot(id);
        this.currentRobot = response.data;
        return response.data;
      } catch (error) {
        console.error(`获取机器人[ID=${id}]失败:`, error);
        ElMessage.error('获取机器人详情失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async createRobot(robotData: Partial<Robot>) {
      this.loading = true;
      try {
        const response = await robotApi.createRobot(robotData);
        ElMessage.success('创建机器人成功');
        // 添加到列表中
        this.robots.push(response.data);
        return response.data;
      } catch (error) {
        console.error('创建机器人失败:', error);
        ElMessage.error('创建机器人失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async updateRobot(id: number, robotData: Partial<Robot>) {
      this.loading = true;
      try {
        const response = await robotApi.updateRobot(id, robotData);
        ElMessage.success('更新机器人成功');
        // 更新列表中的数据
        const index = this.robots.findIndex(r => r.id === id);
        if (index !== -1) {
          this.robots[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error(`更新机器人[ID=${id}]失败:`, error);
        ElMessage.error('更新机器人失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async deleteRobot(id: number) {
      this.loading = true;
      try {
        await robotApi.deleteRobot(id);
        ElMessage.success('删除机器人成功');
        // 从列表中移除
        this.robots = this.robots.filter(r => r.id !== id);
        return true;
      } catch (error) {
        console.error(`删除机器人[ID=${id}]失败:`, error);
        ElMessage.error('删除机器人失败');
        return false;
      } finally {
        this.loading = false;
      }
    }
  }
});