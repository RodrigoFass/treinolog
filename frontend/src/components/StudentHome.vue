<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import http, { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'
import AppIcon from './AppIcon.vue'
import StatCard from './StatCard.vue'
import StreakPanel from './StreakPanel.vue'

const auth = useAuthStore()
const router = useRouter()

const workouts = ref([])
const today = ref(null)
const achievements = ref(null)
const inviteCode = ref('')
const error = ref('')
const linkMessage = ref('')
const starting = ref(null)

async function loadWorkouts() {
  const { data } = await http.get('/workouts')
  workouts.value = data.workouts
}

async function loadToday() {
  const { data } = await http.get('/nutrition/today')
  today.value = data
}

async function loadAchievements() {
  const { data } = await http.get('/achievements', { params: { weeks: 1 } })
  achievements.value = data
}

async function loadAll() {
  const tasks = [loadAchievements()]
  if (auth.user.personal_id) tasks.push(loadWorkouts())
  if (auth.user.nutritionist_id) tasks.push(loadToday())
  await Promise.all(tasks)
}

onMounted(async () => {
  try {
    await auth.fetchMe()
    await loadAll()
  } catch (e) {
    error.value = errorMessage(e)
  }
})

// treinos desta semana e a meta semanal (vem do backend)
const trainedThisWeek = computed(() => achievements.value?.trained_this_week ?? 0)
const weeklyGoal = computed(() => achievements.value?.weekly_goal ?? 3)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bom dia'
  if (hour < 18) return 'Boa tarde'
  return 'Boa noite'
})

// RF02 / RF10: vinculo ao personal ou ao nutricionista pelo codigo
async function link() {
  error.value = ''
  linkMessage.value = ''
  try {
    const { data } = await http.post('/auth/link', { invite_code: inviteCode.value })
    linkMessage.value = `Pronto! Você agora está com ${data.name} (${data.role}).`
    inviteCode.value = ''
    await auth.fetchMe()
    await loadAll()
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
  <h1 class="title is-3" style="margin-bottom: 0.25rem">{{ greeting }}, {{ auth.user.name.split(' ')[0] }}</h1>
  <p class="muted" style="margin-bottom: 1rem">
    <span v-if="auth.user.personal_name">Personal: {{ auth.user.personal_name }}</span>
    <span v-if="auth.user.personal_name && auth.user.nutritionist_name"> · </span>
    <span v-if="auth.user.nutritionist_name">Nutricionista: {{ auth.user.nutritionist_name }}</span>
  </p>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <RouterLink to="/conquistas" style="color: inherit"><StreakPanel compact /></RouterLink>

  <p class="section-title">Hoje</p>
  <div class="stat-grid">
    <StatCard
      v-if="auth.user.personal_id"
      title="Treinos"
      subtitle="nesta semana"
      color="var(--treino)"
      icon="dumbbell"
      :done="Math.min(trainedThisWeek, weeklyGoal)"
      :total="weeklyGoal"
      meter-label="Meta da semana"
      :highlight="trainedThisWeek >= weeklyGoal"
    />
    <RouterLink v-if="today" to="/alimentacao" style="color: inherit">
      <StatCard
        title="Alimentação"
        :subtitle="today.plan ? `${today.kcal_done} kcal de ${today.plan.total_kcal}` : 'sem plano ainda'"
        color="var(--dieta)"
        icon="utensils"
        :done="today.done"
        :total="today.total"
        meter-label="Refeições de hoje"
        :highlight="today.total > 0 && today.done === today.total"
      />
    </RouterLink>
  </div>

  <template v-if="auth.user.personal_id">
    <p class="section-title">Suas fichas</p>
    <p v-if="!workouts.length" class="muted">Seu personal ainda não montou nenhuma ficha.</p>

    <!-- RF05: fichas ativas -->
    <div v-for="workout in workouts" :key="workout.id" class="neon-card" style="--accent: var(--treino); margin-bottom: 0.75rem">
      <div class="card-head">
        <div>
          <p class="card-title">{{ workout.name }}</p>
          <p v-if="workout.notes" class="muted">{{ workout.notes }}</p>
        </div>
        <button class="button is-primary" :disabled="starting === workout.id" @click="start(workout)">
          Iniciar treino
        </button>
      </div>
      <ol style="padding-left: 20px; margin: 0">
        <li v-for="item in workout.exercises" :key="item.id">
          {{ item.exercise_name }} — {{ item.sets }}x{{ item.reps }}
          <span v-if="item.suggested_load_kg" class="muted">({{ item.suggested_load_kg }} kg)</span>
        </li>
      </ol>
    </div>
  </template>

  <!-- vinculo: aparece enquanto falta o personal ou o nutricionista -->
  <form
    v-if="!auth.user.personal_id || !auth.user.nutritionist_id"
    class="box"
    style="margin-top: 1rem"
    @submit.prevent="link"
  >
    <p style="margin-bottom: 0.5rem">
      <AppIcon name="users" :size="18" />
      Tem um código de convite do seu
      {{ !auth.user.personal_id && !auth.user.nutritionist_id ? 'personal ou nutricionista' : auth.user.personal_id ? 'nutricionista' : 'personal' }}?
    </p>
    <div class="row" style="flex-wrap: nowrap">
      <input
        class="input"
        v-model="inviteCode"
        maxlength="8"
        required
        placeholder="Ex.: AB12CD34"
        style="text-transform: uppercase"
      />
      <button class="button is-primary">Vincular</button>
    </div>
    <p v-if="linkMessage" class="muted" style="margin-top: 0.5rem">{{ linkMessage }}</p>
  </form>
</template>
