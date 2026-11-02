import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

// Envia o token JWT em todas as requisicoes
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Token expirado ou invalido: volta para o login
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config.url.includes('/auth/login')) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export function errorMessage(error) {
  return error.response?.data?.erro || 'Nao foi possivel concluir a operacao.'
}

export default http
