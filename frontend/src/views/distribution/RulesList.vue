<template>
  <div class="rules-container">
    <div class="page-header">
      <h2>分发规则管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建规则
      </el-button>
    </div>

    <!-- 规则列表 -->
    <el-card>
      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="name" label="规则名称" width="200" />
        <el-table-column prop="type" label="匹配类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'json' ? 'primary' : 'success'">
              {{ scope.row.type === 'json' ? 'JSON模式' : '字符串模式' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.is_active"
              @change="toggleRuleStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editRule(scope.row)" plain>
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteRule(scope.row)" plain>
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑规则对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingRule ? '编辑规则' : '创建规则'"
      width="800px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        :rules="ruleFormRules"
        label-width="120px"
      >
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
        </el-form-item>

        <el-form-item label="匹配类型" prop="type">
          <el-radio-group v-model="ruleForm.type">
            <el-radio value="json">JSON模式</el-radio>
            <el-radio value="string">字符串模式</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="ruleForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入规则描述"
          />
        </el-form-item>

        <el-form-item label="提取路径" prop="extract_path" v-if="ruleForm.type === 'json'">
          <el-autocomplete
            v-model="ruleForm.extract_path"
            :fetch-suggestions="getPathSuggestions"
            placeholder="例如: alerts[].labels.instance"
            style="width: 100%"
            clearable
          >
            <template #suffix>
              <el-dropdown @command="selectPresetPath">
                <el-button text type="primary" size="small">
                  <el-icon><ArrowDown /></el-icon>
                  预设
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="alerts[].labels.instance">实例名称 (instance)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.project_custom">项目名称 (project_custom)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.cluster">集群名称 (cluster)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.environment">环境 (environment)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.severity">严重级别 (severity)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.job">任务名称 (job)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.vm">虚拟机名称 (vm)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.namespace">命名空间 (namespace)</el-dropdown-item>
                    <el-dropdown-item command="alerts[].labels.service">服务名称 (service)</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-autocomplete>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            指定要提取的JSON路径，支持Prometheus告警格式。点击"预设"选择常用路径
          </div>
        </el-form-item>

        <el-form-item label="提取模式" prop="extract_pattern" v-if="ruleForm.type === 'string'">
          <el-input
            v-model="ruleForm.extract_pattern"
            placeholder="例如: {{instance}}"
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            使用{{}}包围要提取的变量名，如：{<!-- -->{ instance }}、{<!-- -->{ hostname }}
          </div>
        </el-form-item>

        <el-form-item label="测试数据">
          <el-input
            v-model="testData"
            type="textarea"
            :rows="8"
            placeholder="输入测试数据进行验证"
          />
          <div class="test-actions">
            <el-button @click="testRule" :loading="testing">测试规则</el-button>
            <el-button @click="loadSampleData">加载示例数据</el-button>
          </div>
        </el-form-item>

        <el-form-item v-if="testResult.length > 0" label="提取结果">
          <div class="test-result">
            <el-tag v-for="(result, index) in testResult" :key="index" class="result-tag">
              {{ result }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="saveRule" :loading="saving">
            {{ editingRule ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, InfoFilled, ArrowDown } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { distributionApi } from '../../api';
import type { DistributionRule } from '../../types';

// 接口定义
// Rule接口现在使用导入的DistributionRule类型

// 响应式数据
const loading = ref(false);
const saving = ref(false);
const testing = ref(false);
const showCreateDialog = ref(false);
const editingRule = ref<DistributionRule | null>(null);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const rules = ref<DistributionRule[]>([]);
const testData = ref('');
const testResult = ref<string[]>([]);

// 表单相关
const ruleFormRef = ref<FormInstance>();
const ruleForm = reactive<DistributionRule>({
  name: '',
  type: 'json',
  description: '',
  extract_path: '',
  extract_pattern: '',
  is_active: true
});

const ruleFormRules: FormRules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择匹配类型', trigger: 'change' }
  ],
  extract_path: [
    { 
      required: true, 
      message: '请输入JSON提取路径', 
      trigger: 'blur',
      validator: (_rule, value, callback) => {
        if (ruleForm.type === 'json' && !value) {
          callback(new Error('JSON模式下必须指定提取路径'));
        } else {
          callback();
        }
      }
    }
  ],
  extract_pattern: [
    { 
      required: true, 
      message: '请输入字符串提取模式', 
      trigger: 'blur',
      validator: (_rule, value, callback) => {
        if (ruleForm.type === 'string' && !value) {
          callback(new Error('字符串模式下必须指定提取模式'));
        } else {
          callback();
        }
      }
    }
  ]
};

// 示例数据
const sampleJsonData = `{
    "receiver": "web\\.hook\\.prometheusalert",
    "status": "resolved",
    "alerts": [
        {
            "status": "resolved",
            "labels": {
                "alertname": "ContainerAbsent",
                "image": "nginx:latest",
                "instance": "dev-2",
                "job": "docker-exporter-dev-2",
                "name": "doc-sync-api",
                "severity": "warning"
            },
            "annotations": {
                "description": "容器 doc-sync-api 已停止3分钟，请及时查看! ",
                "summary": "Docker无容器，容器：dev-2"
            },
            "startsAt": "2025-05-08T04:39:27.678Z",
            "endsAt": "2025-05-08T05:13:42.678Z",
            "generatorURL": "http://862270ed36a2:9090/graph?g0.expr=container_status_running%7Bname%21~%22flow.%2A%22%7D+%3D%3D+0\\u0026g0.tab=1",
            "fingerprint": "adcb08b891a22873"
        },
        {
            "status": "resolved",
            "labels": {
                "alertname": "ContainerRestart",
                "image": "nginx:latest",
                "instance": "dev-2",
                "job": "docker-exporter-dev-2",
                "name": "doc-sync-api",
                "severity": "warning"
            },
            "annotations": {
                "description": "容器 doc-sync-api 发生重启，请及时查看! ",
                "summary": "Docker无容器，容器：dev-2"
            },
            "startsAt": "2025-05-08T04:36:27.678Z",
            "endsAt": "2025-05-08T05:13:42.678Z",
            "generatorURL": "http://862270ed36a2:9090/graph?g0.expr=container_status_restarting%7Bname%21~%22flow.%2A%22%7D+%3D%3D+1\\u0026g0.tab=1",
            "fingerprint": "a3203ff29ba80da5"
        }
    ],
    "groupLabels": {
        "instance": "dev-2"
    },
    "commonLabels": {
        "image": "314642755113.dkr.ecr.us-west-1.amazonaws.com/helixlife-ai/paas-doc-sync:master",
        "instance": "dev-2",
        "job": "docker-exporter-dev-2",
        "name": "doc-sync-api",
        "severity": "warning"
    },
    "commonAnnotations": {
        "summary": "Docker无容器，容器：dev-2"
    },
    "externalURL": "http://3fdae39bcac4:9093",
    "version": "4",
    "groupKey": "{}:{instance=\\"dev-2\\"}",
    "truncatedAlerts": 0
}`;

const sampleStringData = `Alert: 虚机分区使用率超过 90%
Instance: 172.27.173.18:80
Project: 青岛地铁官网
Severity: critical
Environment: 测试环境`;

// 方法实现
const fetchRules = async () => {
  loading.value = true;
  try {
    const response = await distributionApi.getRules({
      page: currentPage.value,
      page_size: pageSize.value
    });
    
    rules.value = response.data.results || response.data;
    total.value = response.data.count || response.data.length;
  } catch (error) {
    console.error('获取规则列表失败:', error);
    ElMessage.error('获取规则列表失败');
  } finally {
    loading.value = false;
  }
};

const saveRule = async () => {
  if (!ruleFormRef.value) return;
  
  try {
    await ruleFormRef.value.validate();
    saving.value = true;
    
    if (editingRule.value) {
      await distributionApi.updateRule(editingRule.value.id!, ruleForm);
    } else {
      await distributionApi.createRule(ruleForm);
    }
    
    ElMessage.success(editingRule.value ? '规则更新成功' : '规则创建成功');
    handleDialogClose();
    fetchRules();
  } catch (error) {
    console.error('保存规则失败:', error);
    ElMessage.error('保存规则失败');
  } finally {
    saving.value = false;
  }
};

const editRule = (rule: DistributionRule) => {
  editingRule.value = rule;
  Object.assign(ruleForm, rule);
  showCreateDialog.value = true;
};

const deleteRule = async (_ruleToDelete: DistributionRule) => {
  try {
    await ElMessageBox.confirm('确定要删除此规则吗？', '确认删除', {
      type: 'warning'
    });
    
    await distributionApi.deleteRule(_ruleToDelete.id!);
    
    ElMessage.success('删除成功');
    fetchRules();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

const toggleRuleStatus = async (rule: DistributionRule) => {
  try {
    await distributionApi.updateRule(rule.id!, { is_active: rule.is_active });
    ElMessage.success('状态更新成功');
  } catch (error) {
    rule.is_active = !rule.is_active; // 回滚状态
    console.error('状态更新失败:', error);
    ElMessage.error('状态更新失败');
  }
};

const testRule = async () => {
  if (!testData.value) {
    ElMessage.warning('请输入测试数据');
    return;
  }

  testing.value = true;
  testResult.value = [];

  try {
    const response = await distributionApi.testRule({
      type: ruleForm.type,
      extract_path: ruleForm.extract_path,
      extract_pattern: ruleForm.extract_pattern,
      test_data: testData.value
    });
    
    testResult.value = response.data.extracted_values || [];
    
    if (testResult.value.length === 0) {
      ElMessage.warning('未提取到任何值，请检查规则配置');
    } else {
      ElMessage.success(`成功提取到 ${testResult.value.length} 个值`);
    }
  } catch (error) {
    console.error('测试失败:', error);
    ElMessage.error('测试失败：请检查数据格式和规则配置');
  } finally {
    testing.value = false;
  }
};

const loadSampleData = () => {
  if (ruleForm.type === 'json') {
    testData.value = sampleJsonData;
    // 不修改提取路径，让用户自己设置
  } else {
    testData.value = sampleStringData;
    // 不修改提取模式，让用户自己设置
  }
};

const handleDialogClose = () => {
  showCreateDialog.value = false;
  editingRule.value = null;
  testResult.value = [];
  testData.value = '';
  
  // 重置表单
  Object.assign(ruleForm, {
    name: '',
    type: 'json',
    description: '',
    extract_path: '',
    extract_pattern: '',
    is_active: true
  });
  
  ruleFormRef.value?.resetFields();
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  fetchRules();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchRules();
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN');
};

// 自动补全和预设路径功能
const getPathSuggestions = (queryString: string, callback: Function) => {
  const suggestions = [
    { value: 'alerts[].labels.instance', description: '实例名称' },
    { value: 'alerts[].labels.project_custom', description: '项目名称' },
    { value: 'alerts[].labels.cluster', description: '集群名称' },
    { value: 'alerts[].labels.environment', description: '环境' },
    { value: 'alerts[].labels.severity', description: '严重级别' },
    { value: 'alerts[].labels.job', description: '任务名称' },
    { value: 'alerts[].labels.vm', description: '虚拟机名称' },
    { value: 'alerts[].labels.namespace', description: '命名空间' },
    { value: 'alerts[].labels.service', description: '服务名称' },
    { value: 'alerts[].labels.alertname', description: '告警名称' },
    { value: 'alerts[].labels.department', description: '部门' },
    { value: 'alerts[].labels.group', description: '组' },
    { value: 'alerts[].labels.physical_server', description: '物理服务器' },
    { value: 'alerts[].labels.vim', description: 'VIM' }
  ];

  const results = queryString
    ? suggestions.filter(item =>
        item.value.toLowerCase().includes(queryString.toLowerCase()) ||
        item.description.includes(queryString)
      )
    : suggestions;

  callback(results);
};

const selectPresetPath = (path: string) => {
  ruleForm.extract_path = path;
};

// 生命周期
onMounted(() => {
  fetchRules();
});
</script>

<style scoped>
.rules-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  display: flex;
  align-items: center;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  margin-right: 5px;
}

.test-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.test-result {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.result-tag {
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
