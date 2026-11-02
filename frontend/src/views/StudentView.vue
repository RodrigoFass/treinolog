<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import http, { errorMessage } from '../api/http'
import LoadProgress from '../components/LoadProgress.vue'
import SessionHistory from '../components/SessionHistory.vue'

const route = useRoute()
const studentId = Number(route.params.id)

const student = ref(null)
const workouts = ref([])
const tab = ref('fichas')
const error = ref('')

async function loadWorkouts() {
  const { data } = await http.get('/workouts', { params: { student_id: studentId } })
  workouts.value = data.workouts
}

onMounted(async () => {
  try {
    const { data } = await http.get('/auth/students')
    student.value = data.students.find((s) => s.id === studentId)
    await loadWorkouts()
  } catch (e) {
    error.value = errorMessage(e)
  }
})

async function toggleActive(workout) {
  error.value = ''
  try {
    await http.put(`/workouts/${workout.id}`, { is_active: !workout.is_active })
    await loadWorkouts()
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <p v-if="error" class="error">{{ error }}</p>

  <template v-if="student">
    <h1>{{ student.name }}</h1>

    <div class="row" style="margin-bottom: 12px; justify-content: flex-start">
      <button :class="{ secondary: tab !== 'fichas' }" @click="tab = 'fichas'">Fichas</button>
      <button :class="{ secondary: tab !== 'historico' }" @click="tab = 'historico'">
        Histórico
      </button>
      <button :class="{ secondary: tab !== 'evolucao' }" @click="tab = 'evolucao'">
        Evolução
      </button>
    </div>

    <template v-if="tab === 'fichas'">
      <RouterLink :to="`/fichas/nova?aluno=${studentId}`">
        <button class="full" style="margin-bottom: 12px">Nova ficha</button>
      </RouterLink>
      <p v-if="!workouts.length" class="muted">Nenhuma ficha montada para este aluno.</p>

      <div v-for="workout in workouts" :key="workout.id" class="card">
        <div class="row">
          <div>
            <strong>{{ workout.name }}</strong>
            <span class="badge" style="margin-left: 6px">
              {{ workout.is_active ? 'Ativa' : 'Inativa' }}
            </span>
          </div>
          <div class="row">
            <RouterLink :to="`/fichas/${workout.id}`">
              <button class="secondary">Editar</button>
            </RouterLink>
            <button class="secondary" @click="toggleActive(workout)">
              {{ workout.is_active ? 'Desativar' : 'Reativar' }}
            </button>
          </div>
        </div>
        <ol style="padding-left: 20px; margin-bottom: 0">
          <li v-for="item in workout.exercises" :key="item.id">
            {{ item.exercise_name }} — {{ item.sets }}x{{ item.reps }}
          </li>
        </ol>
      </div>
    </template>

    <SessionHistory v-else-if="tab === 'historico'" :student-id="studentId" />
    <LoadProgress v-else :student-id="studentId" />
  </template>
</template>
