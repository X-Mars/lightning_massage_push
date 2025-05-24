<template>
  <div class="template-form-container">
    <el-card class="template-card">
      <template #header>
        <div class="card-header">
          <h3>{{ isEdit ? '编辑模板' : '创建模板' }}</h3>
        </div>
      </template>
      
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        v-loading="loading"
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
          <div class="editor-container">
            <div class="editor-header">
              <span class="editor-tips">
                使用Jinja2语法，如: <code v-pre>{{ variable }}</code> 表示变量
              </span>
              <el-tooltip content="预览模板效果" placement="top">
                <el-button type="primary" text @click="handlePreview">
                  <el-icon><View /></el-icon> 预览
                </el-button>
              </el-tooltip>
            </div>
            <el-input 
              v-model="form.content" 
              type="textarea" 
              :rows="10" 
              placeholder="请输入模板内容，支持Jinja2语法"
              class="template-editor"
            />
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建模板' }}</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="模板预览"
      width="60%"
    >
      <div class="preview-container">
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
import { useRoute, useRouter } from 'vue-router';
import { useTemplateStore } from '../../stores/template';
import { RobotType, RobotTypeNames, Template } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { View } from '@element-plus/icons-vue';

// 路由相关
const route = useRoute();
const router = useRouter();
const id = computed(() => route.params.id ? Number(route.params.id) : null);
const isEdit = computed(() => !!id.value);

// 模板仓库
const templateStore = useTemplateStore();
const loading = computed(() => templateStore.loading);

// 表单引用
const formRef = ref<FormInstance>();

// 表单数据
const form = reactive({
  name: '',
  description: '',
  content: '',
  robot_type: '' as RobotType
});

// 表单验证规则
const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  robot_type: [{ required: true, message: '请选择机器人类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
});

// 预览相关
const previewDialogVisible = ref(false);
const testData = ref('{\n  "title": "测试标题",\n  "content": "测试内容"\n}');
const previewResult = ref('');

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value && id.value) {
          // 更新模板
          const result = await templateStore.updateTemplate(id.value, form);
          if (result) {
            ElMessage.success('更新模板成功');
            router.push('/templates');
          }
        } else {
          // 创建模板
          const result = await templateStore.createTemplate(form);
          if (result) {
            ElMessage.success('创建模板成功');
            router.push('/templates');
          }
        }
      } catch (error) {
        ElMessage.error('操作失败，请重试');
      }
    }
  });
};

// 取消操作
const handleCancel = () => {
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
      router.push('/templates');
    })
    .catch(() => {
      // 继续编辑
    });
};

// 打开预览窗口
const handlePreview = () => {
  previewResult.value = '';
  previewDialogVisible.value = true;
};

// 渲染模板预览
const renderPreview = () => {
  try {
    const data = JSON.parse(testData.value);
    // 模拟预览结果
    previewResult.value = `<div class="preview-formatted">
      <div class="preview-title">渲染后内容将发送到：${RobotTypeNames[form.robot_type || RobotType.WECHAT]}</div>
      <div class="preview-content">${form.content.replace(/\{\{\s*title\s*\}\}/g, data.title).replace(/\{\{\s*content\s*\}\}/g, data.content)}</div>
    </div>`;
  } catch (error) {
    ElMessage.error('测试数据格式无效，请确保输入正确的JSON格式');
  }
};

// 加载模板数据（编辑模式）
const loadTemplateData = async () => {
  if (isEdit.value && id.value) {
    try {
      const template = await templateStore.fetchTemplateById(id.value);
      if (template) {
        form.name = template.name;
        form.description = template.description || '';
        form.content = template.content;
        form.robot_type = template.robot_type;
      } else {
        ElMessage.error('未找到模板数据');
        router.push('/templates');
      }
    } catch (error) {
      ElMessage.error('加载模板数据失败');
      router.push('/templates');
    }
  }
};

// 组件挂载时初始化
onMounted(() => {
  loadTemplateData();
});
</script>

<style scoped>
.template-form-container {
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

.editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.editor-tips {
  font-size: 12px;
  color: #909399;
}

.template-editor {
  border: none;
}

.template-editor :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  padding: 12px;
  font-family: monospace;
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
