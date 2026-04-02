import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import QuotasView from '../views/QuotasView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/quotas', component: QuotasView },
  { path: '/history', component: HistoryView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
