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
            <el-tag v-if="scope.row.source_rule_name" type="info" size="small">
              {{ scope.row.source_rule_name }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="robot_names" label="配置机器人" min-width="250">
          <template #default="scope">
            <div class="robot-tags">
              <el-tag
                v-for="robotName in scope.row.robot_names || []"
                :key="robotName"
                type="success"
                size="small"
                style="margin-right: 4px; margin-bottom: 2px;"
              >
                {{ robotName }}
              </el-tag>
              <el-tag v-if="!scope.row.robot_names || scope.row.robot_names.length === 0" type="info" size="small">
                未配置
              </el-tag>
            </div>
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
            <el-tag :type="(scope.row.robot_count && scope.row.robot_count > 0) ? 'success' : 'warning'" size="small">
              {{ (scope.row.robot_count && scope.row.robot_count > 0) ? '已配置' : '未配置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="editInstanceRobots(scope.row)"
              plain
            >
              <el-icon><Edit /></el-icon>
              编辑机器人
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="viewInstanceDetail(scope.row)"
              plain
            >
              <el-icon><View /></el-icon>
              详情
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
    <el-dialog v-model="showBatchDialog" title="批量配置机器人" width="600px">
      <el-form :model="batchForm" label-width="120px">
        <el-form-item label="选择机器人">
          <div class="robot-selection">
            <div class="selection-header">
              <el-button 
                size="small" 
                @click="selectAllRobotsForBatch"
                :disabled="batchForm.robot_ids.length === robots.length"
              >
                全选
              </el-button>
              <el-button 
                size="small" 
                @click="clearAllRobotsForBatch"
                :disabled="batchForm.robot_ids.length === 0"
              >
                清空
              </el-button>
              <span class="selection-count">
                已选择 {{ batchForm.robot_ids.length }} / {{ robots.length }} 个机器人
              </span>
            </div>
            <el-select 
              v-model="batchForm.robot_ids" 
              placeholder="请选择机器人" 
              style="width: 100%; margin-top: 8px;" 
              multiple 
              collapse-tags
              collapse-tags-tooltip
              :max-collapse-tags="3"
              filterable
            >
              <el-option
                v-for="robot in robots"
                :key="robot.id"
                :label="`${robot.name} (${getRobotTypeLabel(robot.robot_type)})`"
                :value="robot.id"
              >
                <div class="robot-option">
                  <span class="robot-name">{{ robot.name }}</span>
                  <el-tag 
                    :type="getRobotTypeTagType(robot.robot_type)" 
                    size="small"
                    style="margin-left: 8px;"
                  >
                    {{ getRobotTypeLabel(robot.robot_type) }}
                  </el-tag>
                </div>
              </el-option>
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="预览配置" v-if="batchForm.robot_ids.length > 0">
          <div class="preview-robots">
            <el-tag
              v-for="robotId in batchForm.robot_ids"
              :key="robotId"
              type="success"
              size="small"
              style="margin-right: 4px; margin-bottom: 2px;"
              closable
              @close="removeRobotFromBatch(robotId)"
            >
              {{ getRobotNameById(robotId) }}
            </el-tag>
          </div>
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

    <!-- 单个实例多机器人编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑实例机器人配置" width="1000px">
      <div v-if="editingInstance">
        <el-form :model="editForm" label-width="120px">
          <el-form-item label="实例名称">
            <el-input v-model="editingInstance.instance_name" disabled />
          </el-form-item>
          <el-form-item label="">
            <el-checkbox-group v-model="editForm.robot_ids" class="robot-checkbox-group-clean">
              <el-checkbox
                v-for="robot in robots"
                :key="robot.id"
                :label="robot.id"
                class="robot-checkbox-item"
              >
                <div class="robot-checkbox-content">
                  <span class="robot-name">{{ robot.name }}</span>
                  <el-tag 
                    :type="getRobotTypeTagType(robot.robot_type)" 
                    size="small"
                    class="robot-type-tag"
                  >
                    {{ getRobotTypeLabel(robot.robot_type) }}
                  </el-tag>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveInstanceRobots" :loading="editSaving">
            保存配置
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
            <div v-if="currentInstance.robot_names && currentInstance.robot_names.length > 0">
              <el-tag
                v-for="robotName in currentInstance.robot_names"
                :key="robotName"
                type="success"
                style="margin-right: 4px; margin-bottom: 2px;"
              >
                {{ robotName }}
              </el-tag>
            </div>
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
import { Refresh, Search, View, Edit } from '@element-plus/icons-vue';
import { distributionApi, robotApi } from '../../api';
import type { InstanceMapping, Robot, AlertRecord } from '../../types';

// 响应式数据
const loading = ref(false);
const refreshLoading = ref(false);
const batchSaving = ref(false);
const editSaving = ref(false);
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
const showEditDialog = ref(false);
const currentInstance = ref<InstanceMapping | null>(null);
const editingInstance = ref<InstanceMapping | null>(null);
const instanceAlerts = ref<AlertRecord[]>([]);

// 表单数据
const batchForm = reactive({
  robot_ids: [] as number[]
});

const editForm = reactive({
  robot_ids: [] as number[]
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
        return instance.robot_count && instance.robot_count > 0;
      } else if (statusFilter.value === 'unconfigured') {
        return !instance.robot_count || instance.robot_count === 0;
      }
      return true;
    });
  }

  // 机器人过滤
  if (robotFilter.value) {
    filtered = filtered.filter(instance => 
      instance.robot_ids && instance.robot_ids.includes(robotFilter.value as number)
    );
  }

  return filtered;
});

const configuredCount = computed(() => 
  instances.value.filter(instance => instance.robot_count && instance.robot_count > 0).length
);

const unconfiguredCount = computed(() => 
  instances.value.filter(instance => !instance.robot_count || instance.robot_count === 0).length
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

const batchConfigureMapping = async () => {
  if (!batchForm.robot_ids || batchForm.robot_ids.length === 0) {
    ElMessage.warning('请选择机器人');
    return;
  }

  batchSaving.value = true;
  try {
    await distributionApi.batchConfigureMapping({
      instance_ids: selectedInstances.value.map(i => i.id),
      robot_ids: batchForm.robot_ids
    });

    // 更新本地数据
    selectedInstances.value.forEach(instance => {
      instance.robot_ids = [...batchForm.robot_ids];
      instance.robot_names = batchForm.robot_ids.map(id => {
        const robot = robots.value.find(r => r.id === id);
        return robot?.name || '';
      }).filter(Boolean);
      instance.robot_count = batchForm.robot_ids.length;
    });

    ElMessage.success('批量配置成功');
    showBatchDialog.value = false;
    selectedInstances.value = [];
    batchForm.robot_ids = [];
  } catch (error) {
    console.error('批量配置失败:', error);
    ElMessage.error('批量配置失败');
  } finally {
    batchSaving.value = false;
  }
};

const editInstanceRobots = (instance: InstanceMapping) => {
  editingInstance.value = instance;
  editForm.robot_ids = [...(instance.robot_ids || [])];
  showEditDialog.value = true;
};

const saveInstanceRobots = async () => {
  if (!editingInstance.value) return;

  editSaving.value = true;
  try {
    await distributionApi.updateInstanceMapping(editingInstance.value.id, {
      robot_ids: editForm.robot_ids
    });

    // 更新本地数据
    editingInstance.value.robot_ids = [...editForm.robot_ids];
    editingInstance.value.robot_names = editForm.robot_ids.map(id => {
      const robot = robots.value.find(r => r.id === id);
      return robot?.name || '';
    }).filter(Boolean);
    editingInstance.value.robot_count = editForm.robot_ids.length;

    ElMessage.success('配置更新成功');
    showEditDialog.value = false;
    editingInstance.value = null;
  } catch (error) {
    console.error('配置更新失败:', error);
    ElMessage.error('配置更新失败');
  } finally {
    editSaving.value = false;
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
      instance.robot_ids = [];
      instance.robot_names = [];
      instance.robot_count = 0;
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

// 机器人相关辅助方法
const getRobotNameById = (robotId: number) => {
  const robot = robots.value.find(r => r.id === robotId);
  return robot?.name || '';
};

const getRobotTypeLabel = (robotType: string) => {
  const typeMap: Record<string, string> = {
    'wechat': '企业微信',
    'feishu': '飞书',
    'dingtalk': '钉钉'
  };
  return typeMap[robotType] || robotType;
};

const getRobotTypeTagType = (robotType: string) => {
  const typeMap: Record<string, string> = {
    'wechat': 'success',
    'feishu': 'primary',
    'dingtalk': 'warning'
  };
  return typeMap[robotType] || 'info';
};

// 批量配置辅助方法
const selectAllRobotsForBatch = () => {
  batchForm.robot_ids = robots.value.map(robot => robot.id);
};

const clearAllRobotsForBatch = () => {
  batchForm.robot_ids = [];
};

const removeRobotFromBatch = (robotId: number) => {
  const index = batchForm.robot_ids.indexOf(robotId);
  if (index > -1) {
    batchForm.robot_ids.splice(index, 1);
  }
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

.robot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 24px;
  align-items: center;
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

/* 机器人选择区域样式 */
.robot-selection {
  width: 100%;
}

.selection-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.selection-count {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.robot-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.robot-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.current-robots,
.preview-robots {
  min-height: 32px;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.current-robots .text-muted {
  color: #909399;
  font-style: italic;
}

/* Checkbox 组样式 */
.robot-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
}

.robot-checkbox-group-clean {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 12px;
  padding: 0;
  border: none;
  background-color: transparent;
}

.robot-checkbox-item {
  margin: 0 !important;
  padding: 8px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #ffffff;
  transition: all 0.3s ease;
}

.robot-checkbox-item:hover {
  border-color: #409eff;
  background-color: #f0f8ff;
}

.robot-checkbox-item.is-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.robot-checkbox-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 8px;
  width: 100%;
}

.robot-checkbox-content .robot-name {
  font-weight: 500;
  color: #303133;
}

.robot-checkbox-content .robot-type-tag {
  margin-left: 8px;
}
</style>
