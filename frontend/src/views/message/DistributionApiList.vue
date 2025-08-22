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
        <!-- 分发接口说明 -->
        <!-- <el-alert 
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
        </el-alert> -->

        <!-- 分发接口信息 -->
        <el-card class="distribution-card" shadow="never">
          <div class="distribution-info">
            <div class="api-header">
              <h4>分发接口地址</h4>
              <el-button type="primary" size="small" @click="copyDistributionUrl">
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
                  <el-tag type="info" style="margin-left: 8px">Zabbix Webhook</el-tag>
                  <el-tag type="info" style="margin-left: 8px">自定义JSON</el-tag>
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
                <el-button type="primary" size="small" @click="testChannel(scope.row)" plain>
                  测试
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="channels.length === 0" description="暂无分发通道，请先创建分发通道" />
        </el-card>
      </div>
    </el-card>

    <!-- API文档对话框 -->
    <el-dialog v-model="showDocsDialog" title="分发接口文档" width="900px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="接口说明" name="overview">
          <div class="docs-content">
            <h4>接口概述</h4>
            <p>
              高级分发接口是一个智能消息分发系统，支持根据告警数据自动选择合适的分发通道进行消息推送。
            </p>

            <h4>主要特性</h4>
            <ul>
              <li><strong>智能路由</strong>: 根据实例名称自动匹配配置的分发通道</li>
              <li>
                <strong>多格式支持</strong>: 支持Prometheus AlertManager、Zabbix
                Webhook和自定义JSON格式
              </li>
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
    <el-dialog
      v-model="showExamplesDialog"
      title="分发接口示例"
      width="900px"
      @open="handleExamplesDialogOpen"
    >
      <el-tabs v-model="activeExampleTab">
        <el-tab-pane label="AlertManager 配置" name="alertmanager">
          <div class="docs-content">
            <h4>AlertManager 配置示例</h4>
            <p>以下是在 Prometheus AlertManager 中配置分发接口的完整示例：</p>
            <pre class="code-block">{{ alertmanagerConfig }}</pre>

            <h4>告警规则示例</h4>
            <p>配合使用的 Prometheus 告警规则：</p>
            <pre class="code-block">{{ prometheusRules }}</pre>

            <h4>配置说明</h4>
            <ul>
              <li><strong>webhook_configs</strong>: 配置分发接口的 webhook 地址</li>
              <li><strong>send_resolved</strong>: 设置为 true 可以发送告警恢复通知</li>
              <li><strong>http_config</strong>: 可以配置超时、重试等参数</li>
              <li><strong>route</strong>: 根据告警标签路由到不同的接收器</li>
            </ul>
          </div>
        </el-tab-pane>
        <el-tab-pane label="curl 示例" name="curl">
          <pre class="code-block">{{ curlExample }}</pre>
        </el-tab-pane>
        <el-tab-pane label="Python 示例" name="python">
          <pre class="code-block">{{ pythonExample }}</pre>
        </el-tab-pane>
        <el-tab-pane label="JavaScript 示例" name="javascript">
          <pre class="code-block">{{ javascriptExample }}</pre>
        </el-tab-pane>
        <el-tab-pane label="Zabbix 配置" name="zabbix">
          <div class="docs-content">
            <h4>Zabbix Webhook 配置示例</h4>
            <p>以下是在 Zabbix 中配置分发接口的完整示例：</p>

            <h4>1. 创建媒体类型</h4>
            <p>在 Zabbix 管理界面中创建新的媒体类型：</p>
            <pre class="code-block">{{ zabbixMediaTypeConfig }}</pre>

            <h4>2. 触发器动作配置</h4>
            <p>配置触发器动作，当告警触发时发送 webhook：</p>
            <pre class="code-block">{{ zabbixActionConfig }}</pre>

            <h4>3. 数据格式示例</h4>
            <p>Zabbix 发送到分发接口的数据格式：</p>
            <pre class="code-block">{{ zabbixDataExample }}</pre>

            <h4>配置说明</h4>
            <ul>
              <li><strong>URL</strong>: 设置为分发接口地址</li>
              <li><strong>HTTP 方法</strong>: 选择 POST</li>
              <li><strong>内容类型</strong>: 设置为 application/json</li>
              <li><strong>主机标识</strong>: 使用 {HOST.NAME} 作为实例标识</li>
              <li><strong>告警映射</strong>: 在系统中配置主机名到分发通道的映射关系</li>
            </ul>

            <h4>配置步骤</h4>
            <ol>
              <li>登录 Zabbix 管理界面</li>
              <li>进入 管理 → 媒体类型</li>
              <li>点击 "创建媒体类型"</li>
              <li>选择类型为 "Webhook"</li>
              <li>填写名称，如 "MessagePushSystem"</li>
              <li>设置 URL 为分发接口地址</li>
              <li>配置参数和消息模板</li>
              <li>创建动作规则，绑定该媒体类型</li>
              <li>在用户媒体中添加该媒体类型</li>
            </ol>
          </div>
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
const activeExampleTab = ref('alertmanager');
const testResult = ref<unknown | null>(null);

// 表单数据
const testForm = reactive({
  format: 'prometheus',
  data: '',
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
    robotTypes,
  };
});

// 示例数据 - 使用 computed 确保响应式更新
const prometheusExample = computed(
  () => `{
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
}`
);

const customExample = computed(
  () => `{
  "alerts": [
    {
      "instance": "web-server-01",
      "title": "系统告警",
      "content": "服务器CPU使用率过高",
      "severity": "critical",
      "timestamp": "2023-12-07T10:00:00Z"
    }
  ]
}`
);

const successResponse = computed(
  () => `{
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
}`
);

const errorResponse = computed(
  () => `{
  "success": false,
  "message": "分发失败",
  "error": "Invalid request format"
}`
);

const partialResponse = computed(
  () => `{
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
}`
);

const curlExample = computed(
  () => `curl -X POST "${distributionApiUrl.value}" \\
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
  }'`
);

const alertmanagerConfig = computed(
  () => `# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alertmanager@example.org'

route:
  group_by: ['alertname', 'namespace']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'message-push-system'

receivers:
- name: 'message-push-system'
  webhook_configs:
  - url: '${distributionApiUrl.value}'
    send_resolved: true
    http_config:
      timeout: 10s
    title: 'Prometheus Alert'
    text: 'Alert Summary: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']`
);

const prometheusRules = computed(
  () => `# prometheus-rules.yml
groups:
- name: system-alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage_percent > 90
    for: 5m
    labels:
      severity: critical
      instance: "{{ $labels.instance }}"
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

  - alert: HighMemoryUsage
    expr: memory_usage_percent > 85
    for: 5m
    labels:
      severity: warning
      instance: "{{ $labels.instance }}"
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

  - alert: DiskSpaceLow
    expr: disk_free_percent < 10
    for: 2m
    labels:
      severity: critical
      instance: "{{ $labels.instance }}"
    annotations:
      summary: "Low disk space on {{ $labels.instance }}"
      description: "Only {{ $value }}% disk space remaining on {{ $labels.instance }}"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
      instance: "{{ $labels.instance }}"
    annotations:
      summary: "Service down on {{ $labels.instance }}"`
);

const pythonExample = computed(
  () => `import requests
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
print(response.json())`
);

const javascriptExample = computed(
  () => `fetch('${distributionApiUrl.value}', {
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
.then(data => console.log(data));`
);

// Zabbix配置示例
const zabbixMediaTypeConfig = computed(
  () => `名称: MessagePushSystem
类型: Webhook
URL: ${distributionApiUrl.value}
HTTP 方法: POST
内容类型: application/json

参数配置:
- 参数名: alerts
- 值: [
    {
      "instance": "{HOST.NAME}",
      "title": "{TRIGGER.NAME}",
      "content": "{TRIGGER.DESCRIPTION}",
      "severity": "{TRIGGER.SEVERITY}",
      "status": "{TRIGGER.STATUS}",
      "timestamp": "{EVENT.DATE} {EVENT.TIME}",
      "host": "{HOST.NAME}",
      "hostip": "{HOST.IP}",
      "itemkey": "{ITEM.KEY}",
      "itemvalue": "{ITEM.VALUE}"
    }
  ]

消息模板:
主题: Zabbix 告警: {TRIGGER.NAME}
消息: 
主机: {HOST.NAME} ({HOST.IP})
触发器: {TRIGGER.NAME}
状态: {TRIGGER.STATUS}
严重程度: {TRIGGER.SEVERITY}
时间: {EVENT.DATE} {EVENT.TIME}
描述: {TRIGGER.DESCRIPTION}`
);

const zabbixActionConfig = computed(
  () => `动作配置:
名称: Send to MessagePushSystem
事件源: 触发器

条件:
- 维护状态 不等于 "在维护中"
- 触发器状态 等于 "PROBLEM"
- 触发器严重程度 >= "警告"

操作:
1. 发送消息
   - 发送给用户: Admin (添加媒体类型: MessagePushSystem)
   - 仅发送到: MessagePushSystem
   - 自定义消息: 是
   
2. 恢复操作 (可选)
   - 条件: 触发器状态 等于 "OK"
   - 操作: 发送消息 (告警恢复通知)`
);

const zabbixDataExample = computed(
  () => `{
  "alerts": [
    {
      "instance": "web-server-01",
      "title": "High CPU usage on web-server-01",
      "content": "CPU使用率超过90%，当前值: 95%",
      "severity": "4",
      "status": "PROBLEM",
      "timestamp": "2023-12-07 10:30:00",
      "host": "web-server-01",
      "hostip": "192.168.1.100",
      "itemkey": "system.cpu.util",
      "itemvalue": "95.5"
    }
  ]
}`
);

// 工具方法
const getRobotTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    wechat: '企业微信',
    feishu: '飞书',
    dingtalk: '钉钉',
  };
  return typeMap[type] || type;
};

const getRobotTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    wechat: 'success',
    feishu: 'warning',
    dingtalk: 'info',
  };
  return typeMap[type] || 'info';
};

// 数据获取方法
const fetchData = async () => {
  loading.value = true;
  try {
    const response = await distributionApi.getChannels();
    channels.value = response.data.results || response.data;
  } catch (_error) {
    console.error('获取分发通道失败:', _error);
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
  } catch (_error) {
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
  testForm.data = prometheusExample.value;
  testResult.value = null;
  showTestDialog.value = true;
};

// 查看示例
const viewExamples = () => {
  showExamplesDialog.value = true;
  activeExampleTab.value = 'alertmanager';
};

// 处理示例对话框打开事件
const handleExamplesDialogOpen = () => {
  // 确保默认选中第一个标签页
  activeExampleTab.value = 'alertmanager';
};

// 加载测试数据
const loadTestData = () => {
  if (testForm.format === 'prometheus') {
    testForm.data = prometheusExample.value;
  } else {
    testForm.data = customExample.value;
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
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();
    testResult.value = {
      success: response.ok,
      response: JSON.stringify(result, null, 2),
    };
  } catch (_error) {
    testResult.value = {
      success: false,
      response: `请求失败: ${_error}`,
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
            severity: 'info',
          },
          annotations: {
            summary: `测试通道: ${channel.name}`,
          },
        },
      ],
    };

    const response = await fetch(distributionApiUrl.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    });

    if (response.ok) {
      ElMessage.success(`通道 ${channel.name} 测试成功`);
    } else {
      ElMessage.error(`通道 ${channel.name} 测试失败`);
    }
  } catch (_error) {
    ElMessage.error(`通道 ${channel.name} 测试失败: ${_error}`);
  }
};

// 生命周期
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.distribution-api-container {
  padding: 0;
  width: 100%;
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
  margin-bottom: 0px;
}

/* .distribution-info {
  padding: 20px;
} */

.api-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.api-header h4 {
  margin: 0;
  color: #303133;
}

.api-url-display {
  margin-bottom: 20px;
  padding: 10px;
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
  margin-top: 10px;
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
