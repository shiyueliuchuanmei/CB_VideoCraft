<template>
  <div class="feishu-callback">
    <a-spin size="large" tip="正在登录..." />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'
import { feishuCallback } from '@/api/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  const code = route.query.code
  const state = route.query.state

  if (!code) {
    message.error('授权失败：缺少授权码')
    router.push('/login')
    return
  }

  try {
    const res = await feishuCallback({ code, state })
    userStore.setToken(res.token)
    userStore.setUserInfo(res.user)
    message.success('登录成功')
    router.push('/')
  } catch (error) {
    message.error('飞书登录失败：' + error.message)
    router.push('/login')
  }
})
</script>

<style scoped>
.feishu-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
