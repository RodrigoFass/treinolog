<script setup>
// Logo do TreinoLog: anel de progresso (treino, alimentacao, ofensiva) com um "T" no meio
defineProps({
  size: { type: Number, default: 30 },
  withName: { type: Boolean, default: true },
})
</script>

<template>
  <span class="logo">
    <svg :width="size" :height="size" viewBox="0 0 40 40" aria-label="TreinoLog">
      <defs>
        <linearGradient id="logo-gradiente" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="var(--treino)" />
          <stop offset="0.5" stop-color="var(--foco)" />
          <stop offset="1" stop-color="var(--dieta)" />
        </linearGradient>
      </defs>
      <circle
        cx="20"
        cy="20"
        r="16"
        fill="none"
        stroke="url(#logo-gradiente)"
        stroke-width="4.5"
        stroke-linecap="round"
        stroke-dasharray="84 101"
        transform="rotate(-210 20 20)"
      />
      <rect x="12.5" y="12" width="15" height="4.5" rx="2.2" fill="var(--text)" />
      <rect x="17.75" y="12" width="4.5" height="16" rx="2.2" fill="var(--text)" />
      <circle cx="31.5" cy="11" r="2.6" fill="var(--ofensiva)" />
    </svg>
    <span v-if="withName" class="brand" :style="{ fontSize: `${Math.max(size * 0.62, 18)}px` }">Treino<b>Log</b></span>
  </span>
</template>

<style scoped>
.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.brand {
  font-weight: 500;
  color: var(--text);
}

.brand b {
  font-weight: 700;
  color: var(--foco);
}
</style>
