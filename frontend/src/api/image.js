import request from './request'

/**
 * 图片生成相关 API
 */

// 创建图片生成任务
export const createImageTask = (data) => {
  return request.post('/images/generations', data)
}

// 查询图片生成任务
export const getImageTask = (taskId) => {
  return request.get(`/images/generations/${taskId}`)
}

// 获取图片生成任务列表
export const getImageTaskList = (params = {}) => {
  return request.get('/images/generations', { params })
}

// 取消图片生成任务
export const cancelImageTask = (taskId) => {
  return request.post(`/images/generations/${taskId}/cancel`)
}

// 删除图片生成任务
export const deleteImageTask = (taskId) => {
  return request.delete(`/images/generations/${taskId}`)
}

// 获取可用的图片模型列表
export const getImageModels = () => {
  return request.get('/images/models')
}

// 采用图片
export const adoptImage = (taskId, url) => {
  return request.post(`/images/adopt?task_id=${taskId}&url=${encodeURIComponent(url)}`)
}

// 取消采用图片
export const unadoptImage = (taskId, url) => {
  return request.delete(`/images/adopt?task_id=${taskId}&url=${encodeURIComponent(url)}`)
}

// 获取已采用的图片列表
export const getAdoptedImages = () => {
  return request.get('/images/adopted')
}
