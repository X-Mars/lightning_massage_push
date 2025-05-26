import { defineStore } from 'pinia';
import type { Template } from '../types/index';
import { templateApi } from '../api';
import { ElMessage } from 'element-plus';

interface TemplateState {
  templates: Template[];
  currentTemplate: Template | null;
  loading: boolean;
}

export const useTemplateStore = defineStore('template', {
  state: (): TemplateState => ({
    templates: [],
    currentTemplate: null,
    loading: false
  }),
  
  actions: {
    async fetchTemplates(params = {}) {
      this.loading = true;
      try {
        const response = await templateApi.getTemplates(params);
        // 处理分页数据
        if (response.data.results) {
          this.templates = response.data.results;
          return {
            total: response.data.count,
            results: response.data.results
          };
        } else {
          // 如果没有分页，直接使用数据
          this.templates = response.data;
          return {
            total: response.data.length,
            results: response.data
          };
        }
      } catch (error) {
        console.error('获取模板列表失败:', error);
        ElMessage.error('获取模板列表失败');
        return { total: 0, results: [] };
      } finally {
        this.loading = false;
      }
    },
    
    async fetchTemplateById(id: number) {
      this.loading = true;
      try {
        const response = await templateApi.getTemplate(id);
        this.currentTemplate = response.data;
        return response.data;
      } catch (error) {
        console.error(`获取模板[ID=${id}]失败:`, error);
        ElMessage.error('获取模板详情失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async createTemplate(templateData: Partial<Template>) {
      this.loading = true;
      try {
        const response = await templateApi.createTemplate(templateData);
        ElMessage.success('创建模板成功');
        // 添加到列表中
        this.templates.push(response.data);
        return response.data;
      } catch (error) {
        console.error('创建模板失败:', error);
        ElMessage.error('创建模板失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async updateTemplate(id: number, templateData: Partial<Template>) {
      this.loading = true;
      try {
        const response = await templateApi.updateTemplate(id, templateData);
        ElMessage.success('更新模板成功');
        // 更新列表中的数据
        const index = this.templates.findIndex(t => t.id === id);
        if (index !== -1) {
          this.templates[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error(`更新模板[ID=${id}]失败:`, error);
        ElMessage.error('更新模板失败');
        return null;
      } finally {
        this.loading = false;
      }
    },
    
    async deleteTemplate(id: number) {
      this.loading = true;
      try {
        await templateApi.deleteTemplate(id);
        ElMessage.success('删除模板成功');
        // 从列表中移除
        this.templates = this.templates.filter(t => t.id !== id);
        return true;
      } catch (error) {
        console.error(`删除模板[ID=${id}]失败:`, error);
        ElMessage.error('删除模板失败');
        return false;
      } finally {
        this.loading = false;
      }
    }
  }
});