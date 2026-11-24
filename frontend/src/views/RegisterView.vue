<script setup>
import AppLogo from '../components/AppLogo.vue'
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
  <div class="auth-hero">
    <AppLogo :size="56" />
  </div>
  <h1 class="title is-4">Criar conta</h1>
  <form class="box" @submit.prevent="submit">
    <label>Nome <input class="input" v-model="form.name" required maxlength="120" /></label>
    <label>E-mail <input class="input" v-model="form.email" type="email" required maxlength="160" /></label>
    <label>
      Senha (mínimo 6 caracteres)
      <input class="input" v-model="form.password" type="password" minlength="6" required />
    </label>
    <label>
      Eu sou
      <div class="select is-fullwidth">
        <select v-model="form.role">
          <option value="aluno">Aluno</option>
          <option value="personal">Personal trainer</option>
          <option value="nutricionista">Nutricionista</option>
        </select>
      </div>
    </label>
    <p v-if="error" class="notification is-danger is-light">{{ error }}</p>
    <button class="button is-primary is-fullwidth" :disabled="loading">Cadastrar</button>
  </form>
  <p class="muted">Já tem conta? <RouterLink to="/login">Entrar</RouterLink></p>
</template>
