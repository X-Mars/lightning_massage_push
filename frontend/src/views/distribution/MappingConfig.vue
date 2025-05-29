<template>
  <div class="mapping-container">
    <div class="page-header">
      <h2>分发绑定</h2>
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
          <el-select v-model="channelFilter" placeholder="分发通道筛选" clearable>
            <el-option
              v-for="channel in channels"
              :key="channel.id"
              :label="channel.name"
              :value="channel.id"
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
              <div class="instance-count">
                绑定通道: {{ scope.row.channel_count || 0 }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="channel_names" label="配置通道" min-width="300">
          <template #default="scope">
            <div class="channel-tags">
              <div v-if="scope.row.channel_names && scope.row.channel_names.length > 0">
                <el-tag
                  v-for="channelName in scope.row.channel_names"
                  :key="channelName"
                  type="success"
                  size="small"
                  style="margin-right: 4px; margin-bottom: 2px;"
                >
                  {{ channelName }}
                </el-tag>
              </div>
              <span v-else class="text-muted">未配置</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="source_rule" label="来源规则" width="120" show-overflow-tooltip>
          <template #default="scope">
            {{ scope.row.source_rule || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发现时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="(scope.row.channel_count && scope.row.channel_count > 0) ? 'success' : 'warning'" size="small">
              {{ (scope.row.channel_count && scope.row.channel_count > 0) ? '已配置' : '未配置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="editInstanceChannels(scope.row)"
              plain
            >
              <el-icon><Edit /></el-icon>
              配置通道
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
    <el-dialog v-model="showBatchDialog" title="批量配置分发通道" width="600px">
      <el-form :model="batchForm" label-width="120px">
        <el-form-item label="选择通道">
          <div class="channel-selection">
            <div class="selection-header">
              <el-button 
                size="small" 
                @click="selectAllChannelsForBatch"
                :disabled="batchForm.channel_ids.length === channels.length"
              >
                全选
              </el-button>
              <el-button 
                size="small" 
                @click="clearAllChannelsForBatch"
                :disabled="batchForm.channel_ids.length === 0"
              >
                清空
              </el-button>
              <span class="selection-count">
                已选择 {{ batchForm.channel_ids.length }} / {{ channels.length }} 个通道
              </span>
            </div>
            <el-checkbox-group
              v-model="batchForm.channel_ids"
              class="channel-checkbox-group"
            >
              <el-checkbox
                v-for="channel in channels"
                :key="channel.id"
                :label="channel.id"
                class="channel-checkbox-item"
              >
                <div class="channel-checkbox-content">
                  <span class="channel-name">{{ channel.name }}</span>
                  <div class="channel-info">
                    <el-tag type="info" size="small">{{ channel.robot_name }}</el-tag>
                    <el-tag type="success" size="small">{{ channel.template_name }}</el-tag>
                  </div>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>

        <el-form-item label="预览配置" v-if="batchForm.channel_ids.length > 0">
          <div class="selected-channels">
            <el-tag
              v-for="channelId in batchForm.channel_ids"
              :key="channelId"
              type="success"
              closable
              @close="removeChannelFromBatch(channelId)"
              style="margin: 0 4px 4px 0;"
            >
              {{ getChannelName(channelId) }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="选择实例">
          <div class="selected-instances">
            <el-tag 
              v-for="instance in selectedInstances" 
              :key="instance.id"
              type="primary"
              style="margin: 0 4px 4px 0;"
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
            批量配置
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑实例配置对话框 -->
    <el-dialog v-model="showEditDialog" title="配置分发通道" width="600px">
      <div v-if="editingInstance">
        <el-form :model="editForm" label-width="120px">
          <el-form-item label="实例名称">
            <el-input v-model="editingInstance.instance_name" disabled />
          </el-form-item>
          <el-form-item label="">
            <el-checkbox-group v-model="editForm.channel_ids" class="channel-checkbox-group-clean">
              <el-checkbox
                v-for="channel in channels"
                :key="channel.id"
                :label="channel.id"
                class="channel-checkbox-item"
              >
                <div class="channel-checkbox-content">
                  <span class="channel-name">{{ channel.name }}</span>
                  <div class="channel-info">
                    <el-tag type="info" size="small">{{ channel.robot_name }}</el-tag>
                    <el-tag type="success" size="small">{{ channel.template_name }}</el-tag>
                  </div>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveInstanceChannels" :loading="editSaving">
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
          <el-descriptions-item label="配置通道">
            <div v-if="currentInstance.channel_names && currentInstance.channel_names.length > 0">
              <el-tag
                v-for="channelName in currentInstance.channel_names"
                :key="channelName"
                type="success"
                style="margin-right: 4px; margin-bottom: 2px;"
              >
                {{ channelName }}
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
import { distributionApi } from '../../api';
import type { InstanceMapping, DistributionChannel, AlertRecord } from '../../types';

// 响应式数据
const loading = ref(false);
const refreshLoading = ref(false);
const batchSaving = ref(false);
const editSaving = ref(false);
const searchQuery = ref('');
const statusFilter = ref('');
const channelFilter = ref<number | ''>('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const instances = ref<InstanceMapping[]>([]);
const channels = ref<DistributionChannel[]>([]);
const selectedInstances = ref<InstanceMapping[]>([]);
const showBatchDialog = ref(false);
const showDetailDialog = ref(false);
const showEditDialog = ref(false);
const currentInstance = ref<InstanceMapping | null>(null);
const editingInstance = ref<InstanceMapping | null>(null);
const instanceAlerts = ref<AlertRecord[]>([]);

// 表单数据
const batchForm = reactive({
  channel_ids: [] as number[]
});

const editForm = reactive({
  channel_ids: [] as number[]
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
        return instance.channel_count && instance.channel_count > 0;
      } else if (statusFilter.value === 'unconfigured') {
        return !instance.channel_count || instance.channel_count === 0;
      }
      return true;
    });
  }

  // 通道过滤
  if (channelFilter.value) {
    filtered = filtered.filter(instance =>
      instance.channel_ids && instance.channel_ids.includes(channelFilter.value as number)
    );
  }

  return filtered;
});

const configuredCount = computed(() => {
  return instances.value.filter(instance => 
    instance.channel_count && instance.channel_count > 0
  ).length;
});

const unconfiguredCount = computed(() => {
  return instances.value.filter(instance => 
    !instance.channel_count || instance.channel_count === 0
  ).length;
});

// 工具方法
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN');
};

const getInstanceTagType = (instance: InstanceMapping) => {
  if (instance.channel_count && instance.channel_count > 0) {
    return 'success';
  }
  return 'warning';
};

const getChannelName = (channelId: number) => {
  const channel = channels.value.find(c => c.id === channelId);
  return channel?.name || '';
};

// 数据获取方法
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

const fetchChannels = async () => {
  try {
    const response = await distributionApi.getChannels();
    channels.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取分发通道列表失败:', error);
    ElMessage.error('获取分发通道列表失败');
  }
};

const refreshInstances = async () => {
  refreshLoading.value = true;
  try {
    await distributionApi.refreshInstances();
    ElMessage.success('实例刷新成功');
    await fetchInstances();
  } catch (error) {
    console.error('刷新实例失败:', error);
    ElMessage.error('刷新实例失败');
  } finally {
    refreshLoading.value = false;
  }
};

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  fetchInstances();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchInstances();
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1;
  // filteredInstances会自动重新计算
};

const clearFilters = () => {
  searchQuery.value = '';
  statusFilter.value = '';
  channelFilter.value = '';
};

// 选择处理
const handleSelectionChange = (selection: InstanceMapping[]) => {
  selectedInstances.value = selection;
};

// 批量操作
const batchConfigureMapping = async () => {
  if (batchForm.channel_ids.length === 0) {
    ElMessage.warning('请选择分发通道');
    return;
  }

  batchSaving.value = true;
  try {
    await distributionApi.batchConfigureMapping({
      instance_ids: selectedInstances.value.map(i => i.id),
      channel_ids: batchForm.channel_ids
    });

    // 更新本地数据
    selectedInstances.value.forEach(instance => {
      instance.channel_ids = [...batchForm.channel_ids];
      instance.channel_count = batchForm.channel_ids.length;
      instance.channel_names = batchForm.channel_ids.map(id => {
        const channel = channels.value.find(c => c.id === id);
        return channel?.name || '';
      }).filter(name => name);
    });

    ElMessage.success('批量配置成功');
    showBatchDialog.value = false;
    batchForm.channel_ids = [];
  } catch (error) {
    console.error('批量配置失败:', error);
    ElMessage.error('批量配置失败');
  } finally {
    batchSaving.value = false;
  }
};

const batchClearMapping = async () => {
  try {
    await ElMessageBox.confirm('确定要清除选中实例的分发通道配置吗？', '确认清除', {
      type: 'warning'
    });

    await distributionApi.batchClearMapping({
      instance_ids: selectedInstances.value.map(i => i.id)
    });

    // 更新本地数据
    selectedInstances.value.forEach(instance => {
      instance.channel_ids = [];
      instance.channel_count = 0;
      instance.channel_names = [];
    });

    ElMessage.success('批量清除成功');
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量清除失败:', error);
      ElMessage.error('批量清除失败');
    }
  }
};

// 单个实例操作
const editInstanceChannels = (instance: InstanceMapping) => {
  editingInstance.value = instance;
  editForm.channel_ids = [...(instance.channel_ids || [])];
  showEditDialog.value = true;
};

const saveInstanceChannels = async () => {
  if (!editingInstance.value) return;

  editSaving.value = true;
  try {
    await distributionApi.updateInstanceMapping(editingInstance.value.id, {
      channel_ids: editForm.channel_ids
    });

    // 更新本地数据
    editingInstance.value.channel_ids = [...editForm.channel_ids];
    editingInstance.value.channel_count = editForm.channel_ids.length;
    editingInstance.value.channel_names = editForm.channel_ids.map(id => {
      const channel = channels.value.find(c => c.id === id);
      return channel?.name || '';
    }).filter(name => name);

    ElMessage.success('保存成功');
    showEditDialog.value = false;
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败');
  } finally {
    editSaving.value = false;
  }
};

const viewInstanceDetail = async (instance: InstanceMapping) => {
  currentInstance.value = instance;
  
  // 获取告警历史
  try {
    const response = await distributionApi.getInstanceAlerts(instance.id);
    instanceAlerts.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取告警历史失败:', error);
    instanceAlerts.value = [];
  }
  
  showDetailDialog.value = true;
};

// 批量选择通道
const selectAllChannelsForBatch = () => {
  batchForm.channel_ids = channels.value.map(c => c.id);
};

const clearAllChannelsForBatch = () => {
  batchForm.channel_ids = [];
};

const removeChannelFromBatch = (channelId: number) => {
  const index = batchForm.channel_ids.indexOf(channelId);
  if (index > -1) {
    batchForm.channel_ids.splice(index, 1);
  }
};

// 生命周期
onMounted(() => {
  fetchInstances();
  fetchChannels();
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

.channel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 24px;
  align-items: center;
}

.selected-instances, .selected-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 8px;
  background-color: #fafafa;
}

.channel-selection {
  max-height: 300px;
  overflow-y: auto;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px 0;
  border-bottom: 1px solid #ebeef5;
}

.selection-count {
  font-size: 12px;
  color: #909399;
}

.channel-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
}

.channel-checkbox-group-clean {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 12px;
  padding: 0;
  border: none;
  background-color: transparent;
}

.channel-checkbox-item {
  margin: 0 !important;
  padding: 8px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #ffffff;
  transition: all 0.3s ease;
}

.channel-checkbox-item:hover {
  border-color: #409eff;
  background-color: #f0f8ff;
}

.channel-checkbox-item.is-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.channel-checkbox-content {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
  width: 100%;
}

.channel-checkbox-content .channel-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.channel-info {
  display: flex;
  gap: 4px;
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
  display: table !important;
}

.el-table th {
  text-align: center;
  background-color: #fafafa;
}

.el-table td {
  vertical-align: middle;
}
</style>
