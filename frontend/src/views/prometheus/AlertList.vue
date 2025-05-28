<template>
  <div class="alert-list-container">
    <el-card class="alert-card">
      <template #header>
        <div class="card-header">
          <h3>告警记录</h3>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="告警名称">
            <el-input v-model="searchForm.alertName" placeholder="输入告警名称搜索" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" style="width: 150px" clearable>
              <el-option label="活跃" value="firing" />
              <el-option label="已解决" value="resolved" />
            </el-select>
          </el-form-item>
          <el-form-item label="严重程度">
            <el-select v-model="searchForm.severity" placeholder="请选择严重程度" style="width: 150px" clearable>
              <el-option label="严重" value="critical" />
              <el-option label="警告" value="warning" />
              <el-option label="信息" value="info" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 表格区域 -->
      <el-table 
        v-loading="loading" 
        :data="alertData" 
        style="width: 100%" 
        border
        row-key="id"
      >
        <el-table-column prop="alertname" label="告警名称" min-width="200" />
        <el-table-column prop="instance" label="实例" width="150" />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="scope">
            <el-tag :type="getSeverityTagType(scope.row.severity)">
              {{ getSeverityText(scope.row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'firing' ? 'danger' : 'success'">
              {{ scope.row.status === 'firing' ? '活跃' : '已解决' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180" />
        <el-table-column prop="endTime" label="结束时间" width="180" />
        <el-table-column prop="summary" label="摘要" min-width="250" show-overflow-tooltip />
        <el-table-column fixed="right" label="操作" width="120">
          <template #default="scope">
            <el-button type="primary" text size="small" @click="viewAlertDetail(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 告警详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="告警详情"
      width="70%"
    >
      <div v-if="currentAlert" class="alert-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="告警名称" label-align="right">{{ currentAlert.alertname }}</el-descriptions-item>
          <el-descriptions-item label="实例" label-align="right">{{ currentAlert.instance }}</el-descriptions-item>
          <el-descriptions-item label="严重程度" label-align="right">
            <el-tag :type="getSeverityTagType(currentAlert.severity)">
              {{ getSeverityText(currentAlert.severity) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态" label-align="right">
            <el-tag :type="currentAlert.status === 'firing' ? 'danger' : 'success'">
              {{ currentAlert.status === 'firing' ? '活跃' : '已解决' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间" label-align="right">{{ currentAlert.startTime }}</el-descriptions-item>
          <el-descriptions-item label="结束时间" label-align="right">{{ currentAlert.endTime || '仍在进行' }}</el-descriptions-item>
          <el-descriptions-item label="摘要" label-align="right" :span="2">{{ currentAlert.summary }}</el-descriptions-item>
          <el-descriptions-item label="描述" label-align="right" :span="2">{{ currentAlert.description }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentAlert.labels" class="alert-labels">
          <h4>标签</h4>
          <el-tag 
            v-for="(value, key) in currentAlert.labels" 
            :key="key" 
            class="label-tag"
          >
            {{ key }}: {{ value }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';

// 告警数据接口
interface Alert {
  id: string;
  alertname: string;
  instance: string;
  severity: string;
  status: string;
  startTime: string;
  endTime?: string;
  summary: string;
  description: string;
  labels: Record<string, string>;
}

// 页面数据
const loading = ref(false);
const detailDialogVisible = ref(false);
const currentAlert = ref<Alert | null>(null);

// 搜索表单
const searchForm = reactive({
  alertName: '',
  status: '',
  severity: ''
});

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
});

// 模拟告警数据
const alertData = ref<Alert[]>([
  {
    id: '1',
    alertname: 'HighCPUUsage',
    instance: 'web-server-01',
    severity: 'critical',
    status: 'firing',
    startTime: '2025-05-28 10:30:00',
    summary: 'CPU使用率超过90%',
    description: '服务器CPU使用率持续超过90%，可能影响系统性能',
    labels: {
      'instance': 'web-server-01',
      'job': 'node-exporter',
      'severity': 'critical'
    }
  },
  {
    id: '2',
    alertname: 'DiskSpaceLow',
    instance: 'db-server-01',
    severity: 'warning',
    status: 'firing',
    startTime: '2025-05-28 09:15:00',
    summary: '磁盘空间不足',
    description: '磁盘空间使用率超过85%，建议清理或扩容',
    labels: {
      'instance': 'db-server-01',
      'job': 'node-exporter',
      'severity': 'warning'
    }
  },
  {
    id: '3',
    alertname: 'ServiceDown',
    instance: 'api-server-02',
    severity: 'critical',
    status: 'resolved',
    startTime: '2025-05-28 08:00:00',
    endTime: '2025-05-28 08:30:00',
    summary: '服务不可用',
    description: 'API服务无法正常响应请求',
    labels: {
      'instance': 'api-server-02',
      'job': 'api-monitor',
      'severity': 'critical'
    }
  }
]);

// 获取严重程度标签类型
const getSeverityTagType = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'danger';
    case 'warning':
      return 'warning';
    case 'info':
      return 'info';
    default:
      return '';
  }
};

// 获取严重程度文本
const getSeverityText = (severity: string) => {
  switch (severity) {
    case 'critical':
      return '严重';
    case 'warning':
      return '警告';
    case 'info':
      return '信息';
    default:
      return severity;
  }
};

// 刷新数据
const refreshData = () => {
  ElMessage.success('数据已刷新');
  // 这里可以添加实际的API调用
};

// 搜索
const handleSearch = () => {
  console.log('搜索条件:', searchForm);
  ElMessage.info('搜索功能待实现');
};

// 重置搜索
const resetSearch = () => {
  searchForm.alertName = '';
  searchForm.status = '';
  searchForm.severity = '';
  ElMessage.info('搜索条件已重置');
};

// 查看告警详情
const viewAlertDetail = (alert: Alert) => {
  currentAlert.value = alert;
  detailDialogVisible.value = true;
};

// 分页相关
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.currentPage = 1;
};

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page;
};

// 组件挂载时的初始化
onMounted(() => {
  console.log('告警记录页面已加载');
  pagination.total = alertData.value.length;
});
</script>

<style scoped>
.alert-list-container {
  padding: 0;
  width: 100%;
}

.alert-card {
  margin: 0;
  width: 100%;
  border-radius: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-area {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f7f9fc;
  border-radius: 4px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.alert-detail {
  padding: 10px 0;
}

.alert-labels {
  margin-top: 20px;
}

.alert-labels h4 {
  margin-bottom: 10px;
  color: #606266;
}

.label-tag {
  margin: 0 5px 5px 0;
}
</style>
