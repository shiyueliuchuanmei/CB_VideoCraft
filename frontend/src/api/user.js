import request from './request'

/**
 * 用户相关 API
 */

// 用户登录
export const login = (data) => {
  return request.post('/auth/login', data)
}

// 用户注册
export const register = (data) => {
  return request.post('/auth/register', data)
}

// 获取用户信息
export const getUserInfo = () => {
  return request.get('/users/me')
}

// 更新用户信息
export const updateUserInfo = (data) => {
  return request.put('/users/me', data)
}

// 修改密码
export const changePassword = (data) => {
  return request.post('/users/me/password', data)
}

// 获取用户设置
export const getUserSettings = () => {
  return request.get('/users/me/settings')
}

// 更新用户设置
export const updateUserSettings = (data) => {
  return request.put('/users/me/settings', data)
}
