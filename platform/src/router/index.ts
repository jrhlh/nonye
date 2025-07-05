// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MainLayout from '../components/layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../pages/DashboardPage.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'monitoring',
          name: 'monitoring',
          component: () => import('../pages/MonitoringPage.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'personnel',
          name: 'personnel',
          component: () => import('../pages/PersonnelPage.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'devices',
          name: 'devices',
          component: () => import('../pages/DeviceManagementPage.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../pages/ReportsPage.vue'),
          meta: { requiresAuth: true }
        }
      ]
    }
  ]
})

// // 路由守卫
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = localStorage.getItem('user') !== null

//   if (to.meta.requiresAuth && !isAuthenticated) {
//     next('/login')
//   } else {
//     next()
//   }
// })

export default router