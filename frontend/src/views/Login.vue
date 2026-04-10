<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <img src="@/assets/logo.svg" alt="logo" class="logo" />
        <h1>VideoCraft</h1>
        <p>电商视频智能创作平台</p>
      </div>
      
      <a-card class="login-card">
        <a-tabs v-model:activeKey="activeKey" centered>
          <a-tab-pane key="login" tab="登录">
            <a-form
              :model="loginForm"
              :rules="loginRules"
              layout="vertical"
              @finish="handleLogin"
            >
              <a-form-item name="email" label="邮箱">
                <a-input
                  v-model:value="loginForm.email"
                  placeholder="请输入邮箱"
                  size="large"
                >
                  <template #prefix>
                    <MailOutlined />
                  </template>
                </a-input>
              </a-form-item>
              
              <a-form-item name="password" label="密码">
                <a-input-password
                  v-model:value="loginForm.password"
                  placeholder="请输入密码"
                  size="large"
                >
                  <template #prefix>
                    <LockOutlined />
                  </template>
                </a-input-password>
              </a-form-item>
              
              <a-form-item>
                <a-checkbox v-model:checked="loginForm.remember">
                  记住我
                </a-checkbox>
                <a class="forgot-link" @click="showForgot = true">忘记密码?</a>
              </a-form-item>
              
              <a-form-item>
                <a-button
                  type="primary"
                  size="large"
                  block
                  html-type="submit"
                  :loading="loading"
                >
                  登录
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
          
          <a-tab-pane key="register" tab="注册">
            <a-form
              :model="registerForm"
              :rules="registerRules"
              layout="vertical"
              @finish="handleRegister"
            >
              <a-form-item name="name" label="用户名">
                <a-input
                  v-model:value="registerForm.name"
                  placeholder="请输入用户名"
                  size="large"
                >
                  <template #prefix>
                    <UserOutlined />
                  </template>
                </a-input>
              </a-form-item>
              
              <a-form-item name="email" label="邮箱">
                <a-input
                  v-model:value="registerForm.email"
                  placeholder="请输入邮箱"
                  size="large"
                >
                  <template #prefix>
                    <MailOutlined />
                  </template>
                </a-input>
              </a-form-item>
              
              <a-form-item name="password" label="密码">
                <a-input-password
                  v-model:value="registerForm.password"
                  placeholder="请输入密码"
                  size="large"
                >
                  <template #prefix>
                    <LockOutlined />
                  </template>
                </a-input-password>
              </a-form-item>
              
              <a-form-item name="confirmPassword" label="确认密码">
                <a-input-password
                  v-model:value="registerForm.confirmPassword"
                  placeholder="请再次输入密码"
                  size="large"
                >
                  <template #prefix>
                    <LockOutlined />
                  </template>
                </a-input-password>
              </a-form-item>
              
              <a-form-item>
                <a-button
                  type="primary"
                  size="large"
                  block
                  html-type="submit"
                  :loading="loading"
                >
                  注册
                </a-button>
              </a-form-item>
            </a-form>
          </a-tab-pane>
        </a-tabs>
      </a-card>
      
      <div class="login-footer">
        <p>© 2026 VideoCraft. All rights reserved.</p>
      </div>
    </div>
    
    <!-- 忘记密码弹窗 -->
    <a-modal
      v-model:open="showForgot"
      title="找回密码"
      @ok="handleForgot"
    >
      <a-form layout="vertical">
        <a-form-item label="邮箱">
          <a-input v-model:value="forgotEmail" placeholder="请输入注册邮箱" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  MailOutlined,
  LockOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { login, register } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 当前标签页
const activeKey = ref('login')

// 加载状态
const loading = ref(false)

// 忘记密码
const showForgot = ref(false)
const forgotEmail = ref('')

// 登录表单
const loginForm = reactive({
  email: '',
  password: '',
  remember: false,
})

// 注册表单
const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// 登录表单验证规则
const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

// 注册表单验证规则
const registerRules = {
  name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度2-20位', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        if (value !== registerForm.password) {
          return Promise.reject('两次输入的密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur',
    },
  ],
}

// 登录
const handleLogin = async () => {
  loading.value = true
  try {
    const res = await login({
      email: loginForm.email,
      password: loginForm.password,
    })
    
    userStore.setToken(res.token)
    userStore.setUserInfo(res.user)
    
    message.success('登录成功')
    router.push('/')
  } catch (error) {
    message.error('登录失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 注册
const handleRegister = async () => {
  loading.value = true
  try {
    await register({
      name: registerForm.name,
      email: registerForm.email,
      password: registerForm.password,
    })
    
    message.success('注册成功，请登录')
    activeKey.value = 'login'
  } catch (error) {
    message.error('注册失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 找回密码
const handleForgot = () => {
  if (!forgotEmail.value) {
    message.warning('请输入邮箱')
    return
  }
  message.success('重置密码邮件已发送')
  showForgot.value = false
}
</script>

<style scoped lang="less">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;

  .login-container {
    width: 100%;
    max-width: 420px;

    .login-header {
      text-align: center;
      margin-bottom: 24px;
      color: #fff;

      .logo {
        width: 80px;
        height: 80px;
        margin-bottom: 16px;
      }

      h1 {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 8px;
      }

      p {
        font-size: 16px;
        opacity: 0.9;
      }
    }

    .login-card {
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);

      .forgot-link {
        float: right;
        color: #1890ff;
      }
    }

    .login-footer {
      text-align: center;
      margin-top: 24px;
      color: rgba(255, 255, 255, 0.8);
      font-size: 14px;
    }
  }
}
</style>
