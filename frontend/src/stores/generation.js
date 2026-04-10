import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGenerationStore = defineStore('generation', () => {
  // State
  const currentTask = ref(null)
  const taskList = ref([])
  const loading = ref(false)
  
  // Getters
  const pendingTasks = computed(() => 
    taskList.value.filter(t => t.status === 'pending' || t.status === 'processing')
  )
  
  const completedTasks = computed(() => 
    taskList.value.filter(t => t.status === 'completed')
  )
  
  // Actions
  const setCurrentTask = (task) => {
    currentTask.value = task
  }
  
  const addTask = (task) => {
    taskList.value.unshift(task)
  }
  
  const updateTask = (taskId, updates) => {
    const index = taskList.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      taskList.value[index] = { ...taskList.value[index], ...updates }
    }
  }
  
  const setTaskList = (list) => {
    taskList.value = list
  }
  
  const setLoading = (value) => {
    loading.value = value
  }
  
  return {
    currentTask,
    taskList,
    loading,
    pendingTasks,
    completedTasks,
    setCurrentTask,
    addTask,
    updateTask,
    setTaskList,
    setLoading,
  }
})
