<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { formatDateTime } from '../utils/format'

// RF06: registro de carga e repeticoes de cada serie
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const session = ref(null)
const workout = ref(null)
const inputs = ref({})
const error = ref('')

const editable = computed(() => auth.isAluno && session.value?.student_id === auth.user.id)

function key(itemId, setNumber) {
  return `${itemId}-${setNumber}`
}

onMounted(async () => {
  try {
    const { data } = await http.get(`/sessions/${route.params.id}`)
    session.value = data
    workout.value = (await http.get(`/workouts/${data.workout_id}`)).data

    // Preenche cada serie com o que ja foi registrado ou com a prescricao
    for (const item of workout.value.exercises) {
      for (let n = 1; n <= item.sets; n++) {
        const logged = data.sets.find((s) => s.workout_exercise_id === item.id && s.set_number === n)
        inputs.value[key(item.id, n)] = {
          load_kg: logged ? logged.load_kg : (item.suggested_load_kg ?? ''),
          reps_done: logged ? logged.reps_done : parseInt(item.reps, 10) || '',
          saved: Boolean(logged),
          saving: false,
        }
      }
    }
  } catch (e) {
    error.value = errorMessage(e)
  }
})

async function saveSet(item, setNumber) {
  const entry = inputs.value[key(item.id, setNumber)]
  error.value = ''
  entry.saving = true
  try {
    await http.put(`/sessions/${session.value.id}/sets`, {
      workout_exercise_id: item.id,
      set_number: setNumber,
      reps_done: Number(entry.reps_done),
      load_kg: Number(entry.load_kg || 0),
    })
    entry.saved = true
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    entry.saving = false
  }
}

async function discard() {
  if (!confirm('Excluir este treino e todas as séries registradas?')) return
  await http.delete(`/sessions/${session.value.id}`)
  router.push('/inicio')
}
</script>

<template>
  <p v-if="error" class="error">{{ error }}</p>

  <template v-if="session && workout">
    <h1>{{ workout.name }}</h1>
    <p class="muted">{{ formatDateTime(session.performed_at) }}</p>

    <div v-for="item in workout.exercises" :key="item.id" class="card">
      <strong>{{ item.exercise_name }}</strong>
      <p class="muted" style="margin: 4px 0 10px">
        Prescrito: {{ item.sets }}x{{ item.reps }}
        <span v-if="item.suggested_load_kg"> · {{ item.suggested_load_kg }} kg</span>
        <span v-if="item.rest_seconds"> · descanso {{ item.rest_seconds }}s</span>
      </p>

      <div class="set-row muted" style="margin-bottom: 4px">
        <span>Série</span><span>Carga (kg)</span><span>Reps</span><span></span>
      </div>
      <div
        v-for="n in item.sets"
        :key="n"
        class="set-row"
        :class="{ saved: inputs[key(item.id, n)]?.saved }"
      >
        <span>{{ n }}ª</span>
        <input
          v-model="inputs[key(item.id, n)].load_kg"
          type="number"
          inputmode="decimal"
          min="0"
          step="0.5"
          :disabled="!editable"
        />
        <input
          v-model="inputs[key(item.id, n)].reps_done"
          type="number"
          inputmode="numeric"
          min="0"
          :disabled="!editable"
        />
        <button
          v-if="editable"
          :disabled="inputs[key(item.id, n)].saving"
          @click="saveSet(item, n)"
        >
          {{ inputs[key(item.id, n)].saved ? '✓' : 'OK' }}
        </button>
      </div>
    </div>

    <div v-if="editable" class="row">
      <button class="danger" @click="discard">Excluir treino</button>
      <button @click="router.push('/historico')">Concluir</button>
    </div>
  </template>
</template>
