<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <p>页面不存在</p>
      <a-button type="primary" @click="goHome">返回首页</a-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped lang="less">
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;

  .content {
    text-align: center;

    h1 {
      font-size: 120px;
      font-weight: 700;
      color: #1890ff;
      margin-bottom: 16px;
    }

    p {
      font-size: 24px;
      color: #666;
      margin-bottom: 32px;
    }
  }
}
</style>
