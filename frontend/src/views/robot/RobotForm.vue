<template>
  <div class="robot-form-container">
    <el-card class="robot-card">
      <template #header>
        <div class="card-header">
          <h3>{{ isEdit ? '编辑机器人' : '创建机器人' }}</h3>
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
            <el-form-item label="机器人名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入机器人名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="机器人类型" prop="robot_type">
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
        
        <el-form-item label="Webhook地址" prop="webhook_url">
          <el-input v-model="form.webhook_url" placeholder="请输入Webhook地址">
            <template #append>
              <el-tooltip content="填写对应机器人平台提供的Webhook URL">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入机器人描述"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建机器人' }}</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="form.robot_type" class="help-section">
        <h4>{{ RobotTypeNames[form.robot_type] }}机器人配置说明</h4>
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
          <p>详细说明请参考：<a href="https://developer.work.weixin.qq.com/document/path/91770" target="_blank">企业微信机器人官方文档</a></p>
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
          <p>详细说明请参考：<a href="https://www.feishu.cn/hc/zh-CN/articles/360024984973" target="_blank">飞书机器人官方文档</a></p>
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
          <p>详细说明请参考：<a href="https://open.dingtalk.com/document/robots/custom-robot-access" target="_blank">钉钉机器人官方文档</a></p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useRobotStore } from '../../stores/robot';
import { RobotType, RobotTypeNames, Robot } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { QuestionFilled } from '@element-plus/icons-vue';

// 路由相关
const route = useRoute();
const router = useRouter();
const id = computed(() => route.params.id ? Number(route.params.id) : null);
const isEdit = computed(() => !!id.value);

// 机器人仓库
const robotStore = useRobotStore();
const loading = computed(() => robotStore.loading);

// 表单引用
const formRef = ref<FormInstance>();

// 表单数据
const form = reactive({
  name: '',
  webhook_url: '',
  description: '',
  robot_type: '' as RobotType
});

// URL验证函数
const validateUrl = (rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入Webhook地址'));
    return;
  }
  
  try {
    new URL(value);
    callback();
  } catch (error) {
    callback(new Error('请输入有效的URL地址'));
  }
};

// 表单验证规则
const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入机器人名称', trigger: 'blur' }],
  robot_type: [{ required: true, message: '请选择机器人类型', trigger: 'change' }],
  webhook_url: [
    { required: true, message: '请输入Webhook地址', trigger: 'blur' },
    { validator: validateUrl, trigger: 'blur' }
  ]
});

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value && id.value) {
          // 更新机器人
          const result = await robotStore.updateRobot(id.value, form);
          if (result) {
            ElMessage.success('更新机器人成功');
            router.push('/robots');
          }
        } else {
          // 创建机器人
          const result = await robotStore.createRobot(form);
          if (result) {
            ElMessage.success('创建机器人成功');
            router.push('/robots');
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
      router.push('/robots');
    })
    .catch(() => {
      // 继续编辑
    });
};

// 加载机器人数据（编辑模式）
const loadRobotData = async () => {
  if (isEdit.value && id.value) {
    try {
      const robot = await robotStore.fetchRobotById(id.value);
      if (robot) {
        form.name = robot.name;
        form.webhook_url = robot.webhook_url;
        form.description = robot.description || '';
        form.robot_type = robot.robot_type;
      } else {
        ElMessage.error('未找到机器人数据');
        router.push('/robots');
      }
    } catch (error) {
      ElMessage.error('加载机器人数据失败');
      router.push('/robots');
    }
  }
};

// 组件挂载时初始化
onMounted(() => {
  loadRobotData();
});
</script>

<style scoped>
.robot-form-container {
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

.help-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f7f9fc;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.help-section h4 {
  margin-top: 0;
  color: #409EFF;
}

.help-content {
  font-size: 14px;
  line-height: 1.6;
}

.help-content p {
  margin-bottom: 10px;
}

.help-content a {
  color: #409EFF;
  text-decoration: none;
}

.help-content a:hover {
  text-decoration: underline;
}
</style>