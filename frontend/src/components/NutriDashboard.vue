<script setup>
import { onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'
import ProgressRing from './ProgressRing.vue'

// RF14: painel do nutricionista com os pacientes
const auth = useAuthStore()
const patients = ref([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await http.get('/nutrition/patients')
    patients.value = data.patients
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1 class="title is-4">Olá, {{ auth.user.name }}</h1>

  <div class="neon-card" style="--accent: var(--foco)">
    <p class="muted">Código de convite para seus pacientes</p>
    <p class="code-box">{{ auth.user.invite_code }}</p>
  </div>

  <p class="section-title">Seus pacientes</p>
  <p v-if="loading" class="muted">Carregando...</p>
  <p v-else-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-else-if="!patients.length" class="muted">
    Nenhum paciente vinculado ainda. Envie o código de convite acima.
  </p>

  <RouterLink
    v-for="patient in patients"
    :key="patient.id"
    :to="`/pacientes/${patient.id}`"
    class="list-card"
  >
    <ProgressRing
      :value="(patient.adherence_7d ?? 0) / 100"
      color="var(--dieta)"
      icon="utensils"
      :size="58"
    />
    <div style="flex: 1">
      <strong>{{ patient.name }}</strong>
      <p class="muted">{{ patient.plan_name || 'Sem plano alimentar' }}</p>
      <p class="muted">
        Adesão (7 dias): {{ patient.adherence_7d ?? '—' }}{{ patient.adherence_7d !== null ? '%' : '' }}
        · Peso: {{ patient.last_weight ? `${patient.last_weight.weight_kg} kg` : '—' }}
      </p>
    </div>
  </RouterLink>
</template>
