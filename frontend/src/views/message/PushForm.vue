<template>
  <div class="push-form-container">
    <el-card class="push-card">
      <template #header>
        <div class="card-header">
          <h3>发送消息</h3>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择模板" prop="template_id">
              <el-select
                v-model="form.template_id"
                placeholder="请选择消息模板"
                style="width: 100%"
                @change="handleTemplateChange"
              >
                <el-option
                  v-for="template in templates"
                  :key="template.id"
                  :label="template.name"
                  :value="template.id"
                >
                  <div class="template-option">
                    <span>{{ template.name }}</span>
                    <el-tag size="small" :type="getRobotTypeTagType(template.robot_type)">
                      {{ RobotTypeNames[template.robot_type] }}
                    </el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="选择机器人" prop="robot_id">
              <el-select
                v-model="form.robot_id"
                placeholder="请选择机器人"
                style="width: 100%"
                :disabled="!form.template_id"
              >
                <el-option
                  v-for="robot in filteredRobots"
                  :key="robot.id"
                  :label="robot.name"
                  :value="robot.id"
                >
                  <div class="robot-option">
                    <span>{{ robot.name }}</span>
                    <span class="robot-url">{{ robot.webhook_url }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <div class="template-preview">
              <div class="template-preview-header">
                <h4>模板内容预览</h4>
                <el-tooltip content="查看模板中可用变量" placement="top" v-if="selectedTemplate">
                  <el-button type="primary" text @click="analyzeTemplateVariables">
                    <el-icon><InfoFilled /></el-icon> 查看变量
                  </el-button>
                </el-tooltip>
              </div>
              <pre class="template-content" v-if="selectedTemplate">{{
                selectedTemplate.content
              }}</pre>
              <div class="template-content template-placeholder" v-else>
                <el-empty description="请先选择模板查看内容" :image-size="80"></el-empty>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="template-preview">
              <div class="template-preview-header">
                <h4>消息数据 (JSON格式)</h4>
                <el-tooltip content="验证JSON格式" placement="top" v-if="form.template_id">
                  <el-button type="primary" text @click="validateJsonContent">
                    <el-icon><Document /></el-icon> 验证格式
                  </el-button>
                </el-tooltip>
              </div>
              <el-input
                v-model="form.content"
                type="textarea"
                class="json-content-input"
                :rows="10"
                placeholder="请先选择模板，然后输入JSON格式的消息数据"
                :disabled="!form.template_id"
              >
                <template #prepend v-if="!form.template_id">
                  <div class="json-placeholder-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                </template>
              </el-input>
            </div>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handlePreview" :disabled="!isFormValid">预览</el-button>
          <el-button type="success" @click="handleSubmit" :disabled="!isFormValid"
            >发送消息</el-button
          >
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="消息预览" width="60%">
      <div class="preview-container">
        <div class="preview-header">
          <div>
            <h4>模板：{{ selectedTemplate?.name }}</h4>
            <p>
              机器人：{{ selectedRobot?.name }} ({{
                selectedRobot ? RobotTypeNames[selectedRobot.robot_type] : ''
              }})
            </p>
          </div>
        </div>

        <el-divider>预览结果</el-divider>
        <div class="preview-result" v-html="previewResult"></div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSendFromPreview" :loading="sending">
            确认发送
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 变量分析对话框 -->
    <el-dialog v-model="variablesDialogVisible" title="模板变量" width="500px">
      <div class="variables-container">
        <p>在以下JSON数据中使用这些变量：</p>
        <el-tag v-for="variable in templateVariables" :key="variable" class="variable-tag">
          {{ variable }}
        </el-tag>

        <div class="variables-example">
          <h5>示例数据:</h5>
          <pre class="example-json">{{ variablesExample }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useTemplateStore } from '../../stores/template';
import { useRobotStore } from '../../stores/robot';
import { useMessageStore } from '../../stores/message';
import { RobotType, RobotTypeEnum, RobotTypeNames } from '../../types';
import type { Template, Robot } from '../../types';
import { ElMessage } from 'element-plus';
import type { FormInstance, FormRules, FormItemRule } from 'element-plus';
import { InfoFilled } from '@element-plus/icons-vue';
import { Document } from '@element-plus/icons-vue';

// 存储
const templateStore = useTemplateStore();
const robotStore = useRobotStore();
const messageStore = useMessageStore();
const loading = computed(() => templateStore.loading || robotStore.loading || messageStore.loading);
const sending = ref(false);

// 模板和机器人数据
const templates = computed(() => templateStore.templates);
const robots = computed(() => robotStore.robots);

// 表单引用
const formRef = ref<FormInstance>();

// 表单数据
const form = reactive({
  template_id: undefined as number | undefined,
  robot_id: undefined as number | undefined,
  content: '{\n  \n}',
});

// JSON验证函数
const validateJson: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入消息数据'));
    return;
  }

  try {
    JSON.parse(value);
    callback();
  } catch (_error) {
    callback(new Error('请输入有效的JSON格式'));
  }
};

// 表单验证规则
const rules = reactive<FormRules>({
  template_id: [{ required: true, message: '请选择消息模板', trigger: 'change' }],
  robot_id: [{ required: true, message: '请选择机器人', trigger: 'change' }],
  content: [
    { required: true, message: '请输入消息数据', trigger: 'blur' },
    { validator: validateJson, trigger: 'blur' },
  ],
});

// 选中的模板和机器人
const selectedTemplate = ref<Template | null>(null);
const selectedRobot = ref<Robot | null>(null);

// 根据选择的模板筛选合适类型的机器人
const filteredRobots = computed(() => {
  if (!selectedTemplate.value) return [];

  console.log('筛选机器人，当前模板类型:', selectedTemplate.value.robot_type);
  console.log('当前所有机器人:', robots.value);

  const filtered = robots.value.filter(
    robot => robot.robot_type === selectedTemplate.value?.robot_type
  );

  console.log('筛选后的机器人列表:', filtered);
  return filtered;
});

// 表单是否有效
const isFormValid = computed(() => {
  return !!form.template_id && !!form.robot_id && !!form.content;
});

// 预览相关
const previewDialogVisible = ref(false);
const previewResult = ref('');

// 变量分析相关
const variablesDialogVisible = ref(false);
const templateVariables = ref<string[]>([]);
const variablesExample = ref('{}');

// 获取机器人类型标签样式
const getRobotTypeTagType = (type: RobotType) => {
  switch (type) {
    case RobotTypeEnum.WECHAT:
      return 'success';
    case RobotTypeEnum.FEISHU:
      return 'primary';
    case RobotTypeEnum.DINGTALK:
      return 'warning';
    default:
      return 'info';
  }
};

// 处理模板变更
const handleTemplateChange = async (id: number) => {
  form.robot_id = undefined; // 重置机器人选择

  const template = templates.value.find(t => t.id === id);
  selectedTemplate.value = template || null;

  console.log('选择的模板:', template);

  // 确保已加载机器人数据
  if (robots.value.length === 0) {
    console.log('机器人数据为空，重新加载');
    await robotStore.fetchRobots();
  }

  // 如果只有一个匹配的机器人，自动选择
  if (filteredRobots.value.length === 1) {
    form.robot_id = filteredRobots.value[0].id;
    selectedRobot.value = filteredRobots.value[0];
    console.log('自动选择唯一匹配的机器人:', selectedRobot.value);
  } else if (filteredRobots.value.length > 0) {
    console.log('发现多个匹配的机器人，请手动选择');
  } else {
    console.log('未找到匹配的机器人，请检查机器人类型是否与模板匹配');
    ElMessage.warning(
      `未找到与此模板匹配的 ${template ? RobotTypeNames[template.robot_type] : ''} 类型机器人`
    );
  }

  // 生成默认的JSON示例
  if (template) {
    analyzeTemplateVariables();
  }
};

// 分析模板中的变量
const analyzeTemplateVariables = () => {
  if (!selectedTemplate.value) return;

  const content = selectedTemplate.value.content;
  const variableRegex = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g;
  const vars = new Set<string>();

  let match;
  while ((match = variableRegex.exec(content)) !== null) {
    vars.add(match[1]);
  }

  templateVariables.value = Array.from(vars);

  // 生成示例JSON
  const exampleObj: Record<string, string> = {};
  templateVariables.value.forEach(v => {
    exampleObj[v] = `替换为${v}的值`;
  });

  variablesExample.value = JSON.stringify(exampleObj, null, 2);

  if (templateVariables.value.length > 0) {
    variablesDialogVisible.value = true;
  } else {
    ElMessage.info('未在模板中发现变量');
  }
};

// 预览消息
const handlePreview = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async valid => {
    if (valid) {
      try {
        const contentObj = JSON.parse(form.content);

        // 更新选中的机器人
        selectedRobot.value = robots.value.find(r => r.id === form.robot_id) || null;

        // 模拟预览结果，实际项目中应该调用后端API来渲染模板
        let result = selectedTemplate.value?.content || '';

        // 简单替换模板变量
        for (const [key, value] of Object.entries(contentObj)) {
          const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
          result = result.replace(regex, String(value));
        }

        // 格式化显示
        previewResult.value = formatMessageContent(result);

        // 显示预览对话框
        previewDialogVisible.value = true;
      } catch (_error) {
        ElMessage.error('JSON格式错误');
      }
    }
  });
};

// 验证 JSON 格式
const validateJsonContent = () => {
  try {
    const jsonObject = JSON.parse(form.content);
    // 格式化后的 JSON，保持良好的缩进
    form.content = JSON.stringify(jsonObject, null, 2);
    ElMessage.success('JSON 格式有效！');

    // 检查是否包含模板中所需的所有变量
    if (selectedTemplate.value) {
      // 分析模板变量
      const content = selectedTemplate.value.content;
      const variableRegex = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g;
      const templateVars = new Set<string>();

      let match;
      while ((match = variableRegex.exec(content)) !== null) {
        templateVars.add(match[1]);
      }

      // 检查 JSON 是否包含所有变量
      const missingVars: string[] = [];
      templateVars.forEach(v => {
        if (!(v in jsonObject)) {
          missingVars.push(v);
        }
      });

      // 如果有缺失的变量，提示用户
      if (missingVars.length > 0) {
        ElMessage.warning(`JSON 缺少以下模板变量: ${missingVars.join(', ')}`);
      }
    }
  } catch (_error) {
    if (_error instanceof Error) {
      ElMessage.error(`JSON 格式错误: ${_error.message}`);
    } else {
      ElMessage.error('JSON 格式无效');
    }
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

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async valid => {
    if (valid) {
      // 先预览，再确认发送
      handlePreview();
    }
  });
};

// 从预览对话框发送消息
const handleSendFromPreview = async () => {
  sending.value = true;

  try {
    const contentObj = JSON.parse(form.content);

    // 调用发送API
    const result = await messageStore.pushMessage({
      template_id: form.template_id!,
      robot_id: form.robot_id!,
      content: contentObj,
    });

    if (result) {
      ElMessage.success('消息发送成功');
      previewDialogVisible.value = false;

      // 清空表单
      form.content = '{\n  \n}';
    }
  } catch (_error) {
    ElMessage.error('消息发送失败');
  } finally {
    sending.value = false;
  }
};

// 组件挂载时初始化
onMounted(async () => {
  // 获取模板和机器人列表
  try {
    // 先加载模板
    await templateStore.fetchTemplates();
    console.log('加载的模板数据:', templates.value);

    // 然后加载机器人
    const robotsData = await robotStore.fetchRobots();
    console.log('加载的机器人数据:', robotsData);

    if (robots.value.length === 0) {
      console.warn('机器人列表为空，这可能导致选择机器人的下拉框没有数据');
      ElMessage.warning('未找到可用的机器人，请先添加机器人');
    }
  } catch (_error) {
    console.error('加载数据失败:', _error);
    ElMessage.error('加载机器人或模板数据失败');
  }
});
</script>

<style scoped>
.push-form-container {
  padding: 0;
  width: 100%;
}

.push-card {
  margin: 0;
  width: 100%;
  border-radius: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-option,
.robot-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.robot-url {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.template-preview {
  margin: 15px 0;
  background-color: #f7f9fc;
  border-radius: 4px;
  padding: 15px;
  border: 1px solid #ebeef5;
}

.template-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.template-preview-header h4 {
  margin: 0;
}

.template-content {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  font-family: monospace;
  white-space: pre-wrap;
  height: 265px;
  overflow-y: auto;
}

.template-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fafafa;
}

.preview-container {
  padding: 10px;
}

.preview-header {
  margin-bottom: 15px;
}

.preview-header h4,
.preview-header p {
  margin: 5px 0;
}

.preview-result {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  min-height: 100px;
  max-height: 300px;
  overflow-y: auto;
}

.variables-container {
  padding: 10px;
}

.variable-tag {
  margin: 5px;
}

.variables-example {
  margin-top: 20px;
}

.variables-example h5 {
  margin-bottom: 10px;
}

.example-json {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
}

/* JSON输入框样式 */
:deep(.json-content-input .el-textarea__inner) {
  background-color: #fff;
  font-family: monospace;
  white-space: pre-wrap;
  height: 265px !important; /* 确保与模板预览区域高度一致 */
  resize: none;
}
</style>
