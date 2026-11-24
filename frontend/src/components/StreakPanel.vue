<script setup>
import { computed, onMounted, ref } from 'vue'

import http, { errorMessage } from '../api/http'
import AppIcon from './AppIcon.vue'

// RF15: ofensiva, calendario de dias ativos e conquistas
const props = defineProps({
  studentId: { type: Number, default: null },
  compact: { type: Boolean, default: false },
})

const summary = ref(null)
const error = ref('')
const today = new Date().toLocaleDateString('sv-SE') // AAAA-MM-DD no fuso local

onMounted(async () => {
  try {
    const params = props.studentId ? { student_id: props.studentId } : {}
    const { data } = await http.get('/achievements', { params })
    summary.value = data
  } catch (e) {
    error.value = errorMessage(e)
  }
})

function dayClass(day) {
  return {
    trained: day.trained && !day.diet,
    diet: day.diet && !day.trained,
    both: day.trained && day.diet,
    today: day.day === today,
    future: day.future,
  }
}

function dayTitle(day) {
  const parts = []
  if (day.trained) parts.push('treinou')
  if (day.diet) parts.push('cumpriu a dieta')
  return `${new Date(`${day.day}T12:00`).toLocaleDateString('pt-BR')}: ${parts.join(' e ') || 'sem registro'}`
}

const unlocked = computed(() => summary.value?.badges.filter((b) => b.unlocked).length ?? 0)

// medalhas de tempo sem falha, separadas por trilha
const tracks = computed(() => {
  if (!summary.value) return []
  return [
    {
      id: 'treino',
      title: 'Treino sem falha',
      color: 'var(--treino)',
      icon: 'dumbbell',
      current: `${summary.value.training_weeks.current} semana(s) seguidas com ${summary.value.weekly_goal}+ treinos`,
      medals: summary.value.medals.filter((m) => m.track === 'treino'),
    },
    {
      id: 'dieta',
      title: 'Dieta sem falha',
      color: 'var(--dieta)',
      icon: 'utensils',
      current: `${summary.value.diet_streak.current} dia(s) seguidos com todas as refeições`,
      medals: summary.value.medals.filter((m) => m.track === 'dieta'),
    },
  ]
})

defineExpose({ summary })
</script>

<template>
  <p v-if="error" class="notification is-danger is-light">{{ error }}</p>

  <template v-if="summary">
    <div class="neon-card streak-hero is-highlight">
      <div class="streak-flame" :class="{ 'is-off': !summary.current_streak }">
        <AppIcon name="flame" :size="34" />
      </div>
      <div style="flex: 1">
        <p class="big-number">
          {{ summary.current_streak }}
          <span class="muted" style="font-size: 1rem">dia{{ summary.current_streak === 1 ? '' : 's' }} de ofensiva</span>
        </p>
        <p class="muted">
          Recorde: {{ summary.best_streak }} · {{ summary.active_days }} dias ativos
          <span v-if="!summary.active_today && summary.current_streak"> · treine ou cumpra a dieta hoje para manter</span>
        </p>
      </div>
    </div>

    <template v-if="!compact">
      <p class="section-title">Últimas 12 semanas</p>
      <div class="box">
        <div class="calendar">
          <div
            v-for="day in summary.calendar"
            :key="day.day"
            class="calendar-day"
            :class="dayClass(day)"
            :title="dayTitle(day)"
          ></div>
        </div>
        <div class="legend" style="margin-top: 0.75rem">
          <span style="--c: var(--treino)">Treinou</span>
          <span style="--c: var(--dieta)">Cumpriu a dieta</span>
          <span style="--c: linear-gradient(135deg, var(--treino) 50%, var(--dieta) 50%)">Os dois</span>
        </div>
      </div>

      <p class="section-title">Medalhas de tempo sem falha</p>
      <div class="stat-grid">
        <div v-for="track in tracks" :key="track.id" class="neon-card" :style="{ '--accent': track.color }">
          <div class="card-head">
            <div>
              <p class="card-title">{{ track.title }}</p>
              <p class="muted">{{ track.current }}</p>
            </div>
            <span class="avatar"><AppIcon :name="track.icon" /></span>
          </div>
          <div class="medal-row">
            <div
              v-for="medal in track.medals"
              :key="medal.id"
              class="medal"
              :class="[medal.tier, { locked: !medal.unlocked }]"
              :title="medal.title"
            >
              <div class="medal-coin"><AppIcon name="trophy" :size="20" /></div>
              <strong>{{ medal.target }} {{ medal.unit === 'semanas' ? (medal.target === 1 ? 'semana' : 'semanas') : 'dias' }}</strong>
              <div class="meter-track"><div class="meter-fill" :style="{ width: `${(100 * medal.progress) / medal.target}%` }"></div></div>
            </div>
          </div>
        </div>
      </div>

      <p class="section-title">Conquistas ({{ unlocked }}/{{ summary.badges.length }})</p>
      <div class="badge-grid">
        <div
          v-for="badge in summary.badges"
          :key="badge.id"
          class="badge-item"
          :class="{ locked: !badge.unlocked }"
        >
          <div class="badge-icon"><AppIcon :name="badge.unlocked ? 'trophy' : 'flame'" /></div>
          <strong style="font-size: 0.9rem">{{ badge.title }}</strong>
          <p class="muted" style="font-size: 0.78rem">{{ badge.description }}</p>
        </div>
      </div>
    </template>
  </template>
</template>
