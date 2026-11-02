<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import http, { errorMessage } from '../api/http'

// RF03: catalogo de exercicios (cadastrar, editar, listar e excluir)
const exercises = ref([])
const filter = ref('')
const form = reactive({ id: null, name: '', muscle_group: '', description: '' })
const error = ref('')

const groups = computed(() => [...new Set(exercises.value.map((e) => e.muscle_group))].sort())
const visible = computed(() =>
  filter.value ? exercises.value.filter((e) => e.muscle_group === filter.value) : exercises.value,
)

async function load() {
  const { data } = await http.get('/exercises')
  exercises.value = data.exercises
}

onMounted(load)

function edit(exercise) {
  Object.assign(form, exercise)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function reset() {
  Object.assign(form, { id: null, name: '', muscle_group: '', description: '' })
}

async function save() {
  error.value = ''
  const payload = {
    name: form.name,
    muscle_group: form.muscle_group,
    description: form.description || null,
  }
  try {
    if (form.id) {
      await http.put(`/exercises/${form.id}`, payload)
    } else {
      await http.post('/exercises', payload)
    }
    reset()
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function remove(exercise) {
  if (!confirm(`Excluir "${exercise.name}"?`)) return
  error.value = ''
  try {
    await http.delete(`/exercises/${exercise.id}`)
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <h1>Catálogo de exercícios</h1>

  <form class="card" @submit.prevent="save">
    <label>Nome <input v-model="form.name" required maxlength="120" /></label>
    <label>
      Grupo muscular
      <input v-model="form.muscle_group" list="groups" required maxlength="60" />
      <datalist id="groups">
        <option v-for="group in groups" :key="group" :value="group" />
      </datalist>
    </label>
    <label>Descrição <textarea v-model="form.description" rows="2"></textarea></label>
    <div class="row">
      <button v-if="form.id" type="button" class="secondary" @click="reset">Cancelar</button>
      <button>{{ form.id ? 'Salvar alterações' : 'Adicionar exercício' }}</button>
    </div>
  </form>

  <p v-if="error" class="error">{{ error }}</p>

  <label v-if="groups.length">
    Filtrar por grupo
    <select v-model="filter">
      <option value="">Todos</option>
      <option v-for="group in groups" :key="group" :value="group">{{ group }}</option>
    </select>
  </label>

  <div v-for="exercise in visible" :key="exercise.id" class="card">
    <div class="row">
      <div>
        <strong>{{ exercise.name }}</strong>
        <span class="badge" style="margin-left: 6px">{{ exercise.muscle_group }}</span>
      </div>
      <div class="row">
        <button class="secondary" @click="edit(exercise)">Editar</button>
        <button class="danger" @click="remove(exercise)">Excluir</button>
      </div>
    </div>
    <p v-if="exercise.description" class="muted">{{ exercise.description }}</p>
  </div>
</template>
