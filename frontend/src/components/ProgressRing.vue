<script setup>
import { computed } from 'vue'

import AppIcon from './AppIcon.vue'

// Anel de progresso (0 a 1) com um icone no meio
const props = defineProps({
  value: { type: Number, default: 0 },
  color: { type: String, default: 'var(--foco)' },
  icon: { type: String, default: '' },
  size: { type: Number, default: 76 },
})

const radius = 30
const circumference = 2 * Math.PI * radius
const offset = computed(() => circumference * (1 - Math.min(Math.max(props.value, 0), 1)))
</script>

<template>
  <div class="ring" :style="{ width: `${size}px`, height: `${size}px`, color }">
    <svg viewBox="0 0 76 76" :width="size" :height="size">
      <circle cx="38" cy="38" :r="radius" class="ring-track" />
      <circle
        cx="38"
        cy="38"
        :r="radius"
        class="ring-value"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
      />
    </svg>
    <span class="ring-icon"><AppIcon v-if="icon" :name="icon" :size="size * 0.3" /></span>
  </div>
</template>

<style scoped>
.ring {
  position: relative;
  flex-shrink: 0;
}

.ring > svg {
  transform: rotate(-90deg);
}

.ring-track {
  fill: none;
  stroke: color-mix(in srgb, currentColor 15%, transparent);
  stroke-width: 7;
}

.ring-value {
  fill: none;
  stroke: currentColor;
  stroke-width: 7;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
  filter: drop-shadow(var(--glow) color-mix(in srgb, currentColor 55%, transparent));
}

.ring-icon {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}
</style>
