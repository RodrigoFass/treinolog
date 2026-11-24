<script setup>
import { onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'
import AppIcon from './AppIcon.vue'
import { daysSince, formatDate } from '../utils/format'

// RF09: painel do personal com alunos e data do ultimo treino
const auth = useAuthStore()
const students = ref([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await http.get('/auth/students')
    students.value = data.students
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})

function lastWorkoutLabel(iso) {
  const days = daysSince(iso)
  if (days === null) return 'Nunca treinou'
  if (days === 0) return 'Treinou hoje'
  return `Último treino: ${formatDate(iso)} (há ${days} dia${days > 1 ? 's' : ''})`
}
</script>

<template>
  <h1 class="title is-4">Olá, {{ auth.user.name }}</h1>

  <div class="neon-card" style="--accent: var(--foco)">
    <p class="muted">Código de convite para seus alunos</p>
    <p class="code-box">{{ auth.user.invite_code }}</p>
  </div>

  <p class="section-title">Seus alunos</p>
  <p v-if="loading" class="muted">Carregando...</p>
  <p v-else-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-else-if="!students.length" class="muted">
    Nenhum aluno vinculado ainda. Envie o código de convite acima.
  </p>

  <RouterLink
    v-for="student in students"
    :key="student.id"
    :to="`/alunos/${student.id}`"
    class="list-card"
  >
    <span class="avatar" style="--accent: var(--treino)"><AppIcon name="dumbbell" /></span>
    <div>
      <strong>{{ student.name }}</strong>
      <p class="muted">{{ lastWorkoutLabel(student.last_workout_at) }}</p>
    </div>
  </RouterLink>
</template>
