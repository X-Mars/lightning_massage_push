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
            <el-select
              v-model="searchForm.robot_type"
              placeholder="请选择"
              style="width: 200px"
              clearable
            >
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
      <el-table v-loading="loading" :data="filteredRobots" style="width: 100%" border row-key="id">
        <el-table-column prop="name" label="机器人名称" />
        <el-table-column prop="english_name" label="英文名称" />
        <el-table-column prop="robot_type" label="机器人类型">
          <template #default="scope">
            <el-tag :type="getRobotTypeTagType(scope.row.robot_type)">
              {{ getRobotTypeName(scope.row.robot_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认机器人" width="120">
          <template #default="scope">
            <el-switch
              v-model="scope.row.is_default"
              active-text="是"
              inactive-text="否"
              @change="handleDefaultChange(scope.row)"
              :loading="updatingDefaultId === scope.row.id"
              style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
            />
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
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="scope">
            {{ formatToLocalTime(scope.row.updated_at) }}
          </template>
        </el-table-column>
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
    <el-dialog v-model="testDialogVisible" title="测试机器人" width="500px">
      <div class="test-container">
        <p>
          向 <b>{{ currentRobot?.name }}</b> 发送测试消息
        </p>
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

    <!-- 创建/编辑机器人对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑机器人' : '创建机器人'"
      width="60%"
      :before-close="handleDialogClose"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        v-loading="formLoading"
      >
        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-form-item label="机器人名称" prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入机器人名称"
                @input="handleNameInput"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-form-item label="机器人类型" prop="robot_type">
              <el-select
                v-model="form.robot_type"
                placeholder="请选择机器人类型"
                style="width: 100%"
              >
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

        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <el-form-item label="英文名称" prop="english_name">
              <el-input
                v-model="form.english_name"
                placeholder="请输入英文名称（可选）"
                @input="() => (userEditedEnglishName = true)"
              >
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
            <div class="placeholder-container">
              <!-- 预留空间保持布局对称 -->
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Webhook地址" prop="webhook_url">
              <el-input v-model="form.webhook_url" placeholder="请输入Webhook地址">
                <template #append>
                  <el-tooltip content="填写对应机器人平台提供的Webhook URL">
                    <el-icon><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div v-if="form.robot_type" class="help-section">
        <h4>
          <el-icon><InfoFilled /></el-icon> {{ RobotTypeNames[form.robot_type] }}机器人配置说明
        </h4>
        <div v-if="form.robot_type === 'wechat'" class="help-content">
          <p><b>企业微信机器人配置步骤：</b></p>
          <ol>
            <li>进入企业微信群聊天窗口</li>
            <li>点击右上角的设置图标</li>
            <li>选择"群机器人"选项</li>
            <li>点击"添加"按钮，创建新机器人</li>
            <li>设置机器人名称并保存</li>
            <li>复制生成的Webhook地址</li>
          </ol>
          <p>
            详细说明请参考：<a
              href="https://developer.work.weixin.qq.com/document/path/91770"
              target="_blank"
              >企业微信机器人官方文档</a
            >
          </p>
        </div>
        <div v-else-if="form.robot_type === 'feishu'" class="help-content">
          <p><b>飞书机器人配置步骤：</b></p>
          <ol>
            <li>进入飞书群聊天窗口</li>
            <li>点击右上角的设置图标</li>
            <li>点击"群机器人"</li>
            <li>选择"添加机器人"并选择"自定义机器人"</li>
            <li>设置机器人名称、头像、描述等信息</li>
            <li>复制生成的Webhook地址</li>
          </ol>
          <p>
            详细说明请参考：<a
              href="https://www.feishu.cn/hc/zh-CN/articles/360024984973"
              target="_blank"
              >飞书机器人官方文档</a
            >
          </p>
        </div>
        <div v-else-if="form.robot_type === 'dingtalk'" class="help-content">
          <p><b>钉钉机器人配置步骤：</b></p>
          <ol>
            <li>进入钉钉群聊天窗口</li>
            <li>点击右上角的设置图标</li>
            <li>点击"智能群助手"</li>
            <li>选择"添加机器人"并选择"自定义"</li>
            <li>阅读并同意服务及免责条款</li>
            <li>设置机器人名称、头像、安全设置等信息</li>
            <li>复制生成的Webhook地址</li>
          </ol>
          <p>
            详细说明请参考：<a
              href="https://open.dingtalk.com/document/robots/custom-robot-access"
              target="_blank"
              >钉钉机器人官方文档</a
            >
          </p>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleFormSubmit" :loading="formLoading">
            {{ isEdit ? '保存修改' : '创建机器人' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRobotStore } from '../../stores/robot';
import { RobotType, RobotTypeEnum, RobotTypeNames } from '../../types/index';
import type { Robot } from '../../types/index';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, ChatRound, QuestionFilled, InfoFilled } from '@element-plus/icons-vue';
import { pushApi } from '../../api';
import useClipboard from 'vue-clipboard3';
import type { FormInstance, FormRules, FormItemRule } from 'element-plus';
import { toPinyin, hasChinese } from '../../utils/pinyin';
import { handleApiError } from '../../utils/errorHandler';
import { formatToLocalTime } from '../../utils/timeFormatter';

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
  robot_type: '',
});

// 正在更新默认状态的机器人ID
const updatingDefaultId = ref<number | null>(null);

// 表单相关
const formRef = ref<FormInstance | null>(null);
const formDialogVisible = ref(false);
const formLoading = ref(false);
const isEdit = ref(false);
const currentEditId = ref<number | null>(null);

// 表单数据
const form = reactive({
  name: '',
  english_name: '',
  webhook_url: '',
  robot_type: '' as RobotType,
  is_default: false,
});

// URL验证函数
const validateUrl: FormItemRule['validator'] = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入Webhook地址'));
    return;
  }

  try {
    new URL(value);
    callback();
  } catch (_error) {
    callback(new Error('请输入有效的URL地址'));
  }
};

// 表单验证规则
const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入机器人名称', trigger: 'blur' }],
  robot_type: [{ required: true, message: '请选择机器人类型', trigger: 'change' }],
  webhook_url: [
    { required: true, message: '请输入Webhook地址', trigger: 'blur' },
    { validator: validateUrl, trigger: 'blur' },
  ],
});

// 过滤后的机器人
const filteredRobots = computed(() => {
  return robots.value.filter(robot => {
    const nameMatch =
      !searchForm.name || robot.name.toLowerCase().includes(searchForm.name.toLowerCase());
    const typeMatch = !searchForm.robot_type || robot.robot_type === searchForm.robot_type;
    return nameMatch && typeMatch;
  });
});

// 分页相关
const currentPage = ref(1);
const pageSize = ref(10);
const totalRobots = ref(0); // 后端分页时的总数

// 测试机器人相关
const testDialogVisible = ref(false);
const currentRobot = ref<Robot | null>(null);
const testForm = reactive({
  message: '这是一条测试消息，来自消息推送系统。',
});
const testLoading = ref(false);

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

// 获取机器人类型名称
const getRobotTypeName = (type: string) => {
  return RobotTypeNames[type as RobotType] || '未知类型';
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchRobotData();
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
  fetchRobotData();
};

// 页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchRobotData();
};

// 获取机器人数据
const fetchRobotData = async () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
  };
  const result = await robotStore.fetchRobots(params);
  if (result && result.total) {
    totalRobots.value = result.total;
  }
};

// 新建机器人
const handleCreateRobot = () => {
  resetForm();
  isEdit.value = false;
  currentEditId.value = null;
  formDialogVisible.value = true;
};

// 编辑机器人
const handleEditRobot = (robot: Robot) => {
  resetForm();
  isEdit.value = true;
  currentEditId.value = robot.id;

  // 填充表单
  form.name = robot.name;
  form.english_name = robot.english_name || '';
  form.webhook_url = robot.webhook_url;
  form.robot_type = robot.robot_type;
  form.is_default = robot.is_default || false;

  formDialogVisible.value = true;
};

// 重置表单
let resetForm = () => {
  form.name = '';
  form.english_name = '';
  form.webhook_url = '';
  form.robot_type = '' as RobotType;
  form.is_default = false;
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
      type: 'warning',
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

  try {
    const valid = await formRef.value.validate();
    if (valid) {
      formLoading.value = true;
      try {
        let result;

        if (isEdit.value && currentEditId.value) {
          // 更新机器人
          result = await robotStore.updateRobot(currentEditId.value, {
            name: form.name,
            english_name: form.english_name,
            webhook_url: form.webhook_url,
            robot_type: form.robot_type,
            is_default: form.is_default,
          });

          // 检查是否有错误
          if (result && !result.error) {
            formDialogVisible.value = false;
          } else if (result && result.error) {
            // 处理字段错误
            handleFieldErrors(result.fieldErrors);
          }
        } else {
          // 创建机器人
          result = await robotStore.createRobot({
            name: form.name,
            english_name: form.english_name,
            webhook_url: form.webhook_url,
            robot_type: form.robot_type,
            is_default: form.is_default,
          });

          // 检查是否有错误
          if (result && !result.error) {
            formDialogVisible.value = false;
          } else if (result && result.error) {
            // 处理字段错误
            handleFieldErrors(result.fieldErrors);
          }
        }
  } catch (error: unknown) {
        // 使用全局错误处理
        handleApiError(error, '操作失败，请重试');
      } finally {
        formLoading.value = false;
      }
    }
  } catch (validationError) {
    console.error('表单验证失败:', validationError);
  }
};

// 处理服务器返回的字段错误
const handleFieldErrors = (fieldErrors: unknown) => {
  if (!fieldErrors) return;

  // 处理英文名称错误
  const fe = fieldErrors as Record<string, unknown>;
  if ('english_name' in fe) {
    const englishErr = fe.english_name as unknown;
    const errorMsg = Array.isArray(englishErr)
      ? (englishErr as unknown[]).join(', ')
      : String(englishErr);

    ElMessage.error(`英文名称: ${errorMsg}`);

    // 直接显示错误消息而不是修改规则
    // 这可能会导致验证规则类型错误

    // 重新验证该字段
    if (formRef.value) {
      // 使用setTimeout是为了确保验证规则更新后再验证
      setTimeout(() => {
        formRef.value?.validateField('english_name', () => {});
      });
    }
  }

  // 处理其他字段错误...
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
      content: testForm.message,
    };

    // 调用后端推送接口
    await pushApi.push({
      template_id: 0, // 测试消息无模板，占位符
      robot_id: currentRobot.value.id,
      content: testData as Record<string, unknown>,
    });

    ElMessage.success('测试消息发送成功');
    testDialogVisible.value = false;
  } catch (error: unknown) {
    console.error('发送测试消息失败:', error);
    // 使用全局错误处理
    handleApiError(error, '发送测试消息失败，请检查webhook地址是否正确');
  } finally {
    testLoading.value = false;
  }
};

// 复制webhook地址
const copyWebhook = async (url: string) => {
  try {
    await toClipboard(url);
    ElMessage.success('Webhook地址已复制到剪贴板');
  } catch (_e) {
    console.error('复制失败', _e);
    ElMessage.error('复制失败，请手动复制');
  }
};

// 处理默认机器人设置变化
const handleDefaultChange = async (robot: Robot) => {
  // 保存旧值，以便发生错误时恢复
  const oldValue = !robot.is_default;

  // 标记为正在更新
  updatingDefaultId.value = robot.id;

  try {
    // 调用API更新机器人
    await robotStore.updateRobot(robot.id, {
      is_default: robot.is_default,
    });
    // 重新获取机器人列表以确保数据一致性
    await fetchRobotData();
  } catch (_error) {
    // 恢复旧值
    robot.is_default = oldValue;
    handleApiError(_error, '设置默认机器人失败');
  } finally {
    // 取消标记
    updatingDefaultId.value = null;
  }
};

// 删除机器人
const handleDeleteRobot = (robot: Robot) => {
  ElMessageBox.confirm(`确定要删除机器人"${robot.name}"吗？删除后不可恢复。`, '删除确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
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

// 处理机器人名称输入，自动转为拼音或直接填充
const handleNameInput = (value: string) => {
  // 如果英文名称未被用户手动修改过
  if (!userEditedEnglishName.value) {
    if (!value) {
      // 如果机器人名称为空，则清空英文名称
      form.english_name = '';
    } else if (hasChinese(value)) {
      // 如果包含中文，则转换为拼音（驼峰命名法）
      form.english_name = toPinyin(value);
    } else {
      // 如果是纯英文或其他字符，去空格后直接填充
      form.english_name = value.replace(/\s+/g, '');
    }
  }
};

// 跟踪英文名称是否被用户手动编辑过
const userEditedEnglishName = ref(false);

// 监听英文名称的变化，检测是否为用户手动编辑
watch(
  () => form.english_name,
  (newVal, oldVal) => {
    // 如果英文名称发生变化，且不是自动转换或直接填充引起的变化
    if (
      newVal !== oldVal &&
      newVal !== toPinyin(form.name) &&
      newVal !== form.name.replace(/\s+/g, '')
    ) {
      // 标记为用户手动编辑过
      userEditedEnglishName.value = true;
    }
  }
);

// 重置表单时，也要重置用户编辑标记
const originalResetForm = resetForm;
resetForm = () => {
  originalResetForm();
  userEditedEnglishName.value = false;
};

// 组件挂载时获取机器人列表
onMounted(async () => {
  await fetchRobotData();
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
  border-color: #409eff;
  color: #409eff;
}

.test-container {
  padding: 10px;
}

.help-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f7f9fc;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.help-section h4 {
  margin-top: 0;
  color: #409eff;
}

.help-content {
  font-size: 14px;
  line-height: 1.6;
}

.help-content p {
  margin-bottom: 10px;
}

.help-content a {
  color: #409eff;
  text-decoration: none;
}

.help-content a:hover {
  text-decoration: underline;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  gap: 10px;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.switch-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.tooltip-icon {
  font-size: 14px;
  color: #909399;
  cursor: help;
}

.tooltip-icon:hover {
  color: #409eff;
}
</style>
