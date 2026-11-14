<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const workouts = ref([])
const inviteCode = ref('')
const error = ref('')
const starting = ref(null)

async function loadWorkouts() {
  const { data } = await http.get('/workouts')
  workouts.value = data.workouts
}

onMounted(async () => {
  try {
    await auth.fetchMe()
    if (auth.user.personal_id) await loadWorkouts()
  } catch (e) {
    error.value = errorMessage(e)
  }
})

// RF02: vinculo ao personal
async function link() {
  error.value = ''
  try {
    await http.post('/auth/link', { invite_code: inviteCode.value })
    await auth.fetchMe()
    await loadWorkouts()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

// RF06: inicia a sessao e abre a tela de registro das series
async function start(workout) {
  starting.value = workout.id
  try {
    const { data } = await http.post('/sessions', { workout_id: workout.id })
    router.push(`/sessoes/${data.id}`)
  } catch (e) {
    error.value = errorMessage(e)
    starting.value = null
  }
}
</script>

<template>
  <h1 class="title is-4">Olá, {{ auth.user.name }}</h1>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <form v-if="!auth.user.personal_id" class="box" @submit.prevent="link">
    <p>Peça ao seu personal o código de convite para receber suas fichas.</p>
    <label>
      Código de convite
      <input class="input" v-model="inviteCode" maxlength="8" required style="text-transform: uppercase" />
    </label>
    <button class="button is-primary is-fullwidth">Vincular</button>
  </form>

  <template v-else>
    <p class="muted">Personal: {{ auth.user.personal_name }}</p>
    <h2 class="title is-5">Suas fichas</h2>
    <p v-if="!workouts.length" class="muted">Seu personal ainda não montou nenhuma ficha.</p>

    <!-- RF05: fichas ativas -->
    <div v-for="workout in workouts" :key="workout.id" class="box">
      <div class="row">
        <strong>{{ workout.name }}</strong>
        <button class="button is-primary" :disabled="starting === workout.id" @click="start(workout)">Iniciar treino</button>
      </div>
      <p v-if="workout.notes" class="muted">{{ workout.notes }}</p>
      <ol style="padding-left: 20px; margin-bottom: 0">
        <li v-for="item in workout.exercises" :key="item.id">
          {{ item.exercise_name }} — {{ item.sets }}x{{ item.reps }}
          <span v-if="item.suggested_load_kg" class="muted">({{ item.suggested_load_kg }} kg)</span>
        </li>
      </ol>
    </div>
  </template>
</template>
