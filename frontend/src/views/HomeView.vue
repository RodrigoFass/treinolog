<script setup>
import NutriDashboard from '../components/NutriDashboard.vue'
import PersonalDashboard from '../components/PersonalDashboard.vue'
import StudentHome from '../components/StudentHome.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <PersonalDashboard v-if="auth.isPersonal" />
  <NutriDashboard v-else-if="auth.isNutri" />
  <StudentHome v-else />
</template>
