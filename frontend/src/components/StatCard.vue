<script setup>
import { computed } from 'vue'

import ProgressRing from './ProgressRing.vue'

// Card com anel de progresso e barra embaixo
const props = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  color: { type: String, default: 'var(--foco)' },
  icon: { type: String, default: '' },
  done: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  meterLabel: { type: String, default: '' },
  highlight: { type: Boolean, default: false },
})

const ratio = computed(() => (props.total ? props.done / props.total : 0))
</script>

<template>
  <div class="neon-card" :class="{ 'is-highlight': highlight }" :style="{ '--accent': color }">
    <div class="card-head">
      <div>
        <p class="card-title">{{ title }}</p>
        <p class="muted">{{ subtitle }}</p>
      </div>
      <ProgressRing :value="ratio" :color="color" :icon="icon" :size="68" />
    </div>
    <div v-if="meterLabel" class="meter">
      <div class="meter-label">
        <span>{{ meterLabel }}</span>
        <span>{{ done }}/{{ total }}</span>
      </div>
      <div class="meter-track">
        <div class="meter-fill" :style="{ width: `${Math.round(ratio * 100)}%` }"></div>
      </div>
    </div>
    <slot />
  </div>
</template>
