<template>
  <div class="breadcrumb-container">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

interface BreadcrumbItem {
  path: string;
  title: string;
}

const route = useRoute();

// 根据路由定义面包屑
const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const path = route.path;
  const result: BreadcrumbItem[] = [];
  
  if (path === '/') {
    return [];
  }
  
  if (path.startsWith('/templates')) {
    result.push({ path: '/templates', title: '消息模板' });
    
    if (path.includes('/create')) {
      result.push({ path: '', title: '创建模板' });
    } else if (path.match(/\/templates\/\d+/)) {
      result.push({ path: '', title: '编辑模板' });
    }
  }
  
  if (path.startsWith('/robots')) {
    result.push({ path: '/robots', title: '机器人列表' });
    
    if (path.includes('/create')) {
      result.push({ path: '', title: '创建机器人' });
    } else if (path.match(/\/robots\/\d+/)) {
      result.push({ path: '', title: '编辑机器人' });
    }
  }
  
  if (path === '/messages') {
    result.push({ path: '/messages', title: '消息日志' });
  }
  
  if (path === '/push') {
    result.push({ path: '/push', title: '发送消息' });
  }
  
  return result;
});
</script>

<style scoped>
.breadcrumb-container {
  display: flex;
  align-items: center;
  height: 100%;
  width: 100%;
}
</style>