<script setup>
import { onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'
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

  <div class="box">
    <p class="muted">Código de convite para seus alunos</p>
    <p style="font-size: 1.6rem; font-weight: 700; letter-spacing: 3px; margin: 4px 0">
      {{ auth.user.invite_code }}
    </p>
  </div>

  <h2 class="title is-5">Seus alunos</h2>
  <p v-if="loading" class="muted">Carregando...</p>
  <p v-else-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-else-if="!students.length" class="muted">
    Nenhum aluno vinculado ainda. Envie o código de convite acima.
  </p>

  <RouterLink
    v-for="student in students"
    :key="student.id"
    :to="`/alunos/${student.id}`"
    style="text-decoration: none; color: inherit"
  >
    <div class="box">
      <strong>{{ student.name }}</strong>
      <p class="muted" style="margin: 4px 0 0">{{ lastWorkoutLabel(student.last_workout_at) }}</p>
    </div>
  </RouterLink>
</template>
