<script setup>
import { Chart, registerables } from 'chart.js'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import http, { errorMessage } from '../api/http'
import { formatDate } from '../utils/format'

Chart.register(...registerables)

// RF08: grafico de evolucao da carga maxima por exercicio
const props = defineProps({
  studentId: { type: Number, default: null },
})

const exercises = ref([])
const exerciseId = ref(null)
const points = ref([])
const error = ref('')
const canvas = ref(null)
let chart = null

function params(extra = {}) {
  return props.studentId ? { student_id: props.studentId, ...extra } : extra
}

onMounted(async () => {
  try {
    const { data } = await http.get('/sessions/progress/exercises', { params: params() })
    exercises.value = data.exercises
    if (exercises.value.length) exerciseId.value = exercises.value[0].id
  } catch (e) {
    error.value = errorMessage(e)
  }
})

watch(exerciseId, async (id) => {
  if (!id) return
  try {
    const { data } = await http.get('/sessions/progress', { params: params({ exercise_id: id }) })
    points.value = data.points
    await nextTick()
    draw()
  } catch (e) {
    error.value = errorMessage(e)
  }
})

function draw() {
  if (chart) chart.destroy()
  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: points.value.map((p) => formatDate(p.performed_at)),
      datasets: [
        {
          label: 'Carga máxima (kg)',
          data: points.value.map((p) => p.max_load_kg),
          borderColor: '#1f6feb',
          backgroundColor: '#1f6feb',
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: false, title: { display: true, text: 'kg' } } },
    },
  })
}

onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-else-if="!exercises.length" class="muted">
    Registre alguns treinos para ver a evolução das cargas.
  </p>

  <template v-else>
    <label>
      Exercício
      <div class="select is-fullwidth">
        <select v-model="exerciseId">
          <option v-for="exercise in exercises" :key="exercise.id" :value="exercise.id">
            {{ exercise.name }}
          </option>
        </select>
      </div>
    </label>
    <div class="box">
      <canvas ref="canvas"></canvas>
    </div>
  </template>
</template>
