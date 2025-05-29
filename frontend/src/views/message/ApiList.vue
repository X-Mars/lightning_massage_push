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
                      <el-tab-pane label="名称模式" v-if="scope.row.robot_english_name">
                        <div class="api-url-container">
                          <div 
                            class="api-url-text api-url-clickable"
                            @click="copyApiUrlByName(scope.row.template_id, scope.row.robot_english_name)"
                            title="点击复制接口地址"
                          >
                            {{ getApiUrl(scope.row.template_id, 0, scope.row.robot_english_name) }}
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
                      @click="showApiDocs(scope.row.template_id)" 
                      plain
                    >
                      <el-icon><InfoFilled /></el-icon>
                      接口说明
                    </el-button>
                    <el-dropdown trigger="click" @command="(command) => handleTestCommand(command, scope.row)">
                      <el-button 
                        type="success" 
                        size="small" 
                        plain
                      >
                        <el-icon><Connection /></el-icon>
                        测试
                        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="id">ID模式测试</el-dropdown-item>
                          <el-dropdown-item command="name" v-if="scope.row.robot_english_name">名称模式测试</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>

        <!-- 高级分发接口分组 -->
        <div class="distribution-group" v-if="templates.length > 0">
          <div class="group-header">
            <h4>
              <el-icon><Operation /></el-icon>
              高级分发接口
            </h4>
            <el-tag type="warning" size="small">
              智能分发
            </el-tag>
          </div>
          
          <div class="distribution-section">
            <div class="distribution-header">
              <h5>分发推送接口</h5>
              <p class="description">根据告警数据自动分发到对应的机器人通道</p>
            </div>
            
            <el-table
              :data="getDistributionTemplates()"
              stripe
              border
              size="small"
              style="width: 100%"
            >
              <el-table-column prop="template_name" label="模板名称" min-width="180" />
              <el-table-column prop="robot_type_name" label="适用机器人类型" width="150" />
              <el-table-column label="分发接口地址 (点击复制)" min-width="400">
                <template #default="scope">
                  <div class="api-url-container">
                    <div 
                      class="api-url-text api-url-clickable distribution-url"
                      @click="copyDistributionUrl(scope.row.template_id)"
                      title="点击复制分发接口地址"
                    >
                      {{ getDistributionUrl(scope.row.template_id) }}
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="scope">
                  <el-button 
                    type="warning" 
                    size="small" 
                    @click="showDistributionDocs(scope.row.template_id)" 
                    plain
                  >
                    <el-icon><InfoFilled /></el-icon>
                    分发说明
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small" 
                    @click="testDistributionApi(scope.row.template_id)"
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
            <el-descriptions-item label="适用机器人">{{ currentTemplateInfo.robot_type_name }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="docs-section">
          <h4>接口地址 (点击复制)</h4>
          <el-tabs type="border-card">
            <el-tab-pane label="ID模式">
              <div class="api-url-box">
                <div class="api-url-clickable" @click="copyCurrentApiUrl" title="点击复制接口地址">POST {{ currentApiUrl }}</div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="名称模式">
              <div class="api-url-box">
                <div class="api-url-clickable" @click="copyCurrentApiUrlByName" title="点击复制接口地址">
                  POST {{ currentApiUrlByName }}
                </div>
              </div>
              <div class="api-note">
                <p>
                  <el-icon><InfoFilled /></el-icon> 
                  <strong>说明：</strong>名称模式使用机器人的英文名称作为参数，适用于不方便记忆机器人ID的场景。
                </p>
              </div>
            </el-tab-pane>
          </el-tabs>
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
          <h4>接口信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="接口类型">
              <el-tag :type="currentTestMode === 'name' ? 'success' : 'primary'">
                {{ currentTestMode === 'name' ? '名称模式' : 'ID模式' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="接口地址">
              <div class="api-url-box">
                <div class="api-url-clickable" @click="copyCurrentApiUrl" title="点击复制接口地址">
                  POST {{ currentApiUrl }}
                </div>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="说明" v-if="currentTestMode === 'name'">
              使用机器人英文名称作为参数，无需记忆机器人ID
            </el-descriptions-item>
            <el-descriptions-item label="说明" v-else>
              使用机器人ID作为路径参数，传统调用方式
            </el-descriptions-item>
          </el-descriptions>
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
  Connection,
  ArrowDown,
  Operation
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
const currentApiUrlByName = ref('');

// 测试接口对话框
const testDialogVisible = ref(false);
const testRequestData = ref('');
const testResult = ref<any>(null);
const testLoading = ref(false);
const currentTestMode = ref<'id' | 'name' | 'distribution'>('id'); // 'id'、'name' 或 'distribution'

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
    robot_name: robot.name,
    robot_english_name: robot.english_name || ''
  }));
};

// 获取API地址
const getApiUrl = (templateId: number, robotId: number, robotEnglishName?: string) => {
  const baseUrl = window.location.origin;
  
  // 如果提供了英文名称，则使用英文名称形式的URL
  if (robotEnglishName) {
    return `${baseUrl}/api/public/push/${templateId}/?robot_english_name=${robotEnglishName}`;
  }
  
  // 否则使用ID形式的URL
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

// 复制通过名称访问的API地址
const copyApiUrlByName = async (templateId: number, robotEnglishName: string) => {
  try {
    const url = getApiUrl(templateId, 0, robotEnglishName);
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
  
  // 设置两种API URL格式
  currentApiUrl.value = getApiUrl(templateId, 0).replace('/0/', '/[robot_id]/');
  currentApiUrlByName.value = getApiUrl(templateId, 0, '[robot_english_name]');
  
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

// 复制当前通过名称访问的API地址
const copyCurrentApiUrlByName = async () => {
  try {
    await toClipboard(currentApiUrlByName.value);
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

// === 分发接口相关方法 ===

// 获取分发模板列表
const getDistributionTemplates = () => {
  return templates.value.map(template => ({
    template_id: template.id,
    template_name: template.name,
    robot_type_name: getRobotTypeName(template.robot_type)
  }));
};

// 获取分发接口地址
const getDistributionUrl = (templateId: number) => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/api/public/distribution/push/${templateId}/`;
};

// 复制分发接口地址
const copyDistributionUrl = async (templateId: number) => {
  try {
    const url = getDistributionUrl(templateId);
    await toClipboard(url);
    ElMessage.success('分发接口地址已复制到剪贴板');
  } catch (e) {
    console.error('复制失败', e);
    ElMessage.error('复制失败，请手动复制');
  }
};

// 显示分发接口文档
const showDistributionDocs = async (templateId: number) => {
  currentTemplateId.value = templateId;
  
  // 设置分发API URL
  currentApiUrl.value = getDistributionUrl(templateId);
  
  // 获取模板信息
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    // 为分发接口创建特殊的模板信息
    currentTemplateInfo.value = {
      ...info,
      name: `${info.name} (分发模式)`,
      robot_type_name: '智能分发',
      variables: ['alerts', 'instance_name', 'rule_name', ...info.variables],
      example_json: {
        receiver: "web\\.hook\\.prometheusalert",
        status: "firing",
        alerts: [
          {
            status: "firing",
            labels: {
              alertname: "HighCPUUsage",
              instance: "server-001",
              job: "node-exporter",
              severity: "warning"
            },
            annotations: {
              description: "CPU使用率超过80%",
              summary: "服务器CPU使用率过高"
            },
            startsAt: "2024-01-01T00:00:00.000Z",
            endsAt: "0001-01-01T00:00:00Z",
            generatorURL: "http://prometheus:9090/graph?g0.expr=...",
            fingerprint: "abc123def456"
          }
        ],
        groupLabels: {
          instance: "server-001"
        },
        commonLabels: {
          instance: "server-001",
          job: "node-exporter",
          severity: "warning"
        },
        commonAnnotations: {
          summary: "服务器CPU使用率过高"
        },
        externalURL: "http://alertmanager:9093",
        version: "4"
      }
    };
    docsDialogVisible.value = true;
  }
};

// 测试分发接口
const testDistributionApi = async (templateId: number) => {
  currentTemplateId.value = templateId;
  currentTestMode.value = 'distribution';
  
  // 设置分发API URL
  currentApiUrl.value = getDistributionUrl(templateId);
  
  // 获取模板信息
  const info = await fetchTemplateInfo(templateId);
  if (info) {
    currentTemplateInfo.value = {
      ...info,
      name: `${info.name} (分发测试)`
    };
    
    // 设置分发测试数据
    testRequestData.value = JSON.stringify({
      receiver: "web\\.hook\\.prometheusalert",
      status: "firing",
      alerts: [
        {
          status: "firing",
          labels: {
            alertname: "HighCPUUsage",
            instance: "server-001",
            job: "node-exporter",
            severity: "warning"
          },
          annotations: {
            description: "CPU使用率超过80%",
            summary: "服务器CPU使用率过高"
          },
          startsAt: "2024-01-01T00:00:00.000Z",
          endsAt: "0001-01-01T00:00:00Z"
        }
      ]
    }, null, 2);
    
    testResult.value = null;
    testDialogVisible.value = true;
  }
};

// 处理测试命令
const handleTestCommand = (command: string, row: any) => {
  if (command === 'id') {
    testApi(row.template_id, row.robot_id, undefined, 'id');
  } else if (command === 'name' && row.robot_english_name) {
    testApi(row.template_id, row.robot_id, row.robot_english_name, 'name');
  }
};

// 测试API
const testApi = async (templateId: number, robotId: number, robotEnglishName?: string, mode: 'id' | 'name' = 'id') => {
  currentTemplateId.value = templateId;
  currentRobotId.value = robotId;
  currentTestMode.value = mode;
  
  // 根据模式设置API URL
  if (mode === 'name' && robotEnglishName) {
    currentApiUrl.value = getApiUrl(templateId, 0, robotEnglishName);
  } else {
    currentApiUrl.value = getApiUrl(templateId, robotId);
  }
  
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

.distribution-group {
  margin-bottom: 30px;
  border: 2px dashed #f5a623;
  border-radius: 8px;
  padding: 20px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3d0 100%);
}

.distribution-section {
  margin-bottom: 20px;
}

.distribution-header {
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 3px solid #f5a623;
}

.distribution-header h5 {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.distribution-header .description {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 13px;
}

.distribution-url {
  background: linear-gradient(135deg, #fff2cc 0%, #ffe6a3 100%);
  border: 1px solid #f5a623;
}

.distribution-url:hover {
  background: linear-gradient(135deg, #ffe6a3 0%, #ffd966 100%);
  border-color: #e6940f;
  color: #bf7506;
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
