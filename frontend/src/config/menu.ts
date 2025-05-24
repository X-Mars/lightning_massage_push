import router from '../router';
import type { RouteRecordRaw } from 'vue-router';

// 菜单项接口
export interface MenuItem {
  path: string;
  title: string;
  icon: string;
  children?: MenuItem[];
}

// 从路由配置中获取菜单项
function getMenuItemsFromRoutes(): MenuItem[] {
  const mainRoute = router.options.routes.find((route) => route.path === '/') as RouteRecordRaw;
  if (!mainRoute || !mainRoute.children) return [];

  return mainRoute.children
    .filter((route) => route.meta?.showInMenu)
    .map((route) => ({
      path: `/${route.path}`,
      title: route.meta?.title || route.name?.toString() || '',
      icon: route.meta?.icon || 'Menu',
      children: []
    }));
}

// 导出菜单项
export const menuItems = getMenuItemsFromRoutes();
