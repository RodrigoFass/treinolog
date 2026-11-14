<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

// controla o menu "hamburguer" no celular
const menuAberto = ref(false)

function logout() {
  menuAberto.value = false
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav v-if="auth.isLogged" class="navbar is-primary" role="navigation">
    <div class="navbar-brand">
      <RouterLink to="/inicio" class="navbar-item has-text-weight-bold">TreinoLog</RouterLink>
      <a
        class="navbar-burger"
        :class="{ 'is-active': menuAberto }"
        role="button"
        aria-label="menu"
        @click="menuAberto = !menuAberto"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>

    <div class="navbar-menu" :class="{ 'is-active': menuAberto }" @click="menuAberto = false">
      <div class="navbar-end">
        <RouterLink to="/inicio" class="navbar-item">
          {{ auth.isPersonal ? 'Alunos' : 'Fichas' }}
        </RouterLink>
        <RouterLink v-if="auth.isPersonal" to="/exercicios" class="navbar-item">Exercícios</RouterLink>
        <template v-if="auth.isAluno">
          <RouterLink to="/historico" class="navbar-item">Histórico</RouterLink>
          <RouterLink to="/evolucao" class="navbar-item">Evolução</RouterLink>
        </template>
        <a class="navbar-item" @click="logout">Sair</a>
      </div>
    </div>
  </nav>

  <main class="container">
    <RouterView />
  </main>
</template>
