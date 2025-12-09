import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  // Agora guardamos o objeto user completo que vem do login
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)

  const isAuthenticated = computed(() => !!token.value)

  // COMPUTED POWER: Aqui definimos quem é o chefe
  const isLibrarian = computed(() => {
    return user.value?.role === 'LIBRARIAN' || user.value?.is_superuser === true
  })

  const login = async (username, password) => {
    try {
      const res = await api.post('login/', { username, password })

      // 1. Salva o Token
      token.value = res.data.access
      localStorage.setItem('token', token.value)

      // 2. Salva o Usuário e a Role (que agora vêm no login!)
      user.value = res.data.user
      localStorage.setItem('user', JSON.stringify(user.value))

      return true
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/'
  }

  const updateUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  return { token, user, isAuthenticated, isLibrarian, login, logout, updateUser }
})