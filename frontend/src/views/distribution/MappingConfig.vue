<template>
  <div class="mapping-container">
    <div class="page-header">
      <h2>分发通道关联</h2>
      <el-button type="primary" @click="refreshInstances" :loading="refreshLoading">
        <el-icon><Refresh /></el-icon>
        刷新实例
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索实例名称"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
            <el-option label="已配置" value="configured" />
            <el-option label="未配置" value="unconfigured" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="robotFilter" placeholder="机器人筛选" clearable>
            <el-option
              v-for="robot in robots"
              :key="robot.id"
              :label="robot.name"
              :value="robot.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="clearFilters">清除筛选</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 实例映射表格 -->
    <el-card>
      <div class="table-header">
        <div class="info-stats">
          <el-statistic title="总实例数" :value="total" />
          <el-statistic title="已配置" :value="configuredCount" />
          <el-statistic title="未配置" :value="unconfiguredCount" />
        </div>
        <div class="batch-actions">
          <el-button
            type="primary"
            @click="showBatchDialog = true"
            :disabled="selectedInstances.length === 0"
          >
            批量配置
          </el-button>
          <el-button
            type="danger"
            @click="batchClearMapping"
            :disabled="selectedInstances.length === 0"
            plain
          >
            批量清除
          </el-button>
        </div>
      </div>

      <el-table
        :data="filteredInstances"
        v-loading="loading"
        stripe
        border
        @selection-change="handleSelectionChange"
        style="width: 100%; display: table;"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="instance_name" label="实例名称" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <div class="instance-info">
              <el-tag :type="getInstanceTagType(scope.row)" size="small">
                {{ scope.row.instance_name }}
              </el-tag>
              <span class="instance-count" v-if="scope.row.alert_count > 0">
                ({{ scope.row.alert_count }}次告警)
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="source_rule" label="来源规则" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <el-tag v-if="scope.row.source_rule" type="info" size="small">
              {{ scope.row.source_rule }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="robot_name" label="配置机器人" min-width="200">
          <template #default="scope">
            <el-select
              v-model="scope.row.robot_id"
              placeholder="选择机器人"
              @change="updateMapping(scope.row)"
              clearable
              style="width: 100%"
              size="small"
            >
              <el-option
                v-for="robot in robots"
                :key="robot.id"
                :label="robot.name"
                :value="robot.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="last_alert_time" label="最后告警时间" width="180" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.last_alert_time">
              {{ formatDate(scope.row.last_alert_time) }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发现时间" width="180" show-overflow-tooltip>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.robot_id ? 'success' : 'warning'" size="small">
              {{ scope.row.robot_id ? '已配置' : '未配置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="viewInstanceDetail(scope.row)"
              plain
            >
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="clearMapping(scope.row)"
              plain
              v-if="scope.row.robot_id"
            >
              清除
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

    <!-- 批量配置对话框 -->
    <el-dialog v-model="showBatchDialog" title="批量配置机器人" width="500px">
      <el-form :model="batchForm" label-width="120px">
        <el-form-item label="选择机器人">
          <el-select v-model="batchForm.robot_id" placeholder="请选择机器人" style="width: 100%">
            <el-option
              v-for="robot in robots"
              :key="robot.id"
              :label="robot.name"
              :value="robot.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择的实例">
          <div class="selected-instances">
            <el-tag
              v-for="instance in selectedInstances"
              :key="instance.id"
              closable
              @close="removeFromSelection(instance)"
            >
              {{ instance.instance_name }}
            </el-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showBatchDialog = false">取消</el-button>
          <el-button type="primary" @click="batchConfigureMapping" :loading="batchSaving">
            确认配置
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 实例详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="实例详情" width="800px">
      <div v-if="currentInstance">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="实例名称">
            {{ currentInstance.instance_name }}
          </el-descriptions-item>
          <el-descriptions-item label="配置机器人">
            <el-tag v-if="currentInstance.robot_name" type="success">
              {{ currentInstance.robot_name }}
            </el-tag>
            <span v-else>未配置</span>
          </el-descriptions-item>
          <el-descriptions-item label="来源规则">
            {{ currentInstance.source_rule || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="告警次数">
            {{ currentInstance.alert_count }}
          </el-descriptions-item>
          <el-descriptions-item label="发现时间">
            {{ formatDate(currentInstance.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后告警">
            {{ currentInstance.last_alert_time ? formatDate(currentInstance.last_alert_time) : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 告警历史 -->
        <div class="alert-history" v-if="instanceAlerts.length > 0">
          <h4>最近告警记录</h4>
          <el-table :data="instanceAlerts" size="small">
            <el-table-column prop="alert_time" label="告警时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.alert_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="rule_name" label="触发规则" />
            <el-table-column prop="alert_content" label="告警内容" show-overflow-tooltip />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Refresh, Search, View } from '@element-plus/icons-vue';
import { distributionApi, robotApi } from '../../api';
import type { InstanceMapping, Robot, AlertRecord } from '../../types';

// 响应式数据
const loading = ref(false);
const refreshLoading = ref(false);
const batchSaving = ref(false);
const searchQuery = ref('');
const statusFilter = ref('');
const robotFilter = ref<number | ''>('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const instances = ref<InstanceMapping[]>([]);
const robots = ref<Robot[]>([]);
const selectedInstances = ref<InstanceMapping[]>([]);
const showBatchDialog = ref(false);
const showDetailDialog = ref(false);
const currentInstance = ref<InstanceMapping | null>(null);
const instanceAlerts = ref<AlertRecord[]>([]);

// 表单数据
const batchForm = reactive({
  robot_id: undefined as number | undefined
});

// 计算属性
const filteredInstances = computed(() => {
  let filtered = instances.value;

  // 搜索过滤
  if (searchQuery.value) {
    filtered = filtered.filter(instance =>
      instance.instance_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(instance => {
      if (statusFilter.value === 'configured') {
        return instance.robot_id;
      } else if (statusFilter.value === 'unconfigured') {
        return !instance.robot_id;
      }
      return true;
    });
  }

  // 机器人过滤
  if (robotFilter.value) {
    filtered = filtered.filter(instance => instance.robot_id === robotFilter.value);
  }

  return filtered;
});

const configuredCount = computed(() => 
  instances.value.filter(instance => instance.robot_id).length
);

const unconfiguredCount = computed(() => 
  instances.value.filter(instance => !instance.robot_id).length
);

// 方法实现
const fetchInstances = async () => {
  loading.value = true;
  try {
    const response = await distributionApi.getInstances({
      page: currentPage.value,
      page_size: pageSize.value
    });
    
    instances.value = response.data.results || response.data;
    total.value = response.data.count || response.data.length;
  } catch (error) {
    console.error('获取实例列表失败:', error);
    ElMessage.error('获取实例列表失败');
  } finally {
    loading.value = false;
  }
};

const fetchRobots = async () => {
  try {
    const response = await robotApi.getRobots();
    robots.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取机器人列表失败:', error);
    ElMessage.error('获取机器人列表失败');
  }
};

const updateMapping = async (instance: InstanceMapping) => {
  try {
    await distributionApi.updateInstanceMapping(instance.id, {
      robot_id: instance.robot_id
    });

    // 更新本地数据
    if (instance.robot_id) {
      const robot = robots.value.find(r => r.id === instance.robot_id);
      instance.robot_name = robot?.name;
    } else {
      instance.robot_name = undefined;
    }

    ElMessage.success('配置更新成功');
  } catch (error) {
    console.error('配置更新失败:', error);
    ElMessage.error('配置更新失败');
  }
};

const batchConfigureMapping = async () => {
  if (!batchForm.robot_id) {
    ElMessage.warning('请选择机器人');
    return;
  }

  batchSaving.value = true;
  try {
    await distributionApi.batchConfigureMapping({
      instance_ids: selectedInstances.value.map(i => i.id),
      robot_id: batchForm.robot_id
    });

    // 更新本地数据
    const robot = robots.value.find(r => r.id === batchForm.robot_id);
    selectedInstances.value.forEach(instance => {
      instance.robot_id = batchForm.robot_id as number;
      instance.robot_name = robot?.name;
    });

    ElMessage.success('批量配置成功');
    showBatchDialog.value = false;
    selectedInstances.value = [];
    batchForm.robot_id = undefined;
  } catch (error) {
    console.error('批量配置失败:', error);
    ElMessage.error('批量配置失败');
  } finally {
    batchSaving.value = false;
  }
};

const batchClearMapping = async () => {
  try {
    await ElMessageBox.confirm('确定要清除选中实例的机器人配置吗？', '确认清除', {
      type: 'warning'
    });

    await distributionApi.batchClearMapping({
      instance_ids: selectedInstances.value.map(i => i.id)
    });

    // 更新本地数据
    selectedInstances.value.forEach(instance => {
      instance.robot_id = undefined;
      instance.robot_name = undefined;
    });

    ElMessage.success('批量清除成功');
    selectedInstances.value = [];
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量清除失败:', error);
      ElMessage.error('批量清除失败');
    }
  }
};

const clearMapping = async (instance: InstanceMapping) => {
  try {
    await ElMessageBox.confirm('确定要清除此实例的机器人配置吗？', '确认清除', {
      type: 'warning'
    });

    instance.robot_id = undefined;
    instance.robot_name = undefined;
    await updateMapping(instance);
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清除配置失败');
    }
  }
};

const refreshInstances = async () => {
  refreshLoading.value = true;
  try {
    await distributionApi.refreshInstances();
    await fetchInstances();
    ElMessage.success('实例数据已刷新');
  } catch (error) {
    console.error('刷新实例失败:', error);
    ElMessage.error('刷新实例失败');
  } finally {
    refreshLoading.value = false;
  }
};

const viewInstanceDetail = async (instance: InstanceMapping) => {
  currentInstance.value = instance;
  showDetailDialog.value = true;

  // 获取告警历史
  try {
    const response = await distributionApi.getInstanceAlerts(instance.id);
    instanceAlerts.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取告警历史失败:', error);
    ElMessage.error('获取告警历史失败');
    // 设置空数组作为后备
    instanceAlerts.value = [];
  }
};

const handleSelectionChange = (selection: InstanceMapping[]) => {
  selectedInstances.value = selection;
};

const removeFromSelection = (instance: InstanceMapping) => {
  const index = selectedInstances.value.findIndex(i => i.id === instance.id);
  if (index > -1) {
    selectedInstances.value.splice(index, 1);
  }
};

const handleSearch = () => {
  currentPage.value = 1;
};

const clearFilters = () => {
  searchQuery.value = '';
  statusFilter.value = '';
  robotFilter.value = '';
  currentPage.value = 1;
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  fetchInstances();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchInstances();
};

const getInstanceTagType = (instance: InstanceMapping) => {
  if (instance.alert_count > 10) return 'danger';
  if (instance.alert_count > 5) return 'warning';
  return 'info';
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN');
};

// 生命周期
onMounted(() => {
  fetchInstances();
  fetchRobots();
});
</script>

<style scoped>
.mapping-container {
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

.filter-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.info-stats {
  display: flex;
  gap: 40px;
}

.batch-actions {
  display: flex;
  gap: 10px;
}

.instance-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.instance-count {
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.selected-instances {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 120px;
  overflow-y: auto;
}

.alert-history {
  margin-top: 20px;
}

.alert-history h4 {
  margin-bottom: 10px;
  color: #303133;
}

.text-muted {
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 表格对齐修复 */
.el-table {
  width: 100% !important;
  display: table !important; /* 强制覆盖 inline-block */
}

.el-table th {
  text-align: center;
  background-color: #fafafa;
}

.el-table td {
  vertical-align: middle;
}

.el-table .el-table__header {
  width: 100% !important;
  display: table-header-group !important;
}

.el-table .el-table__body {
  width: 100% !important;
  display: table-row-group !important;
}

.el-table .el-table__header-wrapper {
  width: 100% !important;
  display: block !important;
}

.el-table .el-table__body-wrapper {
  width: 100% !important;
  display: block !important;
}

/* 表格行对齐 */
.el-table tr {
  display: table-row !important;
}

.el-table th,
.el-table td {
  display: table-cell !important;
}

/* 选择框列对齐 */
.el-table .el-table-column--selection .el-table__cell {
  text-align: center;
  padding-left: 0;
  padding-right: 0;
}

/* 操作按钮对齐 */
.el-button + .el-button {
  margin-left: 8px;
}

/* 下拉框样式 */
.el-select {
  width: 100%;
}
</style>
