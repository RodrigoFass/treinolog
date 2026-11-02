<script setup>
import { useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header v-if="auth.isLogged" class="topbar">
    <RouterLink to="/inicio" class="brand">TreinoLog</RouterLink>
    <nav>
      <RouterLink to="/inicio">{{ auth.isPersonal ? 'Alunos' : 'Fichas' }}</RouterLink>
      <RouterLink v-if="auth.isPersonal" to="/exercicios">Exercícios</RouterLink>
      <template v-if="auth.isAluno">
        <RouterLink to="/historico">Histórico</RouterLink>
        <RouterLink to="/evolucao">Evolução</RouterLink>
      </template>
      <button class="link" @click="logout">Sair</button>
    </nav>
  </header>

  <main class="container">
    <RouterView />
  </main>
</template>
