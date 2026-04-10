import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 加载状态
  const loading = ref(false)
  const loadingText = ref('加载中...')
  
  // 全局消息
  const message = ref({
    type: 'info',
    content: '',
    visible: false,
  })
  
  // 在线状态
  const online = ref(navigator.onLine)
  
  // 侧边栏折叠
  const sidebarCollapsed = ref(false)
  
  // 主题
  const theme = ref(localStorage.getItem('theme') || 'light')
  
  // 计算属性
  const isDark = computed(() => theme.value === 'dark')
  
  // 设置加载状态
  const setLoading = (status, text = '加载中...') => {
    loading.value = status
    loadingText.value = text
  }
  
  // 显示消息
  const showMessage = (type, content, duration = 3000) => {
    message.value = { type, content, visible: true }
    setTimeout(() => {
      message.value.visible = false
    }, duration)
  }
  
  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    document.documentElement.setAttribute('data-theme', theme.value)
  }
  
  // 切换侧边栏
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  // 监听网络状态
  const initNetworkListener = () => {
    window.addEventListener('online', () => {
      online.value = true
      showMessage('success', '网络已恢复')
    })
    window.addEventListener('offline', () => {
      online.value = false
      showMessage('error', '网络已断开')
    })
  }
  
  return {
    loading,
    loadingText,
    message,
    online,
    sidebarCollapsed,
    theme,
    isDark,
    setLoading,
    showMessage,
    toggleTheme,
    toggleSidebar,
    initNetworkListener,
  }
})
