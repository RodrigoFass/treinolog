<script setup>
import { onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import { formatDateTime } from '../utils/format'

// RF07: historico de sessoes por data (aluno ou personal consultando um aluno)
const props = defineProps({
  studentId: { type: Number, default: null },
})

const sessions = ref([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const params = props.studentId ? { student_id: props.studentId } : {}
    const { data } = await http.get('/sessions', { params })
    sessions.value = data.sessions
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <p v-if="loading" class="muted">Carregando...</p>
  <p v-else-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-else-if="!sessions.length" class="muted">Nenhum treino registrado ainda.</p>

  <RouterLink
    v-for="session in sessions"
    :key="session.id"
    :to="`/sessoes/${session.id}`"
    style="text-decoration: none; color: inherit"
  >
    <div class="box row">
      <strong>{{ session.workout_name }}</strong>
      <span class="muted">{{ formatDateTime(session.performed_at) }}</span>
    </div>
  </RouterLink>
</template>
