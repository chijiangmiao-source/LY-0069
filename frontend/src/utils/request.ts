import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
      } else if (status === 400 || status === 500) {
        const message = error.response.data?.detail || '请求失败'
        ElMessage.error(message)
      } else {
        ElMessage.error(`请求错误: ${status}`)
      }
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request
