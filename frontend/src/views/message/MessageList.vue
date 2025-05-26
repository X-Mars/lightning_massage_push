<template>
  <div class="message-list-container">
    <el-card class="message-card">
      <template #header>
        <div class="card-header">
          <h3>消息发送日志</h3>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="模板名称">
            <el-input v-model="searchForm.template" placeholder="输入模板名称搜索" clearable />
          </el-form-item>
          <el-form-item label="机器人名称">
            <el-input v-model="searchForm.robot" placeholder="输入机器人名称搜索" clearable />
          </el-form-item>
          <el-form-item label="发送状态">
            <el-select v-model="searchForm.status" placeholder="请选择" style="width: 200px" clearable>
              <el-option label="成功" :value="true" />
              <el-option label="失败" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item label="发送时间">
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
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
        :data="messageList" 
        style="width: 100%" 
        border
        row-key="id"
      >
        <el-table-column prop="template_name" label="模板名称" />
        <el-table-column prop="robot_name" label="机器人" />
        <el-table-column prop="created_by_username" label="发送用户" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status ? 'success' : 'danger'">
              {{ scope.row.status ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发送时间" width="180" sortable />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleViewDetail(scope.row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页区域 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="消息详情"
      width="70%"
    >
      <div v-if="currentMessage" class="message-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模板名称" label-align="right">{{ currentMessage.template_name }}</el-descriptions-item>
          <el-descriptions-item label="机器人名称" label-align="right">{{ currentMessage.robot_name }}</el-descriptions-item>
          <el-descriptions-item label="发送时间" label-align="right">{{ currentMessage.created_at }}</el-descriptions-item>
          <el-descriptions-item label="发送状态" label-align="right">
            <el-tag :type="currentMessage.status ? 'success' : 'danger'">
              {{ currentMessage.status ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发送用户" label-align="right">{{ currentMessage.created_by_username }}</el-descriptions-item>
          <el-descriptions-item label="错误信息" label-align="right" v-if="!currentMessage.status && currentMessage.error_message">
            <span class="error-message">{{ currentMessage.error_message }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider>原始数据</el-divider>
        <pre class="message-data">{{ formatJson(currentMessage.raw_data) }}</pre>
        
        <el-divider>格式化内容</el-divider>
        <div class="formatted-content">
          <div v-html="formatMessageContent(currentMessage.formatted_content)"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useMessageStore } from '../../stores/message';
import type { MessageLog } from '../../types';
import { ElMessage } from 'element-plus';
import { logApi } from '../../api';

// 消息仓库
const messageStore = useMessageStore();
const loading = computed(() => messageStore.loading);

// 消息数据
const messageList = ref<MessageLog[]>([]);
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
});

// 搜索表单
const searchForm = reactive({
  template: '',
  robot: '',
  status: null as boolean | null,
  dateRange: [] as string[]
});

// 详情对话框
const detailDialogVisible = ref(false);
const currentMessage = ref<MessageLog | null>(null);

// 搜索处理
const handleSearch = async () => {
  await fetchMessages();
};

// 重置搜索
const resetSearch = () => {
  searchForm.template = '';
  searchForm.robot = '';
  searchForm.status = null;
  searchForm.dateRange = [];
  handleSearch();
};

// 分页大小变化
const handleSizeChange = async (val: number) => {
  pagination.size = val;
  await fetchMessages();
};

// 页码变化
const handleCurrentChange = async (val: number) => {
  pagination.page = val;
  await fetchMessages();
};

// 查看消息详情
const handleViewDetail = (message: MessageLog) => {
  currentMessage.value = message;
  detailDialogVisible.value = true;
};

// 格式化JSON数据显示
const formatJson = (jsonString: string) => {
  try {
    const obj = JSON.parse(jsonString);
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    return jsonString;
  }
};

// 格式化消息内容
const formatMessageContent = (content: string) => {
  if (!content) return '';
  
  // 根据机器人类型，可能需要不同的格式化处理
  // 这里简单处理Markdown格式的内容
  return content
    .replace(/# (.*?)$/gm, '<h1>$1</h1>')
    .replace(/## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
};

// 获取消息列表
const fetchMessages = async () => {
  try {
    // 构建查询参数
    const params: any = {
      page: pagination.page,
      size: pagination.size
    };
    
    if (searchForm.template) {
      params.template = searchForm.template;
    }
    
    if (searchForm.robot) {
      params.robot = searchForm.robot;
    }
    
    if (searchForm.status !== null) {
      params.status = searchForm.status;
    }
    
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0];
      params.end_date = searchForm.dateRange[1];
    }
    
    console.log('准备获取消息列表，参数:', params);
    
    // 直接获取日志数据以便调试
    try {
      const directResponse = await logApi.getLogs(params);
      console.log('直接调用API返回结果:', directResponse);
    } catch (err) {
      console.error('直接调用API失败:', err);
    }
    
    // 传递构建的参数到 fetchLogs 方法
    const result = await messageStore.fetchLogs(params.page, params.size, { 
      template: params.template,
      robot: params.robot,
      status: params.status,
      start_date: params.start_date,
      end_date: params.end_date
    });
    console.log('Store方法返回数据:', result);
    
    if (result && Array.isArray(result.results)) {
      messageList.value = result.results;
      pagination.total = result.count || 0;
      console.log('更新后的消息列表:', messageList.value);
      
      if (messageList.value.length === 0) {
        console.warn('API返回了空数组，没有消息记录');
        ElMessage.info('没有找到符合条件的消息记录');
      }
    } else if (result && !Array.isArray(result.results)) {
      console.error('API返回的results不是数组类型:', result.results);
      ElMessage.error('数据格式错误: results应为数组');
      messageList.value = [];
    } else {
      console.warn('API返回数据格式异常或为空');
      messageList.value = [];
    }
  } catch (error) {
    ElMessage.error('获取消息列表失败');
  }
};

// 模拟数据
const mockMessages = () => {
  // 只在开发阶段使用模拟数据
  messageList.value = Array.from({ length: 15 }, (_, i) => ({
    id: i + 1,
    template: i + 1,
    template_name: `模板示例 ${i + 1}`,
    robot: i + 1,
    robot_name: `机器人 ${i % 3 === 0 ? '企业微信' : i % 3 === 1 ? '飞书' : '钉钉'}`,
    content: `{"title": "标题${i + 1}", "content": "内容${i + 1}"}`,
    raw_data: `{"title": "标题${i + 1}", "content": "内容${i + 1}"}`,
    formatted_content: `# 标题${i + 1}\n\n这是一条格式化后的消息内容，包含**加粗**和*斜体*效果。\n\n- 项目1\n- 项目2`,
    status: i % 5 !== 0, // 模拟部分失败
    error_message: i % 5 === 0 ? '推送失败：无法连接到webhook地址' : '',
    created_by: 1,
    created_by_username: 'admin',
    created_at: new Date(Date.now() - i * 3600000).toLocaleString()
  }));
  
  pagination.total = 100; // 模拟总数
};

// 组件挂载时获取消息列表
onMounted(() => {
  // 尝试获取真实数据，如果失败则使用模拟数据
  console.log('组件挂载，开始获取消息列表');
  fetchMessages().catch((error) => {
    console.error('获取消息列表失败，切换到模拟数据:', error);
    // 使用模拟数据作为备用选项
    mockMessages();
  });
});

// 监听分页或搜索条件变化
watch(
  [() => pagination.page, () => pagination.size],
  () => {
    console.log('分页参数改变，重新获取数据');
    fetchMessages().catch((error) => {
      console.error('获取消息列表失败，切换到模拟数据:', error);
      mockMessages();
    });
  }
);
</script>

<style scoped>
.message-list-container {
  padding: 0;
  width: 100%;
}

.message-card {
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

.message-detail {
  padding: 10px;
}

.message-data {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  overflow-x: auto;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.formatted-content {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  max-height: 300px;
  overflow-y: auto;
}

.error-message {
  color: #f56c6c;
}
</style>
