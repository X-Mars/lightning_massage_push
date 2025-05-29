<template>
  <div class="api-list-container">
    <el-card class="api-card">
      <template #header>
        <div class="card-header">
          <h3>基本消息接口</h3>
          <div>
            <el-tooltip content="刷新数据" placement="top">
              <el-button @click="fetchData" :loading="loading">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </template>
      
      <div v-loading="loading">
        <!-- 按机器人分组展示 -->
        <div v-if="robotGroups.length > 0">
          <div v-for="group in robotGroups" :key="group.robot_type" class="robot-group">
            <div class="group-header">
              <h4>{{ getRobotTypeName(group.robot_type) }}</h4>
              <el-tag :type="getRobotTypeTagType(group.robot_type)" size="small">
                {{ group.robots.length }} 个机器人
              </el-tag>
            </div>
            
            <div v-for="robot in group.robots" :key="robot.id" class="robot-section">
              <div class="robot-header">
                <h5>{{ robot.name }}</h5>
              </div>
              
              <el-table
                :data="getTemplatesForRobot(robot, group.templates)"
                stripe
                border
                size="small"
                style="width: 100%"
              >
                <el-table-column prop="template_name" label="模板名称" min-width="180" />
                <el-table-column prop="robot_name" label="机器人名称" width="150" />
                <el-table-column label="接口地址 (点击复制)" min-width="400">
                  <template #default="scope">
                    <el-tabs type="border-card" class="api-tabs">
                      <el-tab-pane label="ID模式">
                        <div class="api-url-container">
                          <div 
                            class="api-url-text api-url-clickable"
                            @click="copyApiUrl(scope.row.template_id, scope.row.robot_id)"
                            title="点击复制接口地址"
                          >
                            {{ getApiUrl(scope.row.template_id, scope.row.robot_id) }}
                          </div>
                        </div>
                      </el-tab-pane>
                      <el-tab-pane label="名称模式">
                        <div class="api-url-container">
                          <div 
                            class="api-url-text api-url-clickable name-mode"
                            @click="copyApiUrlByName(scope.row.template_id)"
                            title="点击复制接口地址"
                          >
                            {{ getApiUrlByName(scope.row.template_id) }}
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="showApiDocs(scope.row.template_id, scope.row.robot_id)" 
                      plain
                    >
                      查看文档
                    </el-button>
                    <el-button 
                      type="success" 
                      size="small" 
                      @click="testApi(scope.row.template_id, scope.row.robot_id)" 
                      plain
                    >
                      测试接口
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无可用的消息接口" />
      </div>
    </el-card>

    <!-- API文档对话框 -->
    <el-dialog v-model="showDocsDialog" :title="`API文档 - ${currentTemplateInfo?.name}`" width="800px">
      <div v-if="currentTemplateInfo">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="接口地址">
            <code class="api-code">{{ currentApiUrl }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="请求方法">
            <el-tag type="success">POST</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="内容类型">
            <code>application/json</code>
          </el-descriptions-item>
          <el-descriptions-item label="模板内容" span="2">
            <pre class="template-content">{{ currentTemplateInfo.content }}</pre>
          </el-descriptions-item>
        </el-descriptions>

        <div class="docs-section">
          <h4>请求参数</h4>
          <el-table :data="requestParams" border size="small">
            <el-table-column prop="name" label="参数名" width="150" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="required" label="必填" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.required ? 'danger' : 'info'" size="small">
                  {{ scope.row.required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
          </el-table>
        </div>

        <div class="docs-section">
          <h4>请求示例</h4>
          <pre class="code-block">{{ requestExample }}</pre>
        </div>

        <div class="docs-section">
          <h4>响应示例</h4>
          <pre class="code-block">{{ responseExample }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- API测试对话框 -->
    <el-dialog v-model="showTestDialog" :title="`测试API - ${currentTemplateInfo?.name}`" width="600px">
      <div v-if="currentTemplateInfo">
        <el-form :model="testForm" label-width="100px">
          <el-form-item label="接口地址">
            <el-input v-model="currentApiUrl" disabled />
          </el-form-item>
          <el-form-item label="请求数据">
            <el-input 
              v-model="testForm.data"
              type="textarea"
              :rows="8"
              placeholder="请输入JSON格式的请求数据"
            />
          </el-form-item>
        </el-form>
        
        <div v-if="testResult" class="test-result">
          <h4>测试结果</h4>
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? '请求成功' : '请求失败'"
            show-icon
          />
          <pre class="result-content">{{ testResult.response }}</pre>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTestDialog = false">取消</el-button>
          <el-button type="primary" @click="executeTest" :loading="testLoading">
            发送测试
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import { robotApi, templateApi } from '../../api';
import type { Robot, Template } from '../../types';

// 响应式数据
const loading = ref(false);
const showDocsDialog = ref(false);
const showTestDialog = ref(false);
const testLoading = ref(false);
const robots = ref<Robot[]>([]);
const templates = ref<Template[]>([]);
const currentTemplateId = ref<number | null>(null);
const currentRobotId = ref<number | null>(null);
const currentApiUrl = ref('');
const currentTemplateInfo = ref<Template | null>(null);
const testResult = ref<any>(null);

// 表单数据
const testForm = reactive({
  data: ''
});

// 计算属性 - 按机器人类型分组
const robotGroups = computed(() => {
  const groups = new Map();
  
  robots.value.forEach(robot => {
    if (!groups.has(robot.robot_type)) {
      groups.set(robot.robot_type, {
        robot_type: robot.robot_type,
        robots: [],
        templates: templates.value.filter(t => t.robot_type === robot.robot_type)
      });
    }
    groups.get(robot.robot_type).robots.push(robot);
  });
  
  return Array.from(groups.values());
});

// API参数定义
const requestParams = [
  { name: 'title', type: 'string', required: false, description: '消息标题（可选）' },
  { name: 'content', type: 'string', required: true, description: '消息内容' },
  { name: 'robot_name', type: 'string', required: false, description: '机器人名称（名称模式时必填）' }
];

const requestExample = `{
  "title": "系统告警",
  "content": "服务器CPU使用率过高",
  "robot_name": "运维告警机器人"
}`;

const responseExample = `{
  "success": true,
  "message": "消息发送成功",
  "data": {
    "message_id": 123,
    "sent_at": "2023-12-07T10:30:00Z"
  }
}`;

// 工具方法
const getRobotTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'wechat': '企业微信',
    'feishu': '飞书',
    'dingtalk': '钉钉'
  };
  return typeMap[type] || type;
};

const getRobotTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    'wechat': 'success',
    'feishu': 'warning',
    'dingtalk': 'info'
  };
  return typeMap[type] || 'info';
};

const getTemplatesForRobot = (robot: Robot, templates: Template[]) => {
  return templates.map(template => ({
    template_id: template.id,
    template_name: template.name,
    robot_id: robot.id,
    robot_name: robot.name,
    robot_type: robot.robot_type
  }));
};

// URL生成方法
const getApiUrl = (templateId: number, robotId: number) => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/api/public/push/${templateId}/${robotId}/`;
};

const getApiUrlByName = (templateId: number) => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/api/public/push/${templateId}/`;
};

// 数据获取方法
const fetchData = async () => {
  loading.value = true;
  try {
    const [robotsResponse, templatesResponse] = await Promise.all([
      robotApi.getRobots(),
      templateApi.getTemplates()
    ]);
    
    robots.value = robotsResponse.data.results || robotsResponse.data;
    templates.value = templatesResponse.data.results || templatesResponse.data;
  } catch (error) {
    console.error('获取数据失败:', error);
    ElMessage.error('获取数据失败');
  } finally {
    loading.value = false;
  }
};

// 复制URL方法
const copyApiUrl = async (templateId: number, robotId: number) => {
  try {
    const url = getApiUrl(templateId, robotId);
    await navigator.clipboard.writeText(url);
    ElMessage.success('接口地址已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

const copyApiUrlByName = async (templateId: number) => {
  try {
    const url = getApiUrlByName(templateId);
    await navigator.clipboard.writeText(url);
    ElMessage.success('接口地址已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

// 获取模板信息
const fetchTemplateInfo = async (templateId: number) => {
  try {
    const response = await templateApi.getTemplate(templateId);
    return response.data;
  } catch (error) {
    console.error('获取模板信息失败:', error);
    return null;
  }
};

// 显示API文档
const showApiDocs = async (templateId: number, robotId: number) => {
  currentTemplateId.value = templateId;
  currentRobotId.value = robotId;
  currentApiUrl.value = getApiUrl(templateId, robotId);
  
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    currentTemplateInfo.value = info;
    showDocsDialog.value = true;
  }
};

// 测试API
const testApi = async (templateId: number, robotId: number) => {
  currentTemplateId.value = templateId;
  currentRobotId.value = robotId;
  currentApiUrl.value = getApiUrl(templateId, robotId);
  
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    currentTemplateInfo.value = info;
    testForm.data = JSON.stringify({
      title: "测试消息",
      content: "这是一条测试消息"
    }, null, 2);
    testResult.value = null;
    showTestDialog.value = true;
  }
};

// 执行测试
const executeTest = async () => {
  if (!testForm.data.trim()) {
    ElMessage.error('请输入测试数据');
    return;
  }

  testLoading.value = true;
  try {
    const data = JSON.parse(testForm.data);
    const response = await fetch(currentApiUrl.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    testResult.value = {
      success: response.ok,
      response: JSON.stringify(result, null, 2)
    };
  } catch (error) {
    testResult.value = {
      success: false,
      response: `请求失败: ${error}`
    };
  } finally {
    testLoading.value = false;
  }
};

// 生命周期
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.api-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.robot-group {
  margin-bottom: 30px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.group-header h4 {
  margin: 0;
  color: #303133;
}

.robot-section {
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
}

.robot-header {
  padding: 12px 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.robot-header h5 {
  margin: 0;
  color: #606266;
  font-weight: 500;
}

.api-tabs {
  margin: 0;
}

.api-url-container {
  padding: 8px;
}

.api-url-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  background-color: #f6f8fa;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #d1d9e0;
  word-break: break-all;
}

.api-url-clickable {
  cursor: pointer;
  transition: all 0.3s ease;
}

.api-url-clickable:hover {
  background-color: #e1f3ff;
  border-color: #409eff;
  color: #409eff;
}

.name-mode {
  background-color: #f0f9ff;
  border-color: #91d5ff;
}

.docs-section {
  margin-top: 20px;
}

.docs-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.template-content {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  margin: 0;
}

.code-block {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  border: 1px solid #d1d9e0;
  margin: 0;
  overflow-x: auto;
}

.api-code {
  background-color: #f6f8fa;
  padding: 4px 8px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
}

.test-result {
  margin-top: 20px;
}

.result-content {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  margin-top: 10px;
  border: 1px solid #d1d9e0;
  max-height: 300px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
