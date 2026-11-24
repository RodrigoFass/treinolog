import { ref } from 'vue'

// Tema claro/escuro. A escolha fica salva no navegador;
// sem escolha salva, segue o tema do sistema.
const KEY = 'treinolog-theme'

function savedTheme() {
  try {
    return localStorage.getItem(KEY)
  } catch {
    return null
  }
}

function systemTheme() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const theme = ref(savedTheme() || systemTheme())

export function applyTheme() {
  document.documentElement.setAttribute('data-theme', theme.value)
}

export function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  try {
    localStorage.setItem(KEY, theme.value)
  } catch {
    // navegador sem localStorage: o tema vale so ate fechar a pagina
  }
  applyTheme()
  window.dispatchEvent(new Event('treinolog-theme'))
}

// Le uma cor da paleta (para o Chart.js, que nao entende variavel CSS)
export function cssColor(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
