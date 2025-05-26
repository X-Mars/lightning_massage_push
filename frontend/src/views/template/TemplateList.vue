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
              {{ getRobotTypeName(scope.row.robot_type) }}
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
    
    <!-- 创建/编辑模板对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑模板' : '创建模板'"
      width="70%"
      :before-close="handleDialogClose"
    >
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        v-loading="formLoading"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入模板名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="适用机器人类型" prop="robot_type">
              <el-select v-model="form.robot_type" placeholder="请选择机器人类型" style="width: 100%">
                <el-option
                  v-for="(name, type) in RobotTypeNames"
                  :key="type"
                  :label="name"
                  :value="type"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="模板描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入模板描述"
          />
        </el-form-item>
        
        <el-form-item label="模板内容" prop="content">
          <el-row :gutter="20">
            <!-- 左侧编辑器 -->
            <el-col :span="12">
              <div class="editor-container">
                <div class="editor-header">
                  <span class="editor-tips">
                    使用Jinja2语法，如: <code v-pre>{{ variable }}</code> 表示变量
                  </span>
                </div>
                <el-input 
                  v-model="form.content" 
                  type="textarea" 
                  placeholder="请输入模板内容，支持Jinja2语法"
                  class="template-editor"
                  @input="renderLivePreview"
                />
              </div>
            </el-col>
            
            <!-- 右侧预览 -->
            <el-col :span="12">
              <div class="preview-container">
                <div class="preview-header">
                  <span class="preview-title">实时预览</span>
                  <div>
                    <el-form :inline="true" class="preview-controls">
                      <el-form-item label="测试数据">
                        <el-select v-model="previewDataType" size="small" style="width: 150px" @change="renderLivePreview">
                          <el-option label="标准示例数据" value="standard" />
                          <el-option label="自定义数据" value="custom" />
                        </el-select>
                      </el-form-item>
                    </el-form>
                  </div>
                </div>
                
                <div v-if="previewDataType === 'custom'" class="preview-data">
                  <el-input
                    v-model="formTestData"
                    type="textarea"
                    :rows="3"
                    placeholder="输入JSON格式的测试数据"
                    @input="renderLivePreview"
                  />
                </div>
                
                <div class="preview-output">
                  <div class="preview-type">
                    <!-- <el-tag :type="getRobotTypeTagType(form.robot_type)" effect="plain" v-if="form.robot_type">
                      {{ RobotTypeNames[form.robot_type] }}
                    </el-tag> -->
                  </div>
                  <div class="preview-content-wrapper">
                    <div class="preview-result" v-html="formPreviewResult"></div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleFormSubmit">
            {{ isEdit ? '保存修改' : '创建模板' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 不再需要单独的表单预览对话框 -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useTemplateStore } from '../../stores/template';
import { RobotType, RobotTypeNames } from '../../types';
import type { Template } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, View, Delete } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { marked } from 'marked';

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
const totalTemplates = ref(0); // 后端分页时的总数

// 预览相关
const previewDialogVisible = ref(false);
const currentPreviewTemplate = ref<Template | null>(null);
const testData = ref('{\n  "title": "测试标题",\n  "content": "测试内容"\n}');
const previewResult = ref('');

// 表单相关
const formRef = ref<FormInstance>();
const formDialogVisible = ref(false);
const formLoading = ref(false);
const isEdit = ref(false);
const currentEditId = ref<number | null>(null);

// 表单数据
const form = reactive({
  name: '',
  description: '',
  content: '',
  robot_type: '' as RobotType
});

// 表单预览相关
const formTestData = ref('{\n  "title": "测试标题",\n  "content": "测试内容"\n}');
const formPreviewResult = ref('');
const previewDataType = ref('standard'); // 预览数据类型: standard 或 custom

// 表单验证规则
const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  robot_type: [{ required: true, message: '请选择机器人类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
});

// 获取机器人类型标签样式
const getRobotTypeTagType = (type: string) => {
  switch (type) {
    case 'wechat':
      return 'success';
    case 'feishu':
      return 'primary';
    case 'dingtalk':
      return 'warning';
    default:
      return 'info';
  }
};

// 获取机器人类型名称
const getRobotTypeName = (type: string) => {
  return RobotTypeNames[type as keyof typeof RobotTypeNames] || '未知类型';
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchTemplateData();
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
  fetchTemplateData();
};

// 页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchTemplateData();
};

// 获取模板数据
const fetchTemplateData = async () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value
  };
  const result = await templateStore.fetchTemplates(params);
  if (result && result.total) {
    totalTemplates.value = result.total;
  }
};

// 新建模板
const handleCreateTemplate = () => {
  resetForm();
  isEdit.value = false;
  currentEditId.value = null;
  formDialogVisible.value = true;
  // 延迟一下再渲染预览，确保表单已经重置
  setTimeout(() => renderLivePreview(), 100);
};

// 编辑模板
const handleEditTemplate = (template: Template) => {
  resetForm();
  isEdit.value = true;
  currentEditId.value = template.id;
  
  // 填充表单
  form.name = template.name;
  form.description = template.description || '';
  form.content = template.content;
  form.robot_type = template.robot_type;
  
  formDialogVisible.value = true;
  // 延迟一下再渲染预览，确保表单已经填充
  setTimeout(() => renderLivePreview(), 100);
};

// 重置表单
const resetForm = () => {
  form.name = '';
  form.description = '';
  form.content = '';
  form.robot_type = '' as RobotType;
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

// 关闭对话框
const handleDialogClose = () => {
  ElMessageBox.confirm(
    '确认放弃当前编辑？未保存的内容将会丢失。',
    isEdit.value ? '放弃编辑' : '放弃创建',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      formDialogVisible.value = false;
    })
    .catch(() => {
      // 继续编辑
    });
};

// 提交表单
const handleFormSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      formLoading.value = true;
      try {
        let success = false;
        
        if (isEdit.value && currentEditId.value) {
          // 更新模板
          success = await templateStore.updateTemplate(currentEditId.value, {
            name: form.name,
            description: form.description,
            content: form.content,
            robot_type: form.robot_type as RobotType
          });
          
          if (success) {
            ElMessage.success('更新模板成功');
            formDialogVisible.value = false;
          }
        } else {
          // 创建模板
          success = await templateStore.createTemplate({
            name: form.name,
            description: form.description,
            content: form.content,
            robot_type: form.robot_type as RobotType
          });
          
          if (success) {
            ElMessage.success('创建模板成功');
            formDialogVisible.value = false;
          }
        }
      } catch (error) {
        ElMessage.error('操作失败，请重试');
      } finally {
        formLoading.value = false;
      }
    }
  });
};

// 根据机器人类型渲染内容
const renderContentByRobotType = (content: string, robotType: RobotType) => {
  try {
    // 企业微信和钉钉都使用Markdown格式，飞书使用富文本
    if (robotType === RobotType.WECHAT || robotType === RobotType.DINGTALK) {
      // 使用marked库渲染Markdown
      // 设置配置选项
      const options = {
        breaks: true, // 启用换行
        gfm: true,    // 启用GitHub风格Markdown
      };
      
      return marked.parse(content, options);
    } else if (robotType === RobotType.FEISHU) {
      // 飞书的interactive卡片格式，目前简单处理
      // 1. 处理标题
      let processedContent = content
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>');
      
      // 2. 处理列表
      processedContent = processedContent
        .replace(/^\* (.*$)/gm, '<ul><li>$1</li></ul>')
        .replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>')
        .replace(/^(\d+)\. (.*$)/gm, '<ol><li>$2</li></ol>');
      
      // 3. 处理粗体和斜体
      processedContent = processedContent
        .replace(/\*\*(.*)\*\*/gm, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gm, '<em>$1</em>')
        .replace(/\_(.*)\_/gm, '<em>$1</em>');
      
      // 4. 处理链接
      processedContent = processedContent
        .replace(/\[([^\]]+)\]\(([^)]+)\)/gm, '<a href="$2">$1</a>');
      
      // 5. 处理换行
      processedContent = processedContent.replace(/\n/g, '<br>');
      
      return processedContent;
    }
    // 默认情况下返回带换行的内容
    return content.replace(/\n/g, '<br>');
  } catch (error) {
    console.error('渲染内容时出错:', error);
    // 发生错误时，至少确保换行可以正常工作
    return content.replace(/\n/g, '<br>');
  }
};

// 实时渲染预览
const renderLivePreview = () => {
  try {
    let data;
    if (previewDataType.value === 'standard') {
      // 使用标准示例数据
      data = { 
        title: "测试标题", 
        content: "测试内容",
        time: new Date().toLocaleString(),
        status: "成功",
        user: "系统管理员"
      };
    } else {
      // 使用自定义数据
      data = JSON.parse(formTestData.value);
    }
    
    // 生成预览结果
    if (form.content && form.robot_type) {
      let previewContent = form.content;
      // 替换模板中的变量
      Object.keys(data).forEach(key => {
        const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
        previewContent = previewContent.replace(regex, data[key]);
      });
      
      // 根据机器人类型渲染内容
      const renderedContent = renderContentByRobotType(previewContent, form.robot_type);
      
      formPreviewResult.value = `<div class="preview-formatted">
        <div class="preview-content">${renderedContent}</div>
      </div>`;
    } else {
      formPreviewResult.value = '<div class="preview-empty">请输入模板内容和选择机器人类型</div>';
    }
  } catch (error) {
    formPreviewResult.value = '<div class="preview-error">数据格式错误，请检查JSON格式</div>';
  }
};

// 实时预览文档已经处理了预览逻辑，不再需要额外的预览函数

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
    
    // 获取模板内容并处理变量替换
    let previewContent = currentPreviewTemplate.value?.content || '';
    const robotType = currentPreviewTemplate.value?.robot_type || RobotType.WECHAT;
    
    // 替换所有变量
    Object.keys(data).forEach(key => {
      const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
      previewContent = previewContent.replace(regex, data[key]);
    });
    
    // 根据机器人类型渲染内容
    const renderedContent = renderContentByRobotType(previewContent, robotType);
    
    // 模拟预览结果
    previewResult.value = `<div class="preview-formatted">
      <div class="preview-title">渲染后内容将发送到：${RobotTypeNames[robotType]}</div>
      <div class="preview-content">${renderedContent}</div>
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
  await fetchTemplateData();
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

/* 表单预览容器，用于实时预览 */
.el-form-item .preview-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
  margin-top: 0; /* 与左侧编辑器上边缘对齐 */
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  height: 42px; /* 与editor-header高度保持一致 */
  box-sizing: border-box;
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

.preview-content-wrapper {
  flex: 1;
  overflow-y: auto;
  min-height: 300px;
  max-height: 400px;
}

.preview-content {
  white-space: normal; /* 改为normal以便让<br>标签正常工作 */
  line-height: 1.6; /* 增加行高，提高可读性 */
}

/* Markdown样式 */
.preview-content :deep(h1) {
  font-size: 1.8em;
  margin-top: 0.8em;
  margin-bottom: 0.6em;
}

.preview-content :deep(h2) {
  font-size: 1.5em;
  margin-top: 0.7em;
  margin-bottom: 0.5em;
}

.preview-content :deep(h3) {
  font-size: 1.3em;
  margin-top: 0.6em;
  margin-bottom: 0.4em;
}

.preview-content :deep(h4) {
  font-size: 1.2em;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

.preview-content :deep(p) {
  margin-bottom: 0.8em;
}

.preview-content :deep(ul), .preview-content :deep(ol) {
  padding-left: 2em;
  margin-bottom: 0.8em;
}

.preview-content :deep(li) {
  margin-bottom: 0.3em;
}

.preview-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

.preview-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 1em;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 1em;
  color: #666;
  margin-left: 0;
  margin-right: 0;
}

.preview-content :deep(a) {
  color: #409EFF;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.preview-content :deep(th), .preview-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.preview-content :deep(th) {
  background-color: #f2f2f2;
}

.preview-controls {
  margin: 0;
  padding: 0;
}

.preview-controls .el-form-item {
  margin-bottom: 0;
}

.preview-output {
  background-color: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  height: calc(100% - 30px); /* 减去padding的高度 */
  display: flex;
  flex-direction: column;
}

.preview-type {
  margin-bottom: 10px;
}

.preview-empty {
  color: #909399;
  font-style: italic;
  padding: 20px 0;
  text-align: center;
}

.preview-error {
  color: #f56c6c;
  padding: 20px 0;
  text-align: center;
}

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  height: 42px; /* 固定高度 */
  box-sizing: border-box;
}

.editor-tips {
  font-size: 12px;
  color: #909399;
}

.preview-title {
  font-size: 12px;
  color: #909399;
}

.template-editor {
  border: none;
}

.template-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.template-editor :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  padding: 12px;
  font-family: monospace;
  height: 100%; /* 填满容器高度 */
  resize: none; /* 禁止手动调整大小 */
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  gap: 10px;
}
</style>