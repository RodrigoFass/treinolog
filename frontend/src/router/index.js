import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/inicio' },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  {
    path: '/cadastro',
    component: () => import('../views/RegisterView.vue'),
    meta: { public: true },
  },
  { path: '/inicio', component: () => import('../views/HomeView.vue') },

  // Aluno
  {
    path: '/sessoes/:id',
    component: () => import('../views/SessionView.vue'),
  },
  { path: '/historico', component: () => import('../views/HistoryView.vue') },
  { path: '/evolucao', component: () => import('../views/ProgressView.vue') },

  // Personal
  {
    path: '/exercicios',
    component: () => import('../views/ExercisesView.vue'),
    meta: { role: 'personal' },
  },
  {
    path: '/alunos/:id',
    component: () => import('../views/StudentView.vue'),
    meta: { role: 'personal' },
  },
  {
    path: '/fichas/nova',
    component: () => import('../views/WorkoutEditorView.vue'),
    meta: { role: 'personal' },
  },
  {
    path: '/fichas/:id',
    component: () => import('../views/WorkoutEditorView.vue'),
    meta: { role: 'personal' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLogged) {
    return '/login'
  }
  if (to.meta.public && auth.isLogged) {
    return '/inicio'
  }
  if (to.meta.role && auth.user?.role !== to.meta.role) {
    return '/inicio'
  }
})

export default router
