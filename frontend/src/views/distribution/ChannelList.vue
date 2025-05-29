<template>
  <div class="channels-container">
    <div class="page-header">
      <h2>分发通道管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建通道
      </el-button>
    </div>

    <!-- 分发通道列表 -->
    <el-card>
      <el-table :data="channels" v-loading="loading" stripe>
        <el-table-column prop="name" label="通道名称" width="200" />
        <el-table-column prop="robot_name" label="绑定机器人" width="180">
          <template #default="scope">
            <el-tag :type="getRobotTypeTagType(scope.row.robot_type)" size="small">
              {{ scope.row.robot_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="template_name" label="绑定模板" width="180">
          <template #default="scope">
            <el-tag type="info" size="small">
              {{ scope.row.template_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="scope">
            <el-switch
              v-model="scope.row.is_active"
              @change="toggleChannelStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editChannel(scope.row)" plain>
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteChannel(scope.row)" plain>
              <el-icon><Delete /></el-icon>
              删除
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

    <!-- 创建/编辑通道对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingChannel ? '编辑通道' : '创建通道'"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="channelFormRef"
        :model="channelForm"
        :rules="channelFormRules"
        label-width="120px"
      >
        <el-form-item label="通道名称" prop="name">
          <el-input v-model="channelForm.name" placeholder="请输入通道名称" />
        </el-form-item>

        <el-form-item label="选择机器人" prop="robot">
          <el-select
            v-model="channelForm.robot"
            placeholder="请选择机器人"
            filterable
            style="width: 100%"
            @change="onRobotChange"
          >
            <el-option
              v-for="robot in robots"
              :key="robot.id"
              :label="robot.name"
              :value="robot.id"
            >
              <div class="robot-option">
                <span>{{ robot.name }}</span>
                <el-tag 
                  :type="getRobotTypeTagType(robot.robot_type)" 
                  size="small"
                  style="margin-left: 8px;"
                >
                  {{ getRobotTypeLabel(robot.robot_type) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择模板" prop="template">
          <el-select
            v-model="channelForm.template"
            placeholder="请选择模板"
            filterable
            style="width: 100%"
            :disabled="!channelForm.robot"
          >
            <el-option
              v-for="template in filteredTemplates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            >
              <div class="template-option">
                <span>{{ template.name }}</span>
                <el-tag type="info" size="small" style="margin-left: 8px;">
                  {{ getRobotTypeLabel(template.robot_type) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip" v-if="channelForm.robot">
            <el-icon><InfoFilled /></el-icon>
            只显示与选中机器人类型匹配的模板
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="channelForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入通道描述"
          />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="channelForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="saveChannel" :loading="saving">
            {{ editingChannel ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, InfoFilled } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { distributionApi, robotApi, templateApi } from '../../api';
import type { DistributionChannel, Robot, Template } from '../../types';

// 响应式数据
const loading = ref(false);
const saving = ref(false);
const showCreateDialog = ref(false);
const editingChannel = ref<DistributionChannel | null>(null);
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 数据列表
const channels = ref<DistributionChannel[]>([]);
const robots = ref<Robot[]>([]);
const templates = ref<Template[]>([]);

// 表单相关
const channelFormRef = ref<FormInstance>();
const channelForm = reactive<Partial<DistributionChannel>>({
  name: '',
  robot: undefined,
  template: undefined,
  description: '',
  is_active: true
});

const channelFormRules: FormRules = {
  name: [
    { required: true, message: '请输入通道名称', trigger: 'blur' }
  ],
  robot: [
    { required: true, message: '请选择机器人', trigger: 'change' }
  ],
  template: [
    { required: true, message: '请选择模板', trigger: 'change' }
  ]
};

// 计算属性 - 根据选中的机器人筛选模板
const filteredTemplates = computed(() => {
  if (!channelForm.robot) return [];
  
  const selectedRobot = robots.value.find(r => r.id === channelForm.robot);
  if (!selectedRobot) return [];
  
  return templates.value.filter(t => t.robot_type === selectedRobot.robot_type);
});

// 工具方法
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN');
};

const getRobotTypeLabel = (robotType: string) => {
  const typeMap: Record<string, string> = {
    'dingtalk': '钉钉',
    'wechat': '企业微信',
    'feishu': '飞书',
    'webhook': 'Webhook'
  };
  return typeMap[robotType] || robotType;
};

const getRobotTypeTagType = (robotType: string) => {
  const typeMap: Record<string, string> = {
    'dingtalk': 'primary',
    'wechat': 'success',
    'feishu': 'warning',
    'webhook': 'info'
  };
  return typeMap[robotType] || 'info';
};

// 数据获取方法
const fetchChannels = async () => {
  loading.value = true;
  try {
    const response = await distributionApi.getChannels({
      page: currentPage.value,
      page_size: pageSize.value
    });
    
    channels.value = response.data.results || response.data;
    total.value = response.data.count || response.data.length;
  } catch (error) {
    console.error('获取分发通道列表失败:', error);
    ElMessage.error('获取分发通道列表失败');
  } finally {
    loading.value = false;
  }
};

const fetchRobots = async () => {
  try {
    const response = await robotApi.getRobots();
    robots.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取机器人列表失败:', error);
    ElMessage.error('获取机器人列表失败');
  }
};

const fetchTemplates = async () => {
  try {
    const response = await templateApi.getTemplates();
    templates.value = response.data.results || response.data;
  } catch (error) {
    console.error('获取模板列表失败:', error);
    ElMessage.error('获取模板列表失败');
  }
};

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  fetchChannels();
};

const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  fetchChannels();
};

// 对话框处理
const handleDialogClose = () => {
  showCreateDialog.value = false;
  editingChannel.value = null;
  resetForm();
};

const resetForm = () => {
  if (channelFormRef.value) {
    channelFormRef.value.resetFields();
  }
  Object.assign(channelForm, {
    name: '',
    robot: undefined,
    template: undefined,
    description: '',
    is_active: true
  });
};

// 机器人选择变化处理
const onRobotChange = () => {
  // 当机器人改变时，清空模板选择
  channelForm.template = undefined;
};

// 保存通道
const saveChannel = async () => {
  if (!channelFormRef.value) return;
  
  try {
    await channelFormRef.value.validate();
    saving.value = true;
    
    if (editingChannel.value) {
      await distributionApi.updateChannel(editingChannel.value.id!, channelForm);
      ElMessage.success('通道更新成功');
    } else {
      await distributionApi.createChannel(channelForm);
      ElMessage.success('通道创建成功');
    }
    
    handleDialogClose();
    fetchChannels();
  } catch (error) {
    console.error('保存通道失败:', error);
    ElMessage.error('保存通道失败');
  } finally {
    saving.value = false;
  }
};

// 编辑通道
const editChannel = (channel: DistributionChannel) => {
  editingChannel.value = channel;
  Object.assign(channelForm, {
    name: channel.name,
    robot: channel.robot,
    template: channel.template,
    description: channel.description,
    is_active: channel.is_active
  });
  showCreateDialog.value = true;
};

// 删除通道
const deleteChannel = async (channel: DistributionChannel) => {
  try {
    await ElMessageBox.confirm('确定要删除此通道吗？', '确认删除', {
      type: 'warning'
    });
    
    await distributionApi.deleteChannel(channel.id!);
    ElMessage.success('删除成功');
    fetchChannels();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 切换通道状态
const toggleChannelStatus = async (channel: DistributionChannel) => {
  try {
    await distributionApi.updateChannel(channel.id!, { is_active: channel.is_active });
    ElMessage.success('状态更新成功');
  } catch (error) {
    channel.is_active = !channel.is_active; // 回滚状态
    console.error('状态更新失败:', error);
    ElMessage.error('状态更新失败');
  }
};

// 生命周期
onMounted(() => {
  fetchChannels();
  fetchRobots();
  fetchTemplates();
});
</script>

<style scoped>
.channels-container {
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.robot-option, .template-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.form-tip {
  display: flex;
  align-items: center;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  margin-right: 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
