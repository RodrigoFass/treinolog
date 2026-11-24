<script setup>
// Icones simples em SVG (traco), para nao depender de biblioteca externa
defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 22 },
})

const paths = {
  dumbbell: 'M6.5 6v12M17.5 6v12M3.5 9v6M20.5 9v6M6.5 12h11',
  utensils: 'M7 3v7a2 2 0 0 0 4 0V3M9 3v18M17 3c-2 1.5-3 4-3 7h3v11',
  flame:
    'M12 3c1 4 6 6 6 11a6 6 0 0 1-12 0c0-3 2-5 3-6 0 2 1 3 2 3 0-3-1-5 1-8z',
  scale: 'M5 4h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zM8 11a4 4 0 0 1 8 0M12 11l2.2-2.2',
  trophy: 'M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v4M8 20h8',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  sun: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
  moon: 'M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z',
  users: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21a7 7 0 0 1 14 0M17 3a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6.3',
  chart: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  plus: 'M12 5v14M5 12h14',
}
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="paths[name]" />
  </svg>
</template>
