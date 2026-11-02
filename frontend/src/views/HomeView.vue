<script setup>
import PersonalDashboard from '../components/PersonalDashboard.vue'
import StudentHome from '../components/StudentHome.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <PersonalDashboard v-if="auth.isPersonal" />
  <StudentHome v-else />
</template>
