import { defineStore } from 'pinia'

import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isLogged: (state) => Boolean(state.token),
    isPersonal: (state) => state.user?.role === 'personal',
    isAluno: (state) => state.user?.role === 'aluno',
  },

  actions: {
    async login(email, password) {
      const { data } = await http.post('/auth/login', { email, password })
      this.token = data.access_token
      localStorage.setItem('token', data.access_token)
      this.setUser(data.user)
    },

    async register(form) {
      await http.post('/auth/register', form)
      await this.login(form.email, form.password)
    },

    async fetchMe() {
      const { data } = await http.get('/auth/me')
      this.setUser(data)
    },

    setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
