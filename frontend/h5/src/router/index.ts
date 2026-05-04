import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('../views/UploadHands.vue')
    },
    {
      path: '/info',
      name: 'info',
      component: () => import('../views/Info.vue')
    },
    {
      path: '/verify',
      name: 'verify',
      component: () => import('../views/Verify.vue')
    },
    {
      path: '/report/:id',
      name: 'report',
      component: () => import('../views/Report.vue')
    }
  ]
})

export default router
