<template>
  <div class="api-list-container">
    <el-card class="api-card">
      <template #header>
        <div class="card-header">
          <h3>消息接口</h3>
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
                <el-table-column label="接口地址 (点击复制)" min-width="380">
                  <template #default="scope">
                    <div class="api-url-container">
                      <div 
                        class="api-url-text api-url-clickable"
                        @click="copyApiUrl(scope.row.template_id, scope.row.robot_id)"
                        title="点击复制接口地址"
                      >
                        {{ getApiUrl(scope.row.template_id, scope.row.robot_id) }}
                      </div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="showApiDocs(scope.row.template_id)" 
                      plain
                    >
                      <el-icon><InfoFilled /></el-icon>
                      接口说明
                    </el-button>
                    <el-button 
                      type="success" 
                      size="small" 
                      @click="testApi(scope.row.template_id, scope.row.robot_id)" 
                      plain
                    >
                      <el-icon><Connection /></el-icon>
                      测试
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
        
        <!-- 空状态展示 -->
        <el-empty v-else description="暂无数据，请先创建机器人和模板" />
      </div>
    </el-card>
    
    <!-- 接口文档对话框 -->
    <el-dialog
      v-model="docsDialogVisible"
      title="接口文档"
      width="60%"
    >
      <div class="api-docs-container" v-if="currentTemplateInfo">
        <div class="docs-section">
          <h4>基本信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="模板名称">{{ currentTemplateInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="模板描述">{{ currentTemplateInfo.description }}</el-descriptions-item>
            <el-descriptions-item label="适用机器人">{{ currentTemplateInfo.robot_type_name }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="docs-section">
          <h4>接口地址 (点击复制)</h4>
          <div class="api-url-box">
            <div class="api-url-clickable" @click="copyCurrentApiUrl" title="点击复制接口地址">POST {{ currentApiUrl }}</div>
          </div>
        </div>
        
        <div class="docs-section">
          <h4>请求参数</h4>
          <div class="params-list">
            <p>请求体格式: JSON</p>
            <div class="variables-container" v-if="currentTemplateInfo.variables.length > 0">
              <p>必须包含以下变量:</p>
              <el-tag 
                v-for="variable in currentTemplateInfo.variables" 
                :key="variable"
                class="variable-tag"
              >
                {{ variable }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="docs-section">
          <h4>请求示例 (点击复制)</h4>
          <div class="example-box">
            <pre class="example-code api-url-clickable" @click="copyExampleJson" title="点击复制示例JSON">{{ JSON.stringify(currentTemplateInfo.example_json, null, 2) }}</pre>
          </div>
        </div>
        
        <div class="docs-section">
          <h4>响应示例</h4>
          <div class="example-box">
            <pre class="example-code">// 成功响应
{
  "message": "消息推送成功"
}

// 失败响应
{
  "error": "错误信息"
}</pre>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 测试接口对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试接口"
      width="60%"
    >
      <div class="test-api-container" v-if="currentTemplateInfo">
        <div class="test-section">
          <h4>接口地址 (点击复制)</h4>
          <div class="api-url-box">
            <div class="api-url-clickable" @click="copyCurrentApiUrl" title="点击复制接口地址">POST {{ currentApiUrl }}</div>
          </div>
        </div>
        
        <div class="test-section">
          <h4>请求参数</h4>
          <el-input
            v-model="testRequestData"
            type="textarea"
            :rows="10"
            placeholder="请输入JSON格式的请求参数"
          />
        </div>
        
        <div class="test-section">
          <h4>测试结果</h4>
          <div class="test-result" v-loading="testLoading">
            <pre v-if="testResult" class="result-code">{{ JSON.stringify(testResult, null, 2) }}</pre>
            <el-empty v-else description="暂无测试结果" />
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="runApiTest" :loading="testLoading">
            发送请求
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useTemplateStore } from '../../stores/template';
import { useRobotStore } from '../../stores/robot';
import { RobotType, RobotTypeNames } from '../../types';
import type { Template, Robot } from '../../types';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import useClipboard from 'vue-clipboard3';
import { 
  Refresh, 
  InfoFilled, 
  Connection 
} from '@element-plus/icons-vue';

// 存储
const templateStore = useTemplateStore();
const robotStore = useRobotStore();
const loading = ref(false);

// 初始化剪贴板
const { toClipboard } = useClipboard();

// 数据
const templates = ref<Template[]>([]);
const robots = ref<Robot[]>([]);

// 分组后的数据
interface TemplateItem {
  template_id: number;
  template_name: string;
  robot_id: number;
  robot_name: string;
}

interface RobotGroup {
  robot_type: RobotType;
  robots: Robot[];
  templates: Template[];
  items?: TemplateItem[];
}

const robotGroups = ref<RobotGroup[]>([]);

// 接口文档对话框
const docsDialogVisible = ref(false);
const currentTemplateId = ref<number | null>(null);
const currentRobotId = ref<number | null>(null);
const currentTemplateInfo = ref<any>(null);
const currentApiUrl = ref('');

// 测试接口对话框
const testDialogVisible = ref(false);
const testRequestData = ref('');
const testResult = ref<any>(null);
const testLoading = ref(false);

// 获取机器人类型标签样式
const getRobotTypeTagType = (type: RobotType) => {
  switch (type) {
    case RobotType.WECHAT:
      return 'success';
    case RobotType.FEISHU:
      return 'primary';
    case RobotType.DINGTALK:
      return 'warning';
    default:
      return 'info';
  }
};

// 获取机器人类型名称
const getRobotTypeName = (type: RobotType) => {
  return RobotTypeNames[type] || '未知类型';
};

// 获取特定机器人可用的模板列表
const getTemplatesForRobot = (robot: Robot, templates: Template[]) => {
  const matchingTemplates = templates.filter(t => t.robot_type === robot.robot_type);
  return matchingTemplates.map(template => ({
    template_id: template.id,
    template_name: template.name,
    robot_id: robot.id,
    robot_name: robot.name
  }));
};

// 获取API地址
const getApiUrl = (templateId: number, robotId: number) => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/api/public/push/${templateId}/${robotId}/`;
};

// 复制API地址
const copyApiUrl = async (templateId: number, robotId: number) => {
  try {
    const url = getApiUrl(templateId, robotId);
    await toClipboard(url);
    ElMessage.success('接口地址已复制到剪贴板');
  } catch (e) {
    console.error('复制失败', e);
    ElMessage.error('复制失败，请手动复制');
  }
};

// 获取模板信息
const fetchTemplateInfo = async (templateId: number) => {
  try {
    const baseUrl = window.location.origin;
    const response = await axios.get(`${baseUrl}/api/templates/${templateId}/info/`);
    return response.data;
  } catch (error) {
    ElMessage.error('获取模板信息失败');
    console.error('获取模板信息失败:', error);
    return null;
  }
};

// 显示API文档
const showApiDocs = async (templateId: number) => {
  currentTemplateId.value = templateId;
  currentApiUrl.value = getApiUrl(templateId, 0).replace('/0/', '/[robot_id]/');
  
  // 获取模板信息
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    currentTemplateInfo.value = info;
    docsDialogVisible.value = true;
  }
};

// 复制当前API地址
const copyCurrentApiUrl = async () => {
  try {
    await toClipboard(currentApiUrl.value);
    ElMessage.success('接口地址已复制到剪贴板');
  } catch (e) {
    console.error('复制失败', e);
    ElMessage.error('复制失败，请手动复制');
  }
};

// 复制示例JSON
const copyExampleJson = async () => {
  if (currentTemplateInfo.value) {
    try {
      const jsonStr = JSON.stringify(currentTemplateInfo.value.example_json, null, 2);
      await toClipboard(jsonStr);
      ElMessage.success('示例JSON已复制到剪贴板');
    } catch (e) {
      console.error('复制失败', e);
      ElMessage.error('复制失败，请手动复制');
    }
  }
};

// 测试API
const testApi = async (templateId: number, robotId: number) => {
  currentTemplateId.value = templateId;
  currentRobotId.value = robotId;
  currentApiUrl.value = getApiUrl(templateId, robotId);
  
  // 获取模板信息
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    currentTemplateInfo.value = info;
    testRequestData.value = JSON.stringify(info.example_json, null, 2);
    testResult.value = null;
    testDialogVisible.value = true;
  }
};

// 运行API测试
const runApiTest = async () => {
  if (!currentTemplateId.value || !currentRobotId.value) {
    ElMessage.error('模板或机器人ID无效');
    return;
  }
  
  testLoading.value = true;
  
  try {
    // 解析JSON数据
    const requestData = JSON.parse(testRequestData.value);
    
    // 发送请求
    const response = await axios.post(
      currentApiUrl.value,
      requestData
    );
    
    testResult.value = response.data;
    ElMessage.success('测试请求已发送');
  } catch (error: any) {
    console.error('API测试失败:', error);
    if (error.response) {
      // 服务器返回的错误
      testResult.value = error.response.data;
    } else if (error.request) {
      // 请求未收到响应
      testResult.value = { error: '未收到服务器响应' };
    } else {
      // JSON解析错误或其他错误
      testResult.value = { error: error.message || '请求失败' };
    }
    ElMessage.error('测试失败');
  } finally {
    testLoading.value = false;
  }
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  
  try {
    // 获取模板和机器人数据
    await Promise.all([
      templateStore.fetchTemplates(),
      robotStore.fetchRobots()
    ]);
    
    templates.value = templateStore.templates;
    robots.value = robotStore.robots;
    
    // 按机器人类型分组
    const groups: Record<string, RobotGroup> = {};
    
    // 创建机器人类型分组
    robots.value.forEach(robot => {
      const typeStr = robot.robot_type.toString();
      if (!groups[typeStr]) {
        groups[typeStr] = {
          robot_type: robot.robot_type,
          robots: [],
          templates: []
        };
      }
      groups[typeStr].robots.push(robot);
    });
    
    // 将模板放入对应分组
    templates.value.forEach(template => {
      const typeStr = template.robot_type.toString();
      if (groups[typeStr]) {
        groups[typeStr].templates.push(template);
      }
    });
    
    // 转换为数组
    robotGroups.value = Object.values(groups);
    
    console.log('数据加载完成，分组:', robotGroups.value);
    
  } catch (error) {
    console.error('获取数据失败:', error);
    ElMessage.error('加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.api-list-container {
  padding: 0;
  width: 100%;
}

.api-card {
  margin: 0;
  width: 100%;
  border-radius: 0;
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
  margin-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.group-header h4 {
  margin: 0;
  margin-right: 10px;
}

.robot-section {
  margin-bottom: 20px;
}

.robot-header {
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.robot-header h5 {
  margin: 0;
  color: #606266;
}

.api-url-container {
  display: flex;
  align-items: center;
  width: 100%;
}

.api-url-text {
  flex: 1;
  font-size: 12px;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.api-url-clickable {
  cursor: pointer;
  transition: all 0.3s;
  border: 1px dashed transparent;
  color: #606266;
}

.api-url-clickable:hover {
  background-color: #e6f1fc;
  text-decoration: underline;
  border-color: #409EFF;
  color: #409EFF;
}

.example-code.api-url-clickable {
  cursor: pointer;
  transition: all 0.3s;
  border: 1px dashed transparent;
}

.example-code.api-url-clickable:hover {
  background-color: #e6f1fc;
  border-color: #409EFF;
}

.api-url-box {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: monospace;
  overflow-x: auto;
}

.api-url-box .api-url-clickable {
  cursor: pointer;
  transition: all 0.3s;
  font-family: monospace;
  padding: 5px;
  border-radius: 3px;
  border: 1px dashed transparent;
}

.api-url-box .api-url-clickable:hover {
  background-color: #e6f1fc;
  text-decoration: underline;
  border-color: #409EFF;
  color: #409EFF;
}

.variables-container {
  margin: 10px 0;
}

.variable-tag {
  margin: 5px;
}

.example-box {
  position: relative;
}

.example-code, .result-code {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.example-box .el-button {
  position: absolute;
  top: 10px;
  right: 10px;
}

.test-result {
  min-height: 100px;
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.docs-section, .test-section {
  margin-bottom: 20px;
}

.docs-section h4, .test-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}
</style>
