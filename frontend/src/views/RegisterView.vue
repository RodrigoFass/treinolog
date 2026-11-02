<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ name: '', email: '', password: '', role: 'aluno' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(form)
    router.push('/inicio')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <h1>Criar conta</h1>
  <form class="card" @submit.prevent="submit">
    <label>Nome <input v-model="form.name" required maxlength="120" /></label>
    <label>E-mail <input v-model="form.email" type="email" required maxlength="160" /></label>
    <label>
      Senha (mínimo 6 caracteres)
      <input v-model="form.password" type="password" minlength="6" required />
    </label>
    <label>
      Eu sou
      <select v-model="form.role">
        <option value="aluno">Aluno</option>
        <option value="personal">Personal trainer</option>
      </select>
    </label>
    <p v-if="error" class="error">{{ error }}</p>
    <button class="full" :disabled="loading">Cadastrar</button>
  </form>
  <p class="muted">Já tem conta? <RouterLink to="/login">Entrar</RouterLink></p>
</template>
