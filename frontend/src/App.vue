<template>
  <a-config-provider :theme="themeConfig">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { reactive } from 'vue'

// 主题配置
const themeConfig = reactive({
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    fontSize: 14,
  },
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
