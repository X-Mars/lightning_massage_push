<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="floating-circle circle-1"></div>
      <div class="floating-circle circle-2"></div>
      <div class="floating-circle circle-3"></div>
      <div class="floating-circle circle-4"></div>
    </div>

    <div class="login-panel" :class="{ 'panel-shake': loginError }">
      <!-- 左侧面板 -->
      <div class="login-left-panel">
        <div class="brand-container">
          <div class="brand-logo">
            <img src="../assets/lightning.svg" alt="闪电" class="brand-icon pulse-animation" />
            <span class="emoji-sparkle">✨</span>
          </div>
          <div class="brand-title fade-in-up">闪电推送</div>
          <div class="brand-slogan fade-in-up-delay">简洁 · 高效 · 迅速</div>
          <div class="feature-list fade-in-up-delay-2">
            <div class="feature-item">
              <el-icon><MessageBox /></el-icon>
              <span>多平台消息推送</span>
            </div>
            <div class="feature-item">
              <el-icon><Timer /></el-icon>
              <span>实时状态监控</span>
            </div>
            <div class="feature-item">
              <el-icon><Setting /></el-icon>
              <span>灵活配置管理</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="login-right-panel">
        <div class="form-header">
          <div class="welcome-back">
            <el-icon class="welcome-icon"><User /></el-icon>
            <h2>欢迎回来</h2>
          </div>
        </div>

        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="loginRules" 
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username" class="form-item-animated">
            <div class="input-wrapper">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                class="custom-input"
                clearable
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password" class="form-item-animated">
            <div class="input-wrapper">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                class="custom-input"
                show-password
                clearable
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
            </div>
          </el-form-item>

          <el-form-item prop="captcha" class="form-item-animated">
            <div class="captcha-wrapper">
              <div class="input-wrapper captcha-input">
                <el-input
                  v-model="loginForm.captcha"
                  placeholder="请输入验证码"
                  :prefix-icon="Lock"
                  @keyup.enter="handleLogin"
                  class="custom-input"
                  clearable
                  maxlength="4"
                  @focus="handleInputFocus"
                  @blur="handleInputBlur"
                />
              </div>
              <div class="captcha-image-wrapper" @click="refreshCaptcha">
                <img 
                  v-if="captchaImage" 
                  :src="captchaImage" 
                  alt="验证码" 
                  class="captcha-image"
                />
              </div>
            </div>
          </el-form-item>

          <el-button 
            type="primary" 
            class="login-button" 
            :loading="loading" 
            @click="handleLogin"
            size="large"
          >
            <template v-if="!loading">
              <el-icon class="login-icon"><Right /></el-icon>
              登 录
            </template>
            <template v-else>
              <span>登录中...</span>
            </template>
          </el-button>

          <!-- 快速登录提示 -->
          <div class="quick-tip" v-if="!loading">
            <el-icon><InfoFilled /></el-icon>
            <span>按 Enter 键快速登录</span>
          </div>
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
import { ElMessage } from 'element-plus';
import { 
  User, 
  Lock, 
  MessageBox,
  Timer,
  Setting,
  Right,
  InfoFilled
} from '@element-plus/icons-vue';
import { formatToLocalTime } from '../utils/timeFormatter';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const loginError = ref(false);

// 登录表单
const loginFormRef = ref<FormInstance>();
const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
});

// 验证码相关
const captchaImage = ref('');
const captchaKey = ref('');

// 表单验证规则
const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
});

// 获取验证码
const getCaptcha = async () => {
  try {
    const response = await fetch('/api/captcha/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      const result = await response.json();
      if (result.success && result.data) {
        captchaImage.value = result.data.captcha_image;
        captchaKey.value = result.data.captcha_key;
      } else {
        ElMessage.error('获取验证码失败');
      }
    } else {
      ElMessage.error('获取验证码失败');
    }
  } catch (error) {
    console.error('获取验证码错误:', error);
    ElMessage.error('获取验证码失败');
  }
};

// 刷新验证码
const refreshCaptcha = () => {
  captchaImage.value = '';
  loginForm.captcha = '';
  getCaptcha();
};

// 在组件挂载时获取验证码
getCaptcha();

// 输入框焦点事件
const handleInputFocus = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const wrapper = target.closest('.input-wrapper');
  if (wrapper) {
    wrapper.classList.add('focused');
  }
};

const handleInputBlur = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const wrapper = target.closest('.input-wrapper');
  if (wrapper && !target.value) {
    wrapper.classList.remove('focused');
  }
};

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return;

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      loginError.value = false;
      
      try {
        // 直接调用登录接口，包含验证码验证
        const result = await authStore.login(
          loginForm.username, 
          loginForm.password,
          captchaKey.value,
          loginForm.captcha
        );
        
        if (result.success) {
          // 构建登录成功消息
          let successMessage = `
            <div style="text-align: center;">
              <div style="font-size: 16px; font-weight: 500; margin-bottom: 8px;">
                🎉 登录成功！欢迎回来
              </div>
              ${result.lastLogin ? `
                <div style="font-size: 13px; color: #909399; opacity: 0.8;">
                  <i style="margin-right: 4px;">🕒</i>上次登录：${formatToLocalTime(result.lastLogin)}
                </div>
              ` : ''}
            </div>
          `;

          ElMessage.success({
            message: successMessage,
            type: 'success',
            duration: 4500,
            dangerouslyUseHTMLString: true,
          });
          
          // 添加一个小延迟让用户看到成功消息
          setTimeout(() => {
            router.push('/');
          }, 1000);
        } else {
          loginError.value = true;
          ElMessage.error({
            message: '用户名或密码错误 😞',
            type: 'error',
            duration: 3000,
          });
          
          // 登录失败后刷新验证码
          refreshCaptcha();
          
          // 清除错误状态
          setTimeout(() => {
            loginError.value = false;
          }, 500);
        }
      } catch (error: unknown) {
        loginError.value = true;
        
        // 检查是否是验证码错误
        const errorResponse = error as { response?: { data?: { detail?: string } }; message?: string };
        const errorMessage = errorResponse?.response?.data?.detail || errorResponse?.message || '';
        if (errorMessage.includes('验证码')) {
          ElMessage.error({
            message: `${errorMessage} 🔄`,
            type: 'error',
            duration: 3000,
          });
        } else {
          ElMessage.error({
            message: '登录失败，请稍后重试 🔄',
            type: 'error',
            duration: 3000,
          });
        }
        
        // 登录失败后刷新验证码
        refreshCaptcha();
        
        setTimeout(() => {
          loginError.value = false;
        }, 500);
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
/* 基础容器和背景 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰动画 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 15s infinite ease-in-out;
}

.circle-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 15%;
  animation-delay: 4s;
}

.circle-4 {
  width: 60px;
  height: 60px;
  bottom: 10%;
  right: 20%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.5;
  }
  33% {
    transform: translateY(-30px) rotate(120deg);
    opacity: 0.8;
  }
  66% {
    transform: translateY(-60px) rotate(240deg);
    opacity: 0.3;
  }
}

/* 主面板 */
.login-panel {
  width: 950px;
  height: 600px;
  display: flex;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  animation: slideInUp 0.5s ease-out;
}

.panel-shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(60px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* 左侧品牌面板 */
.login-left-panel {
  width: 45%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  padding: 40px;
}

.brand-container {
  text-align: center;
  width: 100%;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  position: relative;
}

.brand-icon {
  width: 96px;
  height: 96px;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.emoji-sparkle {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 24px;
  animation: sparkle 1.5s infinite;
}

@keyframes sparkle {
  0%, 100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2) rotate(180deg);
  }
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.brand-slogan {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 40px;
  letter-spacing: 1px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  opacity: 0.8;
  transition: all 0.3s ease;
}

.feature-item:hover {
  opacity: 1;
  transform: translateY(-8px);
}

.feature-item .el-icon {
  font-size: 20px;
}

/* 动画类 */
.fade-in-up {
  animation: fadeInUp 0.5s ease-out 0.1s both;
}

.fade-in-up-delay {
  animation: fadeInUp 0.5s ease-out 0.2s both;
}

.fade-in-up-delay-2 {
  animation: fadeInUp 0.5s ease-out 0.3s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 右侧登录面板 */
.login-right-panel {
  width: 55%;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 50px;
  position: relative;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-back {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.welcome-back h2 {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.welcome-icon {
  font-size: 32px;
  color: #667eea;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* 表单样式 */
.login-form {
  width: 100%;
  max-width: 400px;
}

.login-form :deep(.el-form-item) {
  width: 100%;
  margin-bottom: 25px;
}

.login-form :deep(.el-form-item__content) {
  width: 100%;
}

.form-item-animated {
  margin-bottom: 25px;
  animation: slideInLeft 0.2s ease-out;
  width: 100%;
}

.form-item-animated :deep(.el-form-item__content) {
  width: 100%;
}

.form-item-animated:nth-child(1) {
  animation-delay: 0.15s;
  animation-fill-mode: both;
}

.form-item-animated:nth-child(2) {
  animation-delay: 0.2s;
  animation-fill-mode: both;
}

.form-item-animated:nth-child(3) {
  animation-delay: 0.25s;
  animation-fill-mode: both;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.custom-input {
  height: 50px;
  transition: all 0.3s ease;
  width: 100%;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 2px solid #e1e6ea;
  box-shadow: none;
  transition: all 0.3s ease;
  background: #f8f9fa;
  width: 100%;
}

.custom-input :deep(.el-input__inner) {
  width: 100%;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
}

.custom-input :deep(.el-input__inner) {
  font-size: 16px;
  color: #2c3e50;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: #bdc3c7;
}

.custom-input :deep(.el-input__prefix) {
  color: #667eea;
}

/* 验证码样式 */
.captcha-wrapper {
  display: flex;
  gap: 15px;
  align-items: center;
  width: 100%;
}

.captcha-input {
  flex: 1;
  min-width: 0; /* 防止flex子元素溢出 */
}

.captcha-image-wrapper {
  width: 120px;
  height: 50px;
  border-radius: 8px;
  border: 2px solid #e1e6ea;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; /* 防止被压缩 */
}

.captcha-image-wrapper:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.captcha-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  color: #667eea;
  font-size: 12px;
}

.loading-icon {
  font-size: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.captcha-refresh-tip {
  position: absolute;
  bottom: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #95a5a6;
  opacity: 0;
  transition: opacity 0.3s ease;
  white-space: nowrap;
}

.captcha-image-wrapper:hover .captcha-refresh-tip {
  opacity: 1;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: 55px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.2s ease-out 0.25s both;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(-1px);
}

.login-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 快速提示 */
.quick-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  color: #95a5a6;
  font-size: 14px;
  animation: fadeInUp 0.2s ease-out 0.25s both;
}

.quick-tip .el-icon {
  font-size: 16px;
  color: #3498db;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-panel {
    width: 90%;
    height: auto;
    flex-direction: column;
  }

  .login-left-panel,
  .login-right-panel {
    width: 100%;
  }

  .login-left-panel {
    min-height: 300px;
  }

  .brand-title {
    font-size: 36px;
  }

  .brand-icon {
    width: 80px;
    height: 80px;
  }
}

@media (max-width: 768px) {
  .login-panel {
    margin: 20px;
    border-radius: 16px;
  }

  .login-left-panel {
    padding: 30px;
  }

  .login-right-panel {
    padding: 40px 30px;
  }

  .feature-list {
    gap: 15px;
  }

  .feature-item {
    font-size: 14px;
  }

  .welcome-back h2 {
    font-size: 28px;
  }

  .login-form {
    max-width: 100%;
  }
}
</style>
