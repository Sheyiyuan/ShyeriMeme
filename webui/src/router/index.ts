import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AdminPage from '../pages/AdminPage.vue'
import WebUIPage from '../pages/WebUIPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/webui'
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage
  },
  {
    path: '/webui',
    name: 'WebUI',
    component: WebUIPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router