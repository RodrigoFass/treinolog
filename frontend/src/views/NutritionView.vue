<script setup>
import { computed, onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import AppIcon from '../components/AppIcon.vue'
import ProgressRing from '../components/ProgressRing.vue'
import WeightChart from '../components/WeightChart.vue'
import { useAuthStore } from '../stores/auth'
import { formatDate } from '../utils/format'

// RF12 e RF13: refeicoes do dia e registro de peso (aluno)
const auth = useAuthStore()
const today = ref(null)
const weights = ref([])
const weight = ref('')
const error = ref('')
const saving = ref(null)

async function load() {
  const [day, w] = await Promise.all([
    http.get('/nutrition/today'),
    http.get('/nutrition/weights'),
  ])
  today.value = day.data
  weights.value = w.data.weights
}

onMounted(async () => {
  try {
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  }
})

async function toggle(meal) {
  saving.value = meal.id
  error.value = ''
  try {
    const { data } = await http.put(`/nutrition/meals/${meal.id}/check`, { done: !meal.done })
    today.value = data
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = null
  }
}

async function saveWeight() {
  error.value = ''
  try {
    await http.post('/nutrition/weights', { weight_kg: Number(weight.value) })
    weight.value = ''
    const { data } = await http.get('/nutrition/weights')
    weights.value = data.weights
  } catch (e) {
    error.value = errorMessage(e)
  }
}

const kcalRatio = computed(() =>
  today.value?.plan?.total_kcal ? today.value.kcal_done / today.value.plan.total_kcal : 0,
)
const lastWeight = computed(() => weights.value.at(-1))
const weightDelta = computed(() => {
  if (weights.value.length < 2) return null
  return (weights.value.at(-1).weight_kg - weights.value[0].weight_kg).toFixed(1)
})
</script>

<template>
  <h1 class="title is-4">Alimentação</h1>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <p v-if="!auth.user.nutritionist_id" class="box">
    Você ainda não tem nutricionista. Peça o código de convite e vincule na tela inicial.
  </p>

  <template v-if="today">
    <div v-if="today.plan" class="neon-card is-highlight" style="--accent: var(--dieta)">
      <div class="card-head">
        <div>
          <p class="card-title">{{ today.plan.name }}</p>
          <p v-if="today.plan.goal" class="muted">Objetivo: {{ today.plan.goal }}</p>
          <p class="big-number" style="margin-top: 0.5rem">
            {{ today.done }}/{{ today.total }}
            <span class="muted" style="font-size: 1rem">refeições</span>
          </p>
          <p class="muted">{{ today.kcal_done }} de {{ today.plan.total_kcal }} kcal</p>
        </div>
        <ProgressRing :value="kcalRatio" color="var(--dieta)" icon="utensils" :size="96" />
      </div>
    </div>
    <p v-else-if="auth.user.nutritionist_id" class="muted">Seu nutricionista ainda não montou o plano.</p>

    <p v-if="today.meals.length" class="section-title">Refeições de hoje</p>
    <div v-for="meal in today.meals" :key="meal.id" class="list-card">
      <button
        class="meal-check"
        :class="{ done: meal.done }"
        :disabled="saving === meal.id"
        :aria-label="meal.done ? `Desmarcar ${meal.name}` : `Marcar ${meal.name} como feita`"
        @click="toggle(meal)"
      >
        <AppIcon v-if="meal.done" name="check" :size="18" />
      </button>
      <div style="flex: 1">
        <div class="row">
          <strong>{{ meal.name }}</strong>
          <span class="chip" style="--accent: var(--dieta)">
            {{ meal.time || 'livre' }}<template v-if="meal.kcal"> · {{ meal.kcal }} kcal</template>
          </span>
        </div>
        <p class="muted" style="margin-top: 2px">{{ meal.foods }}</p>
      </div>
    </div>
  </template>

  <p class="section-title">Peso</p>
  <div class="neon-card" style="--accent: var(--foco)">
    <div class="card-head">
      <div>
        <p class="big-number">{{ lastWeight ? `${lastWeight.weight_kg} kg` : '—' }}</p>
        <p class="muted">
          <template v-if="lastWeight">Último registro: {{ formatDate(`${lastWeight.day}T12:00`) }}</template>
          <template v-if="weightDelta !== null"> · {{ weightDelta > 0 ? '+' : '' }}{{ weightDelta }} kg desde o início</template>
        </p>
      </div>
      <AppIcon name="scale" :size="34" style="color: var(--foco)" />
    </div>
    <form class="row" style="flex-wrap: nowrap" @submit.prevent="saveWeight">
      <input
        class="input"
        v-model="weight"
        type="number"
        inputmode="decimal"
        min="20"
        max="399"
        step="0.1"
        placeholder="Peso de hoje (kg)"
        required
      />
      <button class="button is-primary">Registrar</button>
    </form>
    <WeightChart
      v-if="weights.length > 1"
      :labels="weights.map((w) => formatDate(`${w.day}T12:00`).slice(0, 5))"
      :values="weights.map((w) => w.weight_kg)"
      color="--foco"
      unit="kg"
    />
  </div>
</template>
