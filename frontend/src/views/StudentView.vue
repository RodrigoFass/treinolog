<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import http, { errorMessage } from '../api/http'
import LoadProgress from '../components/LoadProgress.vue'
import SessionHistory from '../components/SessionHistory.vue'
import StreakPanel from '../components/StreakPanel.vue'

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
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <template v-if="student">
    <h1 class="title is-4">{{ student.name }}</h1>

    <div class="tabs is-boxed">
      <ul>
        <li :class="{ 'is-active': tab === 'fichas' }"><a @click="tab = 'fichas'">Fichas</a></li>
        <li :class="{ 'is-active': tab === 'historico' }"><a @click="tab = 'historico'">Histórico</a></li>
        <li :class="{ 'is-active': tab === 'evolucao' }"><a @click="tab = 'evolucao'">Evolução</a></li>
        <li :class="{ 'is-active': tab === 'ofensiva' }"><a @click="tab = 'ofensiva'">Ofensiva</a></li>
      </ul>
    </div>

    <template v-if="tab === 'fichas'">
      <RouterLink :to="`/fichas/nova?aluno=${studentId}`">
        <button class="button is-primary is-fullwidth" style="margin-bottom: 12px">Nova ficha</button>
      </RouterLink>
      <p v-if="!workouts.length" class="muted">Nenhuma ficha montada para este aluno.</p>

      <div v-for="workout in workouts" :key="workout.id" class="box">
        <div class="row">
          <div>
            <strong>{{ workout.name }}</strong>
            <span class="tag is-info is-light" style="margin-left: 6px">
              {{ workout.is_active ? 'Ativa' : 'Inativa' }}
            </span>
          </div>
          <div class="row">
            <RouterLink :to="`/fichas/${workout.id}`">
              <button class="button is-light">Editar</button>
            </RouterLink>
            <button class="button is-light" @click="toggleActive(workout)">
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
    <LoadProgress v-else-if="tab === 'evolucao'" :student-id="studentId" />
    <StreakPanel v-else :student-id="studentId" />
  </template>
</template>
