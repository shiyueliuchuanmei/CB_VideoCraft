<template>
  <a-layout class="layout">
    <!-- 侧边栏 -->
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sider"
    >
      <div class="logo">
        <img src="@/assets/logo.svg" alt="logo" v-if="!collapsed" />
        <span v-else>VC</span>
      </div>
      
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item v-for="item in menuItems" :key="item.key">
          <template #icon>
            <component :is="item.icon" />
          </template>
          <span>{{ item.title }}</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <!-- 主内容区 -->
    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <menu-unfold-outlined
          v-if="collapsed"
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        <menu-fold-outlined
          v-else
          class="trigger"
          @click="() => (collapsed = !collapsed)"
        />
        
        <div class="header-right">
          <a-dropdown>
            <a class="user-info">
              <a-avatar :size="32" icon="<UserOutlined />" />
              <span class="username">{{ userStore.userInfo?.name || '用户' }}</span>
              <DownOutlined />
            </a>
            <template #overlay>
              <a-menu @click="handleUserMenuClick">
                <a-menu-item key="profile">个人中心</a-menu-item>
                <a-menu-item key="settings">系统设置</a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <!-- 内容区 -->
      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  HomeOutlined,
  PictureOutlined,
  VideoCameraOutlined,
  HistoryOutlined,
  SettingOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  DownOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 菜单配置
const menuItems = [
  { key: 'Dashboard', title: '首页', icon: HomeOutlined },
  { key: 'Image', title: '图片生成', icon: PictureOutlined },
  { key: 'Video', title: '视频生成', icon: VideoCameraOutlined },
  { key: 'History', title: '历史记录', icon: HistoryOutlined },
  { key: 'Settings', title: '设置', icon: SettingOutlined },
]

// 状态
const collapsed = ref(false)
const selectedKeys = ref([route.name])

// 监听路由变化
watch(
  () => route.name,
  (name) => {
    selectedKeys.value = [name]
  }
)

// 菜单点击
const handleMenuClick = ({ key }) => {
  router.push({ name: key })
}

// 用户菜单点击
const handleUserMenuClick = ({ key }) => {
  switch (key) {
    case 'profile':
      router.push('/settings')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      userStore.logout()
      message.success('已退出登录')
      router.push('/login')
      break
  }
}
</script>

<style scoped lang="less">
.layout {
  min-height: 100vh;
}

.sider {
  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 20px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    img {
      height: 40px;
    }
  }
}

.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

  .trigger {
    font-size: 18px;
    cursor: pointer;
    transition: color 0.3s;

    &:hover {
      color: #1890ff;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #262626;

      .username {
        font-size: 14px;
      }
    }
  }
}

.content {
  margin: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 112px);
}
</style>
