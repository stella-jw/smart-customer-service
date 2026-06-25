import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { auth } from '@/api'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/user/chat'
  },
  {
    path: '/user',
    children: [
      {
        path: 'chat',
        name: 'UserChat',
        component: () => import('@/pages/user/ChatPage.vue')
      },
      {
        path: 'history',
        name: 'UserHistory',
        component: () => import('@/pages/user/HistoryPage.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/pages/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/bots'
      },
      {
        path: 'bots',
        name: 'Bots',
        component: () => import('@/pages/admin/BotsPage.vue')
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('@/pages/admin/KnowledgeBasePage.vue')
      },
      {
        path: 'qa',
        name: 'QAManagement',
        component: () => import('@/pages/admin/QAManagementPage.vue')
      },
      {
        path: 'config',
        name: 'BotConfig',
        component: () => import('@/pages/admin/BotConfigPage.vue')
      },
      {
        path: 'teams',
        name: 'Teams',
        component: () => import('@/pages/admin/TeamsPage.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'bot-access',
        name: 'BotAccess',
        component: () => import('@/pages/admin/BotAccessPage.vue'),
        meta: { requiresAdmin: true }
      }
    ]
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/pages/admin/LoginPage.vue')
  },
  {
    path: '/admin/register',
    name: 'AdminRegister',
    component: () => import('@/pages/admin/RegisterPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, _from, next) => {
  const isLoggedIn = auth.isLoggedIn()
  const isAdmin = auth.isAdmin()
  const requiresAuth = to.matched.some(record => record.meta?.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta?.requiresAdmin)

  if (requiresAuth && !isLoggedIn) {
    next('/admin/login')
  } else if (requiresAdmin && isLoggedIn && !isAdmin) {
    // Logged in but not admin, redirect to basic admin page
    next('/admin/bots')
  } else if ((to.path === '/admin/login' || to.path === '/admin/register') && isLoggedIn) {
    next('/admin/bots')
  } else {
    next()
  }
})

export default router
