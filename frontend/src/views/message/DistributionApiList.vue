<template>
  <div class="distribution-api-container">
    <el-card class="api-card">
      <template #header>
        <div class="card-header">
          <h3>高级分发接口</h3>
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
        <!-- 分发接口说明 -->
        <el-alert 
          center
          type="info" 
          title="分发接口说明" 
          :closable="false"
          class="info-alert"
        >
          <template #default>
            <p>高级分发接口支持智能分发功能，可以根据告警数据自动选择合适的分发通道进行消息推送。</p>
            <ul>
              <li>支持多实例自动识别和分发</li>
              <li>支持规则匹配和动态路由</li>
              <li>支持批量告警处理</li>
              <li>支持自定义分发策略</li>
            </ul>
          </template>
        </el-alert>

        <!-- 分发接口信息 -->
        <el-card class="distribution-card" shadow="never">
          <div class="distribution-info">
            <div class="api-header">
              <h4>分发接口地址</h4>
              <el-button 
                type="primary" 
                size="small" 
                @click="copyDistributionUrl"
              >
                复制地址
              </el-button>
            </div>
            
            <div class="api-url-display">
              <code class="api-url">{{ distributionApiUrl }}</code>
            </div>

            <div class="api-details">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="请求方法">
                  <el-tag type="success">POST</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="内容类型">
                  <code>application/json</code>
                </el-descriptions-item>
                <el-descriptions-item label="支持格式">
                  <el-tag type="info">Prometheus AlertManager</el-tag>
                  <el-tag type="info" style="margin-left: 8px;">自定义JSON</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="分发策略">
                  <el-tag type="warning">自动匹配实例</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <!-- 分发通道统计 -->
        <el-card class="stats-card" shadow="never">
          <template #header>
            <h4>分发通道统计</h4>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总分发通道" :value="channelStats.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="活跃通道" :value="channelStats.active" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="配置实例" :value="channelStats.instances" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="支持类型" :value="channelStats.robotTypes" />
            </el-col>
          </el-row>
        </el-card>

        <!-- 分发通道列表 -->
        <el-card class="channels-card" shadow="never">
          <template #header>
            <div class="card-header">
              <h4>当前分发通道</h4>
              <el-button 
                type="primary" 
                size="small" 
                @click="$router.push('/distribution/channels')"
              >
                管理通道
              </el-button>
            </div>
          </template>
          
          <el-table :data="channels" stripe border>
            <el-table-column prop="name" label="通道名称" min-width="150" />
            <el-table-column prop="robot_name" label="绑定机器人" min-width="150" />
            <el-table-column prop="template_name" label="绑定模板" min-width="150" />
            <el-table-column prop="robot_type" label="机器人类型" width="120">
              <template #default="scope">
                <el-tag :type="getRobotTypeTagType(scope.row.robot_type)" size="small">
                  {{ getRobotTypeName(scope.row.robot_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                  {{ scope.row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column label="操作" width="100" align="center">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="testChannel(scope.row)"
                  plain
                >
                  测试
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty v-if="channels.length === 0" description="暂无分发通道，请先创建分发通道" />
        </el-card>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="showApiDocs">
            <el-icon><Document /></el-icon>
            查看接口文档
          </el-button>
          <el-button type="success" size="large" @click="testDistributionApi">
            <el-icon><Monitor /></el-icon>
            测试分发接口
          </el-button>
          <el-button type="warning" size="large" @click="viewExamples">
            <el-icon><DataLine /></el-icon>
            查看示例
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- API文档对话框 -->
    <el-dialog v-model="showDocsDialog" title="分发接口文档" width="900px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="接口说明" name="overview">
          <div class="docs-content">
            <h4>接口概述</h4>
            <p>高级分发接口是一个智能消息分发系统，支持根据告警数据自动选择合适的分发通道进行消息推送。</p>
            
            <h4>主要特性</h4>
            <ul>
              <li><strong>智能路由</strong>: 根据实例名称自动匹配配置的分发通道</li>
              <li><strong>多格式支持</strong>: 支持Prometheus AlertManager格式和自定义JSON格式</li>
              <li><strong>批量处理</strong>: 支持一次请求处理多个告警</li>
              <li><strong>自动模板</strong>: 每个分发通道绑定特定的消息模板</li>
              <li><strong>容错机制</strong>: 支持分发失败时的错误处理</li>
            </ul>

            <h4>工作流程</h4>
            <el-steps :active="4" align-center>
              <el-step title="接收告警" description="接收告警数据" />
              <el-step title="解析实例" description="提取实例名称" />
              <el-step title="匹配通道" description="找到配置的分发通道" />
              <el-step title="格式化消息" description="使用绑定的模板" />
              <el-step title="推送消息" description="发送到对应机器人" />
            </el-steps>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="请求格式" name="request">
          <div class="docs-content">
            <h4>请求地址</h4>
            <pre class="code-block">POST {{ distributionApiUrl }}</pre>
            
            <h4>请求头</h4>
            <pre class="code-block">Content-Type: application/json</pre>
            
            <h4>Prometheus AlertManager 格式</h4>
            <pre class="code-block">{{ prometheusExample }}</pre>
            
            <h4>自定义格式</h4>
            <pre class="code-block">{{ customExample }}</pre>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="响应格式" name="response">
          <div class="docs-content">
            <h4>成功响应</h4>
            <pre class="code-block">{{ successResponse }}</pre>
            
            <h4>错误响应</h4>
            <pre class="code-block">{{ errorResponse }}</pre>
            
            <h4>部分成功响应</h4>
            <pre class="code-block">{{ partialResponse }}</pre>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="配置说明" name="config">
          <div class="docs-content">
            <h4>分发通道配置</h4>
            <p>要使用分发接口，需要先配置分发通道：</p>
            <ol>
              <li>创建分发通道，绑定机器人和消息模板</li>
              <li>在实例映射中配置实例与分发通道的关系</li>
              <li>确保分发通道状态为启用</li>
            </ol>
            
            <h4>实例匹配规则</h4>
            <p>系统会根据以下规则匹配实例：</p>
            <ul>
              <li>Prometheus格式：使用 <code>labels.instance</code> 字段</li>
              <li>自定义格式：使用 <code>instance</code> 字段</li>
              <li>如果实例未配置分发通道，将跳过该告警</li>
            </ul>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog v-model="showTestDialog" title="测试分发接口" width="700px">
      <el-form :model="testForm" label-width="100px">
        <el-form-item label="接口地址">
          <el-input v-model="distributionApiUrl" disabled />
        </el-form-item>
        <el-form-item label="数据格式">
          <el-radio-group v-model="testForm.format">
            <el-radio value="prometheus">Prometheus AlertManager</el-radio>
            <el-radio value="custom">自定义格式</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="测试数据">
          <el-input 
            v-model="testForm.data"
            type="textarea"
            :rows="12"
            placeholder="请输入测试数据"
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
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTestDialog = false">取消</el-button>
          <el-button @click="loadTestData">加载示例数据</el-button>
          <el-button type="primary" @click="executeDistributionTest" :loading="testLoading">
            发送测试
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 示例对话框 -->
    <el-dialog v-model="showExamplesDialog" title="分发接口示例" width="800px">
      <el-tabs>
        <el-tab-pane label="curl 示例" name="curl">
          <pre class="code-block">{{ curlExample }}</pre>
        </el-tab-pane>
        <el-tab-pane label="Python 示例" name="python">
          <pre class="code-block">{{ pythonExample }}</pre>
        </el-tab-pane>
        <el-tab-pane label="JavaScript 示例" name="javascript">
          <pre class="code-block">{{ javascriptExample }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh, Document, Monitor, DataLine } from '@element-plus/icons-vue';
import { distributionApi } from '../../api';
import type { DistributionChannel } from '../../types';

// 响应式数据
const loading = ref(false);
const showDocsDialog = ref(false);
const showTestDialog = ref(false);
const showExamplesDialog = ref(false);
const testLoading = ref(false);
const channels = ref<DistributionChannel[]>([]);
const activeTab = ref('overview');
const testResult = ref<any>(null);

// 表单数据
const testForm = reactive({
  format: 'prometheus',
  data: ''
});

// 分发API地址
const distributionApiUrl = computed(() => {
  const baseUrl = window.location.origin;
  return `${baseUrl}/api/public/distribution/push/`;
});

// 分发通道统计
const channelStats = computed(() => {
  const total = channels.value.length;
  const active = channels.value.filter(c => c.is_active).length;
  const robotTypes = new Set(channels.value.map(c => c.robot_type)).size;
  
  return {
    total,
    active,
    instances: 0, // 这里可以从实例映射API获取
    robotTypes
  };
});

// 示例数据
const prometheusExample = `{
  "alerts": [
    {
      "labels": {
        "alertname": "HighCPUUsage",
        "instance": "web-server-01",
        "severity": "critical"
      },
      "annotations": {
        "summary": "High CPU usage detected",
        "description": "CPU usage is above 90%"
      },
      "status": "firing",
      "startsAt": "2023-12-07T10:00:00Z"
    }
  ]
}`;

const customExample = `{
  "alerts": [
    {
      "instance": "web-server-01",
      "title": "系统告警",
      "content": "服务器CPU使用率过高",
      "severity": "critical",
      "timestamp": "2023-12-07T10:00:00Z"
    }
  ]
}`;

const successResponse = `{
  "success": true,
  "message": "分发完成",
  "data": {
    "total_alerts": 1,
    "processed_alerts": 1,
    "successful_sends": 1,
    "failed_sends": 0,
    "results": [
      {
        "instance": "web-server-01",
        "status": "success",
        "channels": ["运维告警通道"],
        "message": "消息发送成功"
      }
    ]
  }
}`;

const errorResponse = `{
  "success": false,
  "message": "分发失败",
  "error": "Invalid request format"
}`;

const partialResponse = `{
  "success": true,
  "message": "部分分发成功",
  "data": {
    "total_alerts": 2,
    "processed_alerts": 2,
    "successful_sends": 1,
    "failed_sends": 1,
    "results": [
      {
        "instance": "web-server-01",
        "status": "success",
        "channels": ["运维告警通道"]
      },
      {
        "instance": "unknown-server",
        "status": "failed",
        "error": "No distribution channels configured"
      }
    ]
  }
}`;

const curlExample = `curl -X POST "${distributionApiUrl.value}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "alerts": [
      {
        "labels": {
          "alertname": "HighCPUUsage",
          "instance": "web-server-01",
          "severity": "critical"
        },
        "annotations": {
          "summary": "High CPU usage detected"
        }
      }
    ]
  }'`;

const pythonExample = `import requests
import json

url = "${distributionApiUrl.value}"
data = {
    "alerts": [
        {
            "labels": {
                "alertname": "HighCPUUsage",
                "instance": "web-server-01",
                "severity": "critical"
            },
            "annotations": {
                "summary": "High CPU usage detected"
            }
        }
    ]
}

response = requests.post(url, json=data)
print(response.json())`;

const javascriptExample = `fetch('${distributionApiUrl.value}', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    alerts: [
      {
        labels: {
          alertname: 'HighCPUUsage',
          instance: 'web-server-01',
          severity: 'critical'
        },
        annotations: {
          summary: 'High CPU usage detected'
        }
      }
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));`;

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

// 数据获取方法
const fetchData = async () => {
  loading.value = true;
  try {
    const response = await distributionApi.getChannels();
    channels.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取分发通道失败:', error);
    ElMessage.error('获取分发通道失败');
  } finally {
    loading.value = false;
  }
};

// 复制分发URL
const copyDistributionUrl = async () => {
  try {
    await navigator.clipboard.writeText(distributionApiUrl.value);
    ElMessage.success('分发接口地址已复制到剪贴板');
  } catch (error) {
    ElMessage.error('复制失败，请手动复制');
  }
};

// 显示API文档
const showApiDocs = () => {
  showDocsDialog.value = true;
  activeTab.value = 'overview';
};

// 测试分发接口
const testDistributionApi = () => {
  testForm.format = 'prometheus';
  testForm.data = prometheusExample;
  testResult.value = null;
  showTestDialog.value = true;
};

// 查看示例
const viewExamples = () => {
  showExamplesDialog.value = true;
};

// 加载测试数据
const loadTestData = () => {
  if (testForm.format === 'prometheus') {
    testForm.data = prometheusExample;
  } else {
    testForm.data = customExample;
  }
};

// 执行分发测试
const executeDistributionTest = async () => {
  if (!testForm.data.trim()) {
    ElMessage.error('请输入测试数据');
    return;
  }

  testLoading.value = true;
  try {
    const data = JSON.parse(testForm.data);
    const response = await fetch(distributionApiUrl.value, {
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

// 测试通道
const testChannel = async (channel: DistributionChannel) => {
  try {
    const testData = {
      alerts: [
        {
          labels: {
            alertname: 'TestAlert',
            instance: 'test-instance',
            severity: 'info'
          },
          annotations: {
            summary: `测试通道: ${channel.name}`
          }
        }
      ]
    };
    
    const response = await fetch(distributionApiUrl.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testData)
    });
    
    if (response.ok) {
      ElMessage.success(`通道 ${channel.name} 测试成功`);
    } else {
      ElMessage.error(`通道 ${channel.name} 测试失败`);
    }
  } catch (error) {
    ElMessage.error(`通道 ${channel.name} 测试失败: ${error}`);
  }
};

// 生命周期
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.distribution-api-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-alert {
  margin-bottom: 20px;
}

.distribution-card,
.stats-card,
.channels-card {
  margin-bottom: 20px;
}

.distribution-info {
  padding: 20px 0;
}

.api-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.api-header h4 {
  margin: 0;
  color: #303133;
}

.api-url-display {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f6f8fa;
  border-radius: 6px;
  border: 1px solid #d1d9e0;
}

.api-url {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  color: #0366d6;
  word-break: break-all;
}

.api-details {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  justify-content: center;
}

.docs-content {
  padding: 20px 0;
}

.docs-content h4 {
  margin-top: 25px;
  margin-bottom: 10px;
  color: #303133;
}

.docs-content h4:first-child {
  margin-top: 0;
}

.docs-content ul,
.docs-content ol {
  padding-left: 20px;
}

.docs-content li {
  margin-bottom: 5px;
}

.code-block {
  background-color: #f6f8fa;
  padding: 15px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  border: 1px solid #d1d9e0;
  margin: 10px 0;
  overflow-x: auto;
  white-space: pre-wrap;
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

:deep(.el-steps) {
  margin: 20px 0;
}

:deep(.el-step__title) {
  font-size: 12px;
}

:deep(.el-step__description) {
  font-size: 11px;
}
</style>
