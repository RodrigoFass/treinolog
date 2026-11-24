<script setup>
import AppLogo from '../components/AppLogo.vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { errorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
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
    <p class="muted">Treino, alimentação e ofensiva num lugar só.</p>
  </div>
  <h1 class="title is-4">Entrar</h1>
  <form class="box" @submit.prevent="submit">
    <label>E-mail <input class="input" v-model="email" type="email" autocomplete="email" required /></label>
    <label>
      Senha <input class="input" v-model="password" type="password" autocomplete="current-password" required />
    </label>
    <p v-if="error" class="notification is-danger is-light">{{ error }}</p>
    <button class="button is-primary is-fullwidth" :disabled="loading">Entrar</button>
  </form>
  <p class="muted">Ainda não tem conta? <RouterLink to="/cadastro">Cadastre-se</RouterLink></p>
</template>
