<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import AppIcon from './components/AppIcon.vue'
import AppLogo from './components/AppLogo.vue'
import { useAuthStore } from './stores/auth'
import { theme, toggleTheme } from './utils/theme'

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
  <nav v-if="auth.isLogged" class="navbar app-nav" role="navigation">
    <div class="navbar-brand">
      <RouterLink to="/inicio" class="navbar-item brand-link"><AppLogo /></RouterLink>
      <a
        class="navbar-item theme-toggle is-hidden-desktop"
        :aria-label="theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro'"
        @click="toggleTheme"
      >
        <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
      </a>
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
        <template v-if="auth.isPersonal">
          <RouterLink to="/inicio" class="navbar-item">Alunos</RouterLink>
          <RouterLink to="/exercicios" class="navbar-item">Exercícios</RouterLink>
        </template>
        <RouterLink v-else-if="auth.isNutri" to="/inicio" class="navbar-item">Pacientes</RouterLink>
        <template v-else>
          <RouterLink to="/inicio" class="navbar-item">Início</RouterLink>
          <RouterLink to="/alimentacao" class="navbar-item">Alimentação</RouterLink>
          <RouterLink to="/conquistas" class="navbar-item">Ofensiva</RouterLink>
          <RouterLink to="/historico" class="navbar-item">Histórico</RouterLink>
          <RouterLink to="/evolucao" class="navbar-item">Evolução</RouterLink>
        </template>
        <a
          class="navbar-item theme-toggle is-hidden-touch"
          :aria-label="theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro'"
          @click.stop="toggleTheme"
        >
          <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
        </a>
        <a class="navbar-item" @click="logout">Sair</a>
      </div>
    </div>
  </nav>

  <a
    v-else
    class="floating-theme"
    :aria-label="theme === 'dark' ? 'Usar tema claro' : 'Usar tema escuro'"
    @click="toggleTheme"
  >
    <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
  </a>

  <main class="container">
    <RouterView />
  </main>
</template>

<style scoped>
.theme-toggle {
  margin-left: auto;
}

.navbar-brand .theme-toggle {
  margin-left: auto;
}

.floating-theme {
  position: fixed;
  top: 1rem;
  right: 1rem;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}
</style>
