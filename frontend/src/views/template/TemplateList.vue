<template>
  <div class="template-list-container">
    <el-card class="template-card">
      <template #header>
        <div class="card-header">
          <h3>消息模板管理</h3>
          <el-button type="primary" @click="handleCreateTemplate">
            <el-icon><Plus /></el-icon>新建模板
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="模板名称">
            <el-input v-model="searchForm.name" placeholder="输入模板名称搜索" clearable />
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
        :data="filteredTemplates" 
        style="width: 100%" 
        border
        row-key="id"
      >
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="robot_type" label="机器人类型" width="120">
          <template #default="scope">
            <el-tag :type="getRobotTypeTagType(scope.row.robot_type)">
              {{ RobotTypeNames[scope.row.robot_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditTemplate(scope.row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="success" size="small" @click="handlePreviewTemplate(scope.row)">
              <el-icon><View /></el-icon>预览
            </el-button>
            <el-button type="danger" size="small" @click="handleDeleteTemplate(scope.row)">
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
          :total="totalTemplates"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="模板预览"
      width="60%"
    >
      <div class="preview-container">
        <div class="preview-header">
          <h4>模板内容</h4>
        </div>
        <div class="preview-code">
          <pre>{{ currentPreviewTemplate?.content }}</pre>
        </div>
        
        <div class="preview-header">
          <h4>测试数据</h4>
        </div>
        <div class="preview-data">
          <el-input
            v-model="testData"
            type="textarea"
            :rows="5"
            placeholder="输入JSON格式的测试数据"
          />
        </div>
        
        <div class="preview-header">
          <h4>预览结果</h4>
          <el-button type="primary" size="small" @click="renderPreview">
            渲染预览
          </el-button>
        </div>
        <div class="preview-result" v-html="previewResult"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTemplateStore } from '../../stores/template';
import { RobotType, RobotTypeNames, Template } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, View, Delete } from '@element-plus/icons-vue';

// 路由实例
const router = useRouter();

// 模板仓库
const templateStore = useTemplateStore();
const loading = computed(() => templateStore.loading);

// 模板数据
const templates = computed(() => templateStore.templates);

// 搜索表单
const searchForm = reactive({
  name: '',
  robot_type: ''
});

// 过滤后的模板
const filteredTemplates = computed(() => {
  return templates.value.filter(template => {
    const nameMatch = !searchForm.name || template.name.toLowerCase().includes(searchForm.name.toLowerCase());
    const typeMatch = !searchForm.robot_type || template.robot_type === searchForm.robot_type;
    return nameMatch && typeMatch;
  });
});

// 分页相关
const currentPage = ref(1);
const pageSize = ref(10);
const totalTemplates = computed(() => filteredTemplates.value.length);

// 预览相关
const previewDialogVisible = ref(false);
const currentPreviewTemplate = ref<Template | null>(null);
const testData = ref('{\n  "title": "测试标题",\n  "content": "测试内容"\n}');
const previewResult = ref('');

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

// 新建模板
const handleCreateTemplate = () => {
  router.push('/templates/create');
};

// 编辑模板
const handleEditTemplate = (template: Template) => {
  router.push(`/templates/${template.id}`);
};

// 预览模板
const handlePreviewTemplate = (template: Template) => {
  currentPreviewTemplate.value = template;
  previewResult.value = '';
  previewDialogVisible.value = true;
};

// 渲染模板预览
const renderPreview = () => {
  try {
    const data = JSON.parse(testData.value);
    // 模拟预览结果
    previewResult.value = `<div class="preview-formatted">
      <div class="preview-title">渲染后内容将发送到：${RobotTypeNames[currentPreviewTemplate.value?.robot_type || RobotType.WECHAT]}</div>
      <div class="preview-content">${currentPreviewTemplate.value?.content.replace(/\{\{\s*title\s*\}\}/g, data.title).replace(/\{\{\s*content\s*\}\}/g, data.content)}</div>
    </div>`;
  } catch (error) {
    ElMessage.error('测试数据格式无效，请确保输入正确的JSON格式');
  }
};

// 删除模板
const handleDeleteTemplate = (template: Template) => {
  ElMessageBox.confirm(
    `确定要删除模板"${template.name}"吗？删除后不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      const success = await templateStore.deleteTemplate(template.id);
      if (success) {
        ElMessage.success('删除成功');
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 组件挂载时获取模板列表
onMounted(async () => {
  await templateStore.fetchTemplates();
});
</script>

<style scoped>
.template-list-container {
  padding: 0;
  width: 100%;
}

.template-card {
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

.preview-container {
  padding: 10px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.preview-code {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.preview-code pre {
  margin: 0;
  white-space: pre-wrap;
}

.preview-data {
  margin-bottom: 15px;
}

.preview-result {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  min-height: 100px;
}

.preview-formatted {
  background-color: white;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.preview-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #409EFF;
}

.preview-content {
  white-space: pre-line;
}
</style>