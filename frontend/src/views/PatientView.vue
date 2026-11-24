<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import http, { errorMessage } from '../api/http'
import StreakPanel from '../components/StreakPanel.vue'
import WeightChart from '../components/WeightChart.vue'
import { formatDate } from '../utils/format'

// RF11, RF12, RF13: paciente do nutricionista (plano, adesao, peso, ofensiva)
const route = useRoute()
const studentId = Number(route.params.id)

const patient = ref(null)
const plans = ref([])
const adherence = ref([])
const weights = ref([])
const tab = ref('plano')
const error = ref('')

async function loadPlans() {
  const { data } = await http.get('/nutrition/plans', { params: { student_id: studentId } })
  plans.value = data.plans
}

onMounted(async () => {
  try {
    const [p, a, w] = await Promise.all([
      http.get('/nutrition/patients'),
      http.get('/nutrition/adherence', { params: { student_id: studentId, days: 14 } }),
      http.get('/nutrition/weights', { params: { student_id: studentId } }),
      loadPlans(),
    ])
    patient.value = p.data.patients.find((x) => x.id === studentId)
    adherence.value = a.data.days
    weights.value = w.data.weights
  } catch (e) {
    error.value = errorMessage(e)
  }
})

async function toggleActive(plan) {
  try {
    await http.put(`/nutrition/plans/${plan.id}`, { is_active: !plan.is_active })
    await loadPlans()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

const shortDate = (day) => formatDate(`${day}T12:00`).slice(0, 5)
const avgAdherence = computed(() => {
  const planned = adherence.value.reduce((s, d) => s + d.total, 0)
  return planned ? Math.round((100 * adherence.value.reduce((s, d) => s + d.done, 0)) / planned) : null
})
</script>

<template>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <template v-if="patient">
    <h1 class="title is-4">{{ patient.name }}</h1>

    <div class="tabs">
      <ul>
        <li :class="{ 'is-active': tab === 'plano' }"><a @click="tab = 'plano'">Plano</a></li>
        <li :class="{ 'is-active': tab === 'adesao' }"><a @click="tab = 'adesao'">Adesão</a></li>
        <li :class="{ 'is-active': tab === 'peso' }"><a @click="tab = 'peso'">Peso</a></li>
        <li :class="{ 'is-active': tab === 'ofensiva' }"><a @click="tab = 'ofensiva'">Ofensiva</a></li>
      </ul>
    </div>

    <template v-if="tab === 'plano'">
      <RouterLink :to="`/planos/novo?aluno=${studentId}`">
        <button class="button is-primary is-fullwidth" style="margin-bottom: 12px">Novo plano alimentar</button>
      </RouterLink>
      <p v-if="!plans.length" class="muted">Nenhum plano montado para este paciente.</p>

      <div
        v-for="plan in plans"
        :key="plan.id"
        class="neon-card"
        :class="{ 'is-highlight': plan.is_active }"
        style="--accent: var(--dieta); margin-bottom: 0.75rem"
      >
        <div class="card-head">
          <div>
            <p class="card-title">{{ plan.name }}</p>
            <p class="muted">{{ plan.goal || 'Sem objetivo definido' }} · {{ plan.total_kcal }} kcal/dia</p>
          </div>
          <span class="chip">{{ plan.is_active ? 'Ativo' : 'Inativo' }}</span>
        </div>
        <ol style="padding-left: 20px; margin: 0">
          <li v-for="meal in plan.meals" :key="meal.id">
            <strong>{{ meal.time || '' }} {{ meal.name }}</strong>: {{ meal.foods }}
            <span v-if="meal.kcal" class="muted">({{ meal.kcal }} kcal)</span>
          </li>
        </ol>
        <div class="row" style="justify-content: flex-end">
          <RouterLink :to="`/planos/${plan.id}`"><button class="button is-light">Editar</button></RouterLink>
          <button class="button is-light" @click="toggleActive(plan)">
            {{ plan.is_active ? 'Desativar' : 'Reativar' }}
          </button>
        </div>
      </div>
    </template>

    <div v-else-if="tab === 'adesao'" class="neon-card" style="--accent: var(--dieta)">
      <p class="card-title">Refeições marcadas por dia</p>
      <p class="muted">Média dos últimos 14 dias: {{ avgAdherence ?? '—' }}{{ avgAdherence !== null ? '%' : '' }}</p>
      <WeightChart
        type="bar"
        :labels="adherence.map((d) => shortDate(d.day))"
        :values="adherence.map((d) => d.percent)"
        color="--dieta"
        unit="%"
        :max="100"
      />
    </div>

    <div v-else-if="tab === 'peso'" class="neon-card" style="--accent: var(--foco)">
      <p class="card-title">Evolução do peso</p>
      <p v-if="weights.length < 2" class="muted">O paciente precisa registrar o peso pelo menos duas vezes.</p>
      <WeightChart
        v-else
        :labels="weights.map((w) => shortDate(w.day))"
        :values="weights.map((w) => w.weight_kg)"
        color="--foco"
        unit="kg"
      />
    </div>

    <StreakPanel v-else :student-id="studentId" />
  </template>
</template>
