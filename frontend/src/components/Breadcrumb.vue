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
import { useRoute, useRouter } from 'vue-router';
import type { RouteRecordNormalized } from 'vue-router';

interface BreadcrumbItem {
  path: string;
  title: string;
}

const route = useRoute();
const router = useRouter();

// 根据当前路由动态生成面包屑
const breadcrumbs = computed<BreadcrumbItem[]>(() => {
  const matchedRoutes = route.matched;
  const breadcrumbItems: BreadcrumbItem[] = [];
  
  // 遍历匹配的路由，构建面包屑路径
  matchedRoutes.forEach((matchedRoute: RouteRecordNormalized, index: number) => {
    // 跳过根路由和没有title的路由
    const isRootLayout = matchedRoute.path === '/' && matchedRoute.children?.length;
    const hasTitle = matchedRoute.meta?.title;
    
    if (!isRootLayout && hasTitle) {
      // 构建当前层级的完整路径
      const fullPath = buildFullPath(matchedRoutes, index);
      
      breadcrumbItems.push({
        path: fullPath,
        title: matchedRoute.meta.title as string
      });
    }
  });
  
  return breadcrumbItems;
});

// 构建完整路径
const buildFullPath = (routes: RouteRecordNormalized[], upToIndex: number): string => {
  let path = '';
  
  for (let i = 0; i <= upToIndex; i++) {
    const routeRecord = routes[i];
    
    // 跳过根路由
    if (routeRecord.path === '/') {
      continue;
    }
    
    // 处理相对路径和绝对路径
    if (routeRecord.path.startsWith('/')) {
      path = routeRecord.path;
    } else {
      path = path.endsWith('/') ? path + routeRecord.path : path + '/' + routeRecord.path;
    }
  }
  
  return path || '/';
};
</script>

<style scoped>
.breadcrumb-container {
  display: flex;
  align-items: center;
  height: 100%;
  width: 100%;
}
</style>