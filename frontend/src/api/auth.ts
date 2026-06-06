import request from '@/utils/request'

export interface LoginData {
  username: string
  password: string
}

export function login(data: LoginData) {
  return request.post('/auth/login', data)
}

export function getUserInfo() {
  return request.get('/auth/me')
}
