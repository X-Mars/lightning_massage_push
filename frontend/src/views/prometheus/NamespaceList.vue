<template>
  <div class="namespace-list-container">
    <el-card class="namespace-card">
      <template #header>
        <div class="card-header">
          <h3>命名空间管理</h3>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="命名空间">
            <el-input v-model="searchForm.namespace" placeholder="输入命名空间名称搜索" clearable />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" style="width: 150px" clearable>
              <el-option label="活跃" value="Active" />
              <el-option label="终止中" value="Terminating" />
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
        :data="namespaceData" 
        style="width: 100%" 
        border
        row-key="name"
      >
        <el-table-column prop="name" label="命名空间" min-width="200" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'Active' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creationTimestamp" label="创建时间" width="180" />
        <el-table-column prop="age" label="存在时间" width="120" />
        <el-table-column prop="podCount" label="Pod数量" width="120" />
        <el-table-column prop="serviceCount" label="Service数量" width="120" />
        <el-table-column prop="labels" label="标签" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <el-tag 
              v-for="(value, key) in scope.row.labels" 
              :key="key" 
              size="small" 
              class="label-tag"
            >
              {{ key }}={{ value }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="scope">
            <el-button type="primary" text size="small" @click="viewNamespaceDetail(scope.row)">
              详情
            </el-button>
            <el-button type="info" text size="small" @click="viewResources(scope.row)">
              资源
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
    
    <!-- 命名空间详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="命名空间详情"
      width="70%"
    >
      <div v-if="currentNamespace" class="namespace-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="名称" label-align="right">{{ currentNamespace.name }}</el-descriptions-item>
          <el-descriptions-item label="状态" label-align="right">
            <el-tag :type="currentNamespace.status === 'Active' ? 'success' : 'warning'">
              {{ currentNamespace.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" label-align="right">{{ currentNamespace.creationTimestamp }}</el-descriptions-item>
          <el-descriptions-item label="存在时间" label-align="right">{{ currentNamespace.age }}</el-descriptions-item>
          <el-descriptions-item label="Pod数量" label-align="right">{{ currentNamespace.podCount }}</el-descriptions-item>
          <el-descriptions-item label="Service数量" label-align="right">{{ currentNamespace.serviceCount }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentNamespace.labels && Object.keys(currentNamespace.labels).length > 0" class="namespace-labels">
          <h4>标签</h4>
          <el-tag 
            v-for="(value, key) in currentNamespace.labels" 
            :key="key" 
            class="label-tag"
          >
            {{ key }}: {{ value }}
          </el-tag>
        </div>
        
        <div v-if="currentNamespace.annotations && Object.keys(currentNamespace.annotations).length > 0" class="namespace-annotations">
          <h4>注解</h4>
          <div class="annotation-list">
            <div v-for="(value, key) in currentNamespace.annotations" :key="key" class="annotation-item">
              <strong>{{ key }}:</strong> {{ value }}
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 资源列表对话框 -->
    <el-dialog
      v-model="resourceDialogVisible"
      title="命名空间资源"
      width="80%"
    >
      <div v-if="currentNamespace">
        <el-tabs v-model="activeResourceTab">
          <el-tab-pane label="Pods" name="pods">
            <el-table :data="resourceData.pods" stripe>
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="status" label="状态" />
              <el-table-column prop="restarts" label="重启次数" />
              <el-table-column prop="age" label="运行时间" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="Services" name="services">
            <el-table :data="resourceData.services" stripe>
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="clusterIP" label="集群IP" />
              <el-table-column prop="externalIP" label="外部IP" />
              <el-table-column prop="ports" label="端口" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="ConfigMaps" name="configmaps">
            <el-table :data="resourceData.configmaps" stripe>
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="dataCount" label="数据项数量" />
              <el-table-column prop="age" label="创建时间" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';

// 命名空间数据接口
interface Namespace {
  name: string;
  status: string;
  creationTimestamp: string;
  age: string;
  podCount: number;
  serviceCount: number;
  labels: Record<string, string>;
  annotations?: Record<string, string>;
}

// 资源数据接口
interface ResourceData {
  pods: Array<{
    name: string;
    status: string;
    restarts: number;
    age: string;
  }>;
  services: Array<{
    name: string;
    type: string;
    clusterIP: string;
    externalIP: string;
    ports: string;
  }>;
  configmaps: Array<{
    name: string;
    dataCount: number;
    age: string;
  }>;
}

// 页面数据
const loading = ref(false);
const detailDialogVisible = ref(false);
const resourceDialogVisible = ref(false);
const currentNamespace = ref<Namespace | null>(null);
const activeResourceTab = ref('pods');

// 搜索表单
const searchForm = reactive({
  namespace: '',
  status: ''
});

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
});

// 模拟命名空间数据
const namespaceData = ref<Namespace[]>([
  {
    name: 'default',
    status: 'Active',
    creationTimestamp: '2025-05-01 10:00:00',
    age: '27d',
    podCount: 12,
    serviceCount: 3,
    labels: {
      'kubernetes.io/metadata.name': 'default'
    },
    annotations: {
      'kubernetes.io/managed-by': 'system'
    }
  },
  {
    name: 'kube-system',
    status: 'Active',
    creationTimestamp: '2025-05-01 10:00:00',
    age: '27d',
    podCount: 8,
    serviceCount: 2,
    labels: {
      'kubernetes.io/metadata.name': 'kube-system',
      'pod-security.kubernetes.io/enforce': 'privileged'
    }
  },
  {
    name: 'monitoring',
    status: 'Active',
    creationTimestamp: '2025-05-15 14:30:00',
    age: '13d',
    podCount: 5,
    serviceCount: 4,
    labels: {
      'kubernetes.io/metadata.name': 'monitoring',
      'purpose': 'monitoring'
    }
  },
  {
    name: 'test-env',
    status: 'Terminating',
    creationTimestamp: '2025-05-20 09:15:00',
    age: '8d',
    podCount: 0,
    serviceCount: 0,
    labels: {
      'kubernetes.io/metadata.name': 'test-env',
      'environment': 'test'
    }
  }
]);

// 模拟资源数据
const resourceData = ref<ResourceData>({
  pods: [
    {
      name: 'nginx-deployment-7d6dd8c95f-abc123',
      status: 'Running',
      restarts: 0,
      age: '2d'
    },
    {
      name: 'redis-server-6c7b9f8d4e-def456',
      status: 'Running',
      restarts: 1,
      age: '5d'
    }
  ],
  services: [
    {
      name: 'nginx-service',
      type: 'ClusterIP',
      clusterIP: '10.96.123.45',
      externalIP: '<none>',
      ports: '80/TCP'
    },
    {
      name: 'redis-service',
      type: 'ClusterIP',
      clusterIP: '10.96.234.56',
      externalIP: '<none>',
      ports: '6379/TCP'
    }
  ],
  configmaps: [
    {
      name: 'app-config',
      dataCount: 3,
      age: '10d'
    },
    {
      name: 'nginx-config',
      dataCount: 1,
      age: '2d'
    }
  ]
});

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
  searchForm.namespace = '';
  searchForm.status = '';
  ElMessage.info('搜索条件已重置');
};

// 查看命名空间详情
const viewNamespaceDetail = (namespace: Namespace) => {
  currentNamespace.value = namespace;
  detailDialogVisible.value = true;
};

// 查看命名空间资源
const viewResources = (namespace: Namespace) => {
  currentNamespace.value = namespace;
  activeResourceTab.value = 'pods';
  resourceDialogVisible.value = true;
  // 这里可以根据命名空间加载对应的资源数据
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
  console.log('命名空间页面已加载');
  pagination.total = namespaceData.value.length;
});
</script>

<style scoped>
.namespace-list-container {
  padding: 0;
  width: 100%;
}

.namespace-card {
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

.namespace-detail {
  padding: 10px 0;
}

.namespace-labels,
.namespace-annotations {
  margin-top: 20px;
}

.namespace-labels h4,
.namespace-annotations h4 {
  margin-bottom: 10px;
  color: #606266;
}

.label-tag {
  margin: 0 5px 5px 0;
}

.annotation-list {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.annotation-item {
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.annotation-item:last-child {
  margin-bottom: 0;
}

.annotation-item strong {
  color: #606266;
  margin-right: 5px;
}
</style>
