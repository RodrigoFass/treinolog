<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import http, { errorMessage } from '../api/http'

// RF11: o nutricionista monta ou edita o plano alimentar
const route = useRoute()
const router = useRouter()
const planId = route.params.id ? Number(route.params.id) : null

const form = ref({ name: '', goal: '', notes: '' })
const meals = ref([
  { name: 'Café da manhã', time: '07:00', foods: '', kcal: null },
  { name: 'Almoço', time: '12:30', foods: '', kcal: null },
  { name: 'Jantar', time: '19:30', foods: '', kcal: null },
])
const studentId = ref(Number(route.query.aluno) || null)
const error = ref('')
const saving = ref(false)

onMounted(async () => {
  if (!planId) return
  try {
    const { data } = await http.get(`/nutrition/plans/${planId}`)
    form.value = { name: data.name, goal: data.goal || '', notes: data.notes || '' }
    meals.value = data.meals.map(({ name, time, foods, kcal }) => ({ name, time: time || '', foods, kcal }))
    studentId.value = data.student_id
  } catch (e) {
    error.value = errorMessage(e)
  }
})

const totalKcal = computed(() => meals.value.reduce((s, m) => s + (Number(m.kcal) || 0), 0))

function addMeal() {
  meals.value.push({ name: '', time: '', foods: '', kcal: null })
}

function removeMeal(index) {
  meals.value.splice(index, 1)
}

async function save() {
  error.value = ''
  saving.value = true
  const payload = {
    ...form.value,
    goal: form.value.goal || null,
    notes: form.value.notes || null,
    meals: meals.value.map((m) => ({
      name: m.name,
      time: m.time || null,
      foods: m.foods,
      kcal: m.kcal === null || m.kcal === '' ? null : Number(m.kcal),
    })),
  }
  try {
    if (planId) {
      await http.put(`/nutrition/plans/${planId}`, payload)
    } else {
      await http.post('/nutrition/plans', { ...payload, student_id: studentId.value })
    }
    router.push(`/pacientes/${studentId.value}`)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <h1 class="title is-4">{{ planId ? 'Editar plano alimentar' : 'Novo plano alimentar' }}</h1>

  <form @submit.prevent="save">
    <div class="box">
      <label>Nome do plano <input class="input" v-model="form.name" required maxlength="60" placeholder="Ex.: Ganho de massa" /></label>
      <label>Objetivo <input class="input" v-model="form.goal" maxlength="120" placeholder="Ex.: Ganhar 3 kg em 3 meses" /></label>
      <label>Observações <textarea class="textarea" v-model="form.notes" rows="2"></textarea></label>
    </div>

    <div class="row">
      <p class="section-title">Refeições ({{ meals.length }})</p>
      <span class="chip" style="--accent: var(--dieta)">{{ totalKcal }} kcal/dia</span>
    </div>

    <div v-for="(meal, index) in meals" :key="index" class="box">
      <div class="columns is-mobile" style="margin-bottom: 0">
        <div class="column">
          <label>Refeição <input class="input" v-model="meal.name" required maxlength="60" /></label>
        </div>
        <div class="column is-4">
          <label>Horário <input class="input" v-model="meal.time" type="time" /></label>
        </div>
      </div>
      <label>
        Alimentos e quantidades
        <textarea class="textarea" v-model="meal.foods" rows="2" required maxlength="1000"></textarea>
      </label>
      <div class="row">
        <label style="margin: 0; flex: 1">
          Calorias (kcal)
          <input class="input" v-model="meal.kcal" type="number" min="0" max="5000" />
        </label>
        <button
          v-if="meals.length > 1"
          type="button"
          class="button is-danger is-light"
          style="align-self: flex-end"
          @click="removeMeal(index)"
        >
          Remover
        </button>
      </div>
    </div>

    <button type="button" class="button is-light is-fullwidth" style="margin-bottom: 1rem" @click="addMeal">
      Adicionar refeição
    </button>

    <p v-if="error" class="notification is-danger is-light">{{ error }}</p>
    <button class="button is-primary is-fullwidth" :disabled="saving">Salvar plano</button>
  </form>
</template>
