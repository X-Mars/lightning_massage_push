<template>
  <div class="login-container">
    <div class="login-panel">
      <!-- 左侧面板 -->
      <div class="login-left-panel">
        <div class="brand-container">
          <div class="brand-title">闪电🌩推送</div>
          <div class="brand-slogan">简洁、高效、迅速</div>
        </div>
      </div>
      
      <!-- 右侧面板 -->
      <div class="login-right-panel">
        <!-- <div class="login-mascot">
          <img src="../assets/eagle.svg" alt="老鹰" class="mascot-image"/>
        </div> -->
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="loginRules" 
          class="login-form"
        >
          <img src="../assets/eagle.svg" alt="老鹰" class="mascot-image"/>
          
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              class="custom-input"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
              class="custom-input"
              show-password
            />
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" underline="never" class="forget-link" @click="handleForgetPassword">忘记密码?</el-link>
          </div>
          
          <el-button 
            type="primary" 
            class="login-button" 
            :loading="loading" 
            @click="handleLogin"
          >登 录</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const rememberMe = ref(false);

// 登录表单
const loginFormRef = ref<FormInstance>();
const loginForm = reactive({
  username: '',
  password: ''
});

// 表单验证规则
const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
});

// 页面加载时检查存储的用户名
const loadSavedUsername = () => {
  const savedUsername = localStorage.getItem('rememberedUsername');
  if (savedUsername) {
    loginForm.username = savedUsername;
    rememberMe.value = true;
  }
};

// 在组件挂载时加载用户名
loadSavedUsername();

// 忘记密码处理
const handleForgetPassword = () => {
  ElMessageBox.alert(
    '请联系系统管理员重置密码',
    '忘记密码',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  );
};

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const success = await authStore.login(loginForm.username, loginForm.password);
        if (success) {
          // 如果选择了"记住我"，保存用户名
          if (rememberMe.value) {
            localStorage.setItem('rememberedUsername', loginForm.username);
          } else {
            localStorage.removeItem('rememberedUsername');
          }
          
          ElMessage.success('登录成功');
          router.push('/');
        } else {
          ElMessage.error('用户名或密码错误');
        }
      } catch (error) {
        ElMessage.error('登录失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f2f5;
}

.login-panel {
  width: 900px;
  height: 500px;
  display: flex;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.login-left-panel {
  width: 40%;
  background-color: #409eff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  background-image: linear-gradient(145deg, #4481eb 0%, #04befe 100%);
}

.brand-container {
  text-align: center;
  padding: 0 20px;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  position: relative;
}

.brand-icon {
  font-size: 60px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.emoji-icon {
  font-size: 36px;
  position: absolute;
  top: -10px;
  right: -5px;
}

.brand-title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.brand-slogan {
  font-size: 16px;
  opacity: 0.8;
  line-height: 1.6;
}

.login-right-panel {
  width: 60%;
  background-color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* justify-content: center; */
  position: relative;
  padding: 40px;
}

.login-mascot {
  position: absolute;
  top: 40px;
  right: 40px;
  width: 120px;
  height: 120px;
}

.mascot-image {
  width: 40%;
  height: 40%;
  object-fit: contain;
}

.login-form {
  width: 320px;
}

.form-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}

.custom-input {
  height: 45px;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1) inset;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0 25px;
}

.forget-link {
  font-size: 14px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 8px;
  margin-top: 10px;
  background-image: linear-gradient(to right, #3d8eff, #42a5fe);
  border: none;
  transition: transform 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(66, 133, 244, 0.3);
}
</style>