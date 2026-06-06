import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'programs',
        name: 'ProgramList',
        component: () => import('@/views/ProgramList.vue')
      },
      {
        path: 'props',
        name: 'PropList',
        component: () => import('@/views/PropList.vue')
      },
      {
        path: 'vehicles',
        name: 'VehicleList',
        component: () => import('@/views/VehicleList.vue')
      },
      {
        path: 'loading',
        name: 'LoadingList',
        component: () => import('@/views/LoadingList.vue')
      },
      {
        path: 'unloading',
        name: 'UnloadingList',
        component: () => import('@/views/UnloadingList.vue')
      },
      {
        path: 'damage',
        name: 'DamageList',
        component: () => import('@/views/DamageList.vue')
      },
      {
        path: 'maintenance',
        name: 'MaintenanceList',
        component: () => import('@/views/MaintenanceList.vue')
      },
      {
        path: 'scrap',
        name: 'ScrapList',
        component: () => import('@/views/ScrapList.vue')
      },
      {
        path: 'tours',
        name: 'TourList',
        component: () => import('@/views/TourList.vue')
      },
      {
        path: 'tour-settlements',
        name: 'TourSettlementList',
        component: () => import('@/views/TourSettlementList.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
