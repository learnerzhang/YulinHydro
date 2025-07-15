import { createRouter, createWebHistory } from 'vue-router'
import SearchPage from '../views/SearchPage.vue'
import DetailPage from '../views/DetailPage.vue'

const routes = [
  {
    path: '/',
    name: 'SearchPage',
    component: SearchPage
  },
  {
    path: '/detail/:id',  // 改为使用id作为参数
    name: 'DetailPage',
    component: DetailPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router