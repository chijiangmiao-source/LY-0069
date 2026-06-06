import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'
import type { User } from '../types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<User | null>(null)

  const login = async (username: string, password: string) => {
    const data = await request.post('/auth/login', { username, password })
    token.value = data.access || data.token || ''
    localStorage.setItem('token', token.value)
    await fetchUserInfo()
    return data
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  const fetchUserInfo = async () => {
    const data = await request.get('/auth/me')
    userInfo.value = data
    return data
  }

  return {
    token,
    userInfo,
    login,
    logout,
    fetchUserInfo
  }
})
