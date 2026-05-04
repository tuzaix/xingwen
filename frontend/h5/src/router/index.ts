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

// 全局前置守卫：保持卡密参数持续传递
router.beforeEach((to, from, next) => {
  const cardCode = to.query.card_code || from.query.card_code
  
  if (cardCode && !to.query.card_code) {
    // 如果上一个页面有卡密，但目标页面没有，则自动补充
    next({
      ...to,
      query: {
        ...to.query,
        card_code: cardCode
      }
    })
  } else {
    next()
  }
})

export default router
