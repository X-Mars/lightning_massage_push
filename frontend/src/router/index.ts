import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// 扩展Vue Router的meta类型定义
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    title?: string;
    icon?: string;
    showInMenu?: boolean;
  }
}

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { 
      requiresAuth: false,
      title: '登录',
      showInMenu: false
    }
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          icon: 'DataLine',
          showInMenu: true
        }
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('../views/template/TemplateList.vue'),
        meta: {
          title: '消息模板',
          icon: 'Document',
          showInMenu: true
        }
      },
      {
        path: 'templates/create',
        name: 'CreateTemplate',
        component: () => import('../views/template/TemplateForm.vue'),
        meta: {
          title: '创建模板',
          showInMenu: false
        }
      },
      {
        path: 'templates/:id',
        name: 'EditTemplate',
        component: () => import('../views/template/TemplateForm.vue'),
        props: true,
        meta: {
          title: '编辑模板',
          showInMenu: false
        }
      },
      {
        path: 'robots',
        name: 'Robots',
        component: () => import('../views/robot/RobotList.vue'),
        meta: {
          title: '机器人配置',
          icon: 'SetUp',
          showInMenu: true
        }
      },
      {
        path: 'robots/create',
        name: 'CreateRobot',
        component: () => import('../views/robot/RobotForm.vue'),
        meta: {
          title: '创建机器人',
          showInMenu: false
        }
      },
      {
        path: 'robots/:id',
        name: 'EditRobot',
        component: () => import('../views/robot/RobotForm.vue'),
        props: true,
        meta: {
          title: '编辑机器人',
          showInMenu: false
        }
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('../views/message/MessageList.vue'),
        meta: {
          title: '消息日志',
          icon: 'ChatDotRound',
          showInMenu: true
        }
      },
      {
        path: 'api',
        name: 'ApiList',
        component: () => import('../views/message/ApiList.vue'),
        meta: {
          title: '消息接口',
          icon: 'Connection',
          showInMenu: true
        }
      },
      {
        path: 'push',
        name: 'Push',
        component: () => import('../views/message/PushForm.vue'),
        meta: {
          title: '发送消息',
          icon: 'Promotion',
          showInMenu: true
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  if (requiresAuth && !authStore.isLoggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router;