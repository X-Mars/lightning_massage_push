<template>
  <div class="common-layout">
    <el-container class="layout-container">
      <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
        <div class="logo-container">
          <h2 class="logo-text" v-show="!isCollapse">
            <img src="../assets/eagle.svg" alt="老鹰" class="mascot-image"/>
            <span class="logo-title">闪电推送</span>
          </h2>
          <h2 class="logo-icon" v-show="isCollapse">
            <img src="../assets/eagle.svg" alt="老鹰" class="mascot-image-2"/>
          </h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409eff"
          :collapse="isCollapse"
          router
        >
          <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <div class="collapse-btn" @click="toggleCollapse">
              <el-icon size="20">
                <component :is="isCollapse ? 'Expand' : 'Fold'" />
              </el-icon>
            </div>
            <Breadcrumb />
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                <span class="username">{{ username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { ArrowDown } from '@element-plus/icons-vue';
import { ElMessageBox } from 'element-plus';
import { menuItems } from '../config/menu';
import Breadcrumb from './BreadcrumbWrapper';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isCollapse = ref(false);
const activeMenu = computed(() => route.path);
const username = ref('管理员');

// 切换导航栏收起/展开
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      authStore.logout();
      router.push('/login');
    }).catch(() => {});
  }
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
  min-height: 100vh;
  width: 100%;
}

.common-layout {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  background-color: #001529;
  border-bottom: 1px solid #1a2d3d;
  overflow: hidden;
  transition: all 0.3s;
}

.logo-text {
  margin: 0;
  padding: 0;
  font-size: 18px;
  color: #fff;
  white-space: nowrap;
  display: flex;
  align-items: center;
}

.logo-title {
  display: inline-block;
  vertical-align: middle;
  margin-left: 8px;
  font-size: 30px;
}

.logo-icon {
  margin: 0;
  padding: 0;
  font-size: 40px;
  color: #fff;
}

.el-menu-vertical {
  border-right: none;
  transition: width 0.3s;
}

.aside {
  background-color: #001529;
  color: white;
  overflow-x: hidden;
  transition: width 0.3s;
}

.collapse-btn {
  cursor: pointer;
  font-size: 20px;
  color: #333;
  margin-right: 15px;
  display: flex;
  align-items: center;
}

.header {
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 64px;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin: 0 8px;
  font-size: 14px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 0;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.mascot-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
  vertical-align: middle;
}

.mascot-image-2 {
  width: 55px;
  height: 55px;
  object-fit: contain;
  vertical-align: middle;
}
</style>