<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import http, { errorMessage } from '../api/http'

// RF04: montar ficha com exercicios, series, repeticoes, carga sugerida e descanso
const route = useRoute()
const router = useRouter()

const workoutId = route.params.id ? Number(route.params.id) : null
const isNew = computed(() => workoutId === null)

const catalog = ref([])
const loaded = ref(false)
const form = reactive({ student_id: Number(route.query.aluno) || null, name: '', notes: '' })
const items = ref([])
const newItem = reactive({
  exercise_id: null,
  sets: 3,
  reps: '10',
  suggested_load_kg: null,
  rest_seconds: 60,
})
const error = ref('')
const message = ref('')

onMounted(async () => {
  try {
    catalog.value = (await http.get('/exercises')).data.exercises
    if (!isNew.value) {
      const { data } = await http.get(`/workouts/${workoutId}`)
      Object.assign(form, { student_id: data.student_id, name: data.name, notes: data.notes })
      items.value = data.exercises
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loaded.value = true
  }
})

function prescription(item) {
  return {
    sets: Number(item.sets),
    reps: String(item.reps),
    suggested_load_kg: item.suggested_load_kg === '' ? null : item.suggested_load_kg,
    rest_seconds: item.rest_seconds === '' ? null : item.rest_seconds,
  }
}

function exerciseName(id) {
  return catalog.value.find((e) => e.id === id)?.name
}

async function addItem() {
  error.value = ''
  if (!newItem.exercise_id) {
    error.value = 'Escolha um exercício do catálogo.'
    return
  }
  const payload = { exercise_id: newItem.exercise_id, ...prescription(newItem) }

  if (isNew.value) {
    // Ficha ainda nao existe: guarda na lista e envia tudo ao salvar
    items.value.push({ ...payload, exercise_name: exerciseName(payload.exercise_id) })
  } else {
    try {
      const { data } = await http.post(`/workouts/${workoutId}/exercises`, payload)
      items.value.push(data)
    } catch (e) {
      error.value = errorMessage(e)
      return
    }
  }
  newItem.exercise_id = null
}

async function updateItem(item) {
  if (isNew.value) return
  error.value = ''
  try {
    await http.put(`/workouts/${workoutId}/exercises/${item.id}`, prescription(item))
    message.value = `${item.exercise_name} atualizado.`
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function removeItem(index) {
  const item = items.value[index]
  error.value = ''
  if (!isNew.value) {
    try {
      await http.delete(`/workouts/${workoutId}/exercises/${item.id}`)
    } catch (e) {
      error.value = errorMessage(e)
      return
    }
  }
  items.value.splice(index, 1)
}

async function save() {
  error.value = ''
  message.value = ''
  try {
    if (isNew.value) {
      await http.post('/workouts', {
        ...form,
        exercises: items.value.map((item) => ({
          exercise_id: item.exercise_id,
          ...prescription(item),
        })),
      })
    } else {
      await http.put(`/workouts/${workoutId}`, { name: form.name, notes: form.notes || null })
    }
    router.push(`/alunos/${form.student_id}`)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function remove() {
  if (!confirm('Excluir esta ficha?')) return
  try {
    await http.delete(`/workouts/${workoutId}`)
    router.push(`/alunos/${form.student_id}`)
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <h1 class="title is-4">{{ isNew ? 'Nova ficha' : 'Editar ficha' }}</h1>

  <form class="box" @submit.prevent="save">
    <label>Nome da ficha <input class="input" v-model="form.name" placeholder="Treino A" maxlength="60" required /></label>
    <label>Observações <textarea class="textarea" v-model="form.notes" rows="2"></textarea></label>
    <button class="button is-primary is-fullwidth">{{ isNew ? 'Salvar ficha' : 'Salvar nome e observações' }}</button>
  </form>

  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>
  <p v-if="message" class="notification is-success is-light">{{ message }}</p>

  <h2 class="title is-5">Exercícios</h2>
  <p v-if="!items.length" class="muted">Adicione exercícios do seu catálogo abaixo.</p>

  <div v-for="(item, index) in items" :key="item.id ?? index" class="box">
    <div class="row">
      <strong>{{ index + 1 }}. {{ item.exercise_name }}</strong>
      <button class="button is-danger is-small" type="button" @click="removeItem(index)">Remover</button>
    </div>
    <div class="columns is-mobile">
      <label class="column">Séries <input class="input" v-model.number="item.sets" type="number" min="1" max="20" /></label>
      <label class="column">Reps <input class="input" v-model="item.reps" maxlength="10" /></label>
      <label class="column">Carga (kg) <input class="input" v-model.number="item.suggested_load_kg" type="number" min="0" step="0.5" /></label>
    </div>
    <label>Descanso (s) <input class="input" v-model.number="item.rest_seconds" type="number" min="0" /></label>
    <button v-if="!isNew" class="button is-light is-fullwidth" type="button" @click="updateItem(item)">
      Salvar exercício
    </button>
  </div>

  <div class="box">
    <strong>Adicionar exercício</strong>
    <label>
      Exercício
      <div class="select is-fullwidth">
        <select v-model="newItem.exercise_id">
          <option :value="null" disabled>Escolha...</option>
          <option v-for="exercise in catalog" :key="exercise.id" :value="exercise.id">
            {{ exercise.name }} ({{ exercise.muscle_group }})
          </option>
        </select>
      </div>
    </label>
    <div class="columns is-mobile">
      <label class="column">Séries <input class="input" v-model.number="newItem.sets" type="number" min="1" max="20" /></label>
      <label class="column">Reps <input class="input" v-model="newItem.reps" maxlength="10" /></label>
      <label class="column">Carga (kg) <input class="input" v-model.number="newItem.suggested_load_kg" type="number" min="0" step="0.5" /></label>
    </div>
    <label>Descanso (s) <input class="input" v-model.number="newItem.rest_seconds" type="number" min="0" /></label>
    <button class="button is-primary is-fullwidth" type="button" @click="addItem">Adicionar</button>
    <p v-if="loaded && !catalog.length" class="muted">
      Seu catálogo está vazio. <RouterLink to="/exercicios">Cadastre exercícios</RouterLink>.
    </p>
  </div>

  <button v-if="!isNew" class="button is-danger is-fullwidth" @click="remove">Excluir ficha</button>
</template>
