<template>
  <div class="robot-list-container">
    <el-card class="robot-card">
      <template #header>
        <div class="card-header">
          <h3>机器人配置管理</h3>
          <el-button type="primary" @click="handleCreateRobot">
            <el-icon><Plus /></el-icon>新建机器人
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="机器人名称">
            <el-input v-model="searchForm.name" placeholder="输入名称搜索" clearable />
          </el-form-item>
          <el-form-item label="机器人类型">
            <el-select v-model="searchForm.robot_type" placeholder="请选择" style="width: 200px" clearable>
              <el-option
                v-for="(name, type) in RobotTypeNames"
                :key="type"
                :label="name"
                :value="type"
              />
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
        :data="filteredRobots" 
        style="width: 100%" 
        border
        row-key="id"
      >
        <el-table-column prop="name" label="机器人名称" />
        <el-table-column prop="robot_type" label="机器人类型">
          <template #default="scope">
            <el-tag :type="getRobotTypeTagType(scope.row.robot_type)">
              {{ getRobotTypeName(scope.row.robot_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="webhook_url" label="Webhook地址 (点击复制)" min-width="250px">
          <template #default="scope">
            <div class="webhook-url">
              <div 
                class="webhook-url-text"
                @click="copyWebhook(scope.row.webhook_url)"
                title="点击复制 Webhook 地址"
              >
                {{ scope.row.webhook_url }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditRobot(scope.row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" size="small" @click="handleTestRobot(scope.row)">
              <el-icon><ChatRound /></el-icon>测试
            </el-button>
            <el-button type="danger" size="small" @click="handleDeleteRobot(scope.row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页区域 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalRobots"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 测试机器人对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试机器人"
      width="500px"
    >
      <div class="test-container">
        <p>向 <b>{{ currentRobot?.name }}</b> 发送测试消息</p>
        <el-form :model="testForm" label-position="top">
          <el-form-item label="测试消息内容">
            <el-input
              v-model="testForm.message"
              type="textarea"
              :rows="5"
              placeholder="输入要发送的测试消息"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="testDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="sendTestMessage" :loading="testLoading">
            发送测试消息
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useRobotStore } from '../../stores/robot';
import { RobotType, RobotTypeNames } from '../../types/index';
import type { Robot } from '../../types/index';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, ChatRound } from '@element-plus/icons-vue';
import { pushApi } from '../../api';
import useClipboard from 'vue-clipboard3';

// 路由实例
const router = useRouter();

// 初始化剪贴板
const { toClipboard } = useClipboard();

// 机器人仓库
const robotStore = useRobotStore();
const loading = computed(() => robotStore.loading);

// 机器人数据
const robots = computed(() => robotStore.robots);

// 搜索表单
const searchForm = reactive({
  name: '',
  robot_type: ''
});

// 过滤后的机器人
const filteredRobots = computed(() => {
  return robots.value.filter(robot => {
    const nameMatch = !searchForm.name || robot.name.toLowerCase().includes(searchForm.name.toLowerCase());
    const typeMatch = !searchForm.robot_type || robot.robot_type === searchForm.robot_type;
    return nameMatch && typeMatch;
  });
});

// 分页相关
const currentPage = ref(1);
const pageSize = ref(10);
const totalRobots = computed(() => filteredRobots.value.length);

// 测试机器人相关
const testDialogVisible = ref(false);
const currentRobot = ref<Robot | null>(null);
const testForm = reactive({
  message: '这是一条测试消息，来自消息推送系统。'
});
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
const getRobotTypeName = (type: string) => {
  return RobotTypeNames[type as RobotType] || '未知类型';
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1;
};

// 重置搜索
const resetSearch = () => {
  searchForm.name = '';
  searchForm.robot_type = '';
  handleSearch();
};

// 分页大小变化
const handleSizeChange = (val: number) => {
  pageSize.value = val;
};

// 页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
};

// 新建机器人
const handleCreateRobot = () => {
  router.push('/robots/create');
};

// 编辑机器人
const handleEditRobot = (robot: Robot) => {
  router.push(`/robots/${robot.id}`);
};

// 测试机器人
const handleTestRobot = (robot: Robot) => {
  currentRobot.value = robot;
  testDialogVisible.value = true;
};

// 发送测试消息
const sendTestMessage = async () => {
  if (!currentRobot.value) return;
  
  testLoading.value = true;
  
  try {
    // 准备测试数据
    const testData = {
      title: '测试消息',
      content: testForm.message
    };
    
    // 调用后端推送接口
    await pushApi.push({
      robot_id: currentRobot.value.id,
      content: testData,
      direct_content: testForm.message, // 直接发送的内容
      test_mode: true // 标记为测试模式
    });
    
    ElMessage.success('测试消息发送成功');
    testDialogVisible.value = false;
    
  } catch (error: any) {
    console.error('发送测试消息失败:', error);
    const errorMsg = error.response?.data?.error || '发送测试消息失败，请检查webhook地址是否正确';
    ElMessage.error(errorMsg);
  } finally {
    testLoading.value = false;
  }
};

// 复制webhook地址
const copyWebhook = async (url: string) => {
  try {
    await toClipboard(url);
    ElMessage.success('Webhook地址已复制到剪贴板');
  } catch (e) {
    console.error('复制失败', e);
    ElMessage.error('复制失败，请手动复制');
  }
};

// 删除机器人
const handleDeleteRobot = (robot: Robot) => {
  ElMessageBox.confirm(
    `确定要删除机器人"${robot.name}"吗？删除后不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      const success = await robotStore.deleteRobot(robot.id);
      if (success) {
        ElMessage.success('删除成功');
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 组件挂载时获取机器人列表
onMounted(async () => {
  await robotStore.fetchRobots();
});
</script>

<style scoped>
.robot-list-container {
  padding: 0;
  width: 100%;
}

.robot-card {
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

.webhook-url {
  display: flex;
  align-items: center;
}

.webhook-url-text {
  flex: 1;
  font-size: 12px;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: all 0.3s;
  color: #606266;
  border: 1px dashed transparent;
}

.webhook-url-text:hover {
  background-color: #e6f1fc;
  text-decoration: underline;
  border-color: #409EFF;
  color: #409EFF;
}

.test-container {
  padding: 10px;
}
</style>
