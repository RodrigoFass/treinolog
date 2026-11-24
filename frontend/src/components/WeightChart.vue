<script setup>
import { Chart, registerables } from 'chart.js'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { cssColor } from '../utils/theme'

Chart.register(...registerables)

// RF13 / RF12: grafico de linha (peso) ou de barras (adesao a dieta), com as cores do tema
const props = defineProps({
  type: { type: String, default: 'line' },
  labels: { type: Array, required: true },
  values: { type: Array, required: true },
  color: { type: String, default: '--dieta' },
  unit: { type: String, default: '' },
  max: { type: Number, default: null },
})

const canvas = ref(null)
let chart = null

function draw() {
  if (chart) chart.destroy()
  const accent = cssColor(props.color)
  const muted = cssColor('--muted')
  const grid = cssColor('--border')
  chart = new Chart(canvas.value, {
    type: props.type,
    data: {
      labels: props.labels,
      datasets: [{
        data: props.values,
        borderColor: accent,
        backgroundColor: props.type === 'bar' ? `${accent}cc` : accent,
        borderRadius: 6,
        tension: 0.3,
        pointRadius: 4,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y} ${props.unit}` } },
      },
      scales: {
        x: { ticks: { color: muted }, grid: { color: grid } },
        y: {
          beginAtZero: props.type === 'bar',
          max: props.max ?? undefined,
          ticks: { color: muted },
          grid: { color: grid },
          title: { display: Boolean(props.unit), text: props.unit, color: muted },
        },
      },
    },
  })
}

onMounted(async () => {
  await nextTick()
  draw()
  window.addEventListener('treinolog-theme', draw)
})

watch(() => [props.labels, props.values], draw)

onBeforeUnmount(() => {
  window.removeEventListener('treinolog-theme', draw)
  chart?.destroy()
})
</script>

<template>
  <canvas ref="canvas"></canvas>
</template>
