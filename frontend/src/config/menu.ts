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
  const mainRoute = router.options.routes.find(route => route.path === '/') as RouteRecordRaw;
  if (!mainRoute || !mainRoute.children) return [];

  return mainRoute.children
    .filter(route => route.meta?.showInMenu)
    .map(route => {
      const menuItem: MenuItem = {
        path: `/${route.path}`,
        title: route.meta?.title || route.name?.toString() || '',
        icon: route.meta?.icon || 'Menu',
      };

      // 处理子路由
      if (route.children && route.children.length > 0) {
        menuItem.children = route.children
          .filter(child => child.meta?.showInMenu)
          .map(child => ({
            path: `/${route.path}/${child.path}`,
            title: child.meta?.title || child.name?.toString() || '',
            icon: child.meta?.icon || 'Menu',
          }));
      }

      return menuItem;
    });
}

// 导出菜单项
export const menuItems = getMenuItemsFromRoutes();
