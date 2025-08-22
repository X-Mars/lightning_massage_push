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
      showInMenu: false,
    },
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
          showInMenu: true,
        },
      },
      {
        path: 'interface',
        name: 'Interface',
        redirect: '/interface/basic',
        meta: {
          title: '消息接口',
          icon: 'Connection',
          showInMenu: true,
        },
        children: [
          {
            path: 'basic',
            name: 'BasicApiList',
            component: () => import('../views/message/BasicApiList.vue'),
            meta: {
              title: '基本消息接口',
              icon: 'ChatDotRound',
              showInMenu: true,
              parent: 'Interface',
            },
          },
          {
            path: 'distribution',
            name: 'DistributionApiList',
            component: () => import('../views/message/DistributionApiList.vue'),
            meta: {
              title: '高级分发接口',
              icon: 'Operation',
              showInMenu: true,
              parent: 'Interface',
            },
          },
        ],
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('../views/template/TemplateList.vue'),
        meta: {
          title: '消息模板',
          icon: 'Document',
          showInMenu: true,
        },
      },
      {
        path: 'robots',
        name: 'Robots',
        component: () => import('../views/robot/RobotList.vue'),
        meta: {
          title: '机器人配置',
          icon: 'SetUp',
          showInMenu: true,
        },
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('../views/message/MessageList.vue'),
        meta: {
          title: '消息日志',
          icon: 'ChatDotRound',
          showInMenu: true,
        },
      },
      {
        path: 'push',
        name: 'Push',
        component: () => import('../views/message/PushForm.vue'),
        meta: {
          title: '发送消息',
          icon: 'Promotion',
          showInMenu: true,
        },
      },
      {
        path: 'prometheus',
        name: 'Prometheus',
        redirect: '/prometheus/alerts',
        meta: {
          title: 'Prometheus',
          icon: 'Monitor',
          showInMenu: true,
        },
        children: [
          {
            path: 'alerts',
            name: 'PrometheusAlerts',
            component: () => import('../views/prometheus/AlertList.vue'),
            meta: {
              title: '告警记录',
              icon: 'Warning',
              showInMenu: true,
              parent: 'Prometheus',
            },
          },
          {
            path: 'namespaces',
            name: 'PrometheusNamespaces',
            component: () => import('../views/prometheus/NamespaceList.vue'),
            meta: {
              title: '命名空间',
              icon: 'FolderOpened',
              showInMenu: true,
              parent: 'Prometheus',
            },
          },
        ],
      },
      {
        path: 'distribution',
        name: 'Distribution',
        redirect: '/distribution/rules',
        meta: {
          title: '高级分发',
          icon: 'Operation',
          showInMenu: true,
        },
        children: [
          {
            path: 'rules',
            name: 'DistributionRules',
            component: () => import('../views/distribution/RulesList.vue'),
            meta: {
              title: '分发规则',
              icon: 'EditPen',
              showInMenu: true,
              parent: 'Distribution',
            },
          },
          {
            path: 'channels',
            name: 'DistributionChannels',
            component: () => import('../views/distribution/ChannelList.vue'),
            meta: {
              title: '分发通道',
              icon: 'Connection',
              showInMenu: true,
              parent: 'Distribution',
            },
          },
          {
            path: 'mapping',
            name: 'DistributionMapping',
            component: () => import('../views/distribution/MappingConfig.vue'),
            meta: {
              title: '分发绑定',
              icon: 'Setting',
              showInMenu: true,
              parent: 'Distribution',
            },
          },
        ],
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
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
