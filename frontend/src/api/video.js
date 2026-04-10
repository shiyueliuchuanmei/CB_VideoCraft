import request from './request'

/**
 * 视频生成相关 API
 */

// 创建视频生成任务
export const createVideoTask = (data) => {
  return request.post('/videos/generations', data)
}

// 查询视频生成任务
export const getVideoTask = (taskId) => {
  return request.get(`/videos/generations/${taskId}`)
}

// 获取视频生成任务列表
export const getVideoTaskList = (params = {}) => {
  return request.get('/videos/generations', { params })
}

// 取消视频生成任务
export const cancelVideoTask = (taskId) => {
  return request.post(`/videos/generations/${taskId}/cancel`)
}

// 删除视频生成任务
export const deleteVideoTask = (taskId) => {
  return request.delete(`/videos/generations/${taskId}`)
}

// 获取可用的视频模型列表
export const getVideoModels = () => {
  return request.get('/videos/models')
}
