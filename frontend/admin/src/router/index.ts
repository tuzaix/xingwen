import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import CardList from '../views/CardList.vue'
import ReportList from '../views/ReportList.vue'
import Stats from '../views/Stats.vue'
import SystemConfig from '../views/SystemConfig.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      component: AdminLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: Dashboard
        },
        {
          path: 'cards',
          name: 'cards',
          component: CardList
        },
        {
          path: 'reports',
          name: 'reports',
          component: ReportList
        },
        {
          path: 'stats',
          name: 'stats',
          component: Stats
        },
        {
          path: 'config',
          name: 'config',
          component: SystemConfig
        }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.name !== 'login' && !authStore.token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
