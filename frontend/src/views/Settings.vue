<template>
  <div class="settings-page">
    <a-row :gutter="24">
      <!-- 左侧菜单 -->
      <a-col :span="6">
        <a-card>
          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="inline"
            @click="handleMenuClick"
          >
            <a-menu-item key="profile">
              <UserOutlined />
              <span>个人资料</span>
            </a-menu-item>
            <a-menu-item key="api">
              <KeyOutlined />
              <span>API 配置</span>
            </a-menu-item>
            <a-menu-item key="preferences">
              <SettingOutlined />
              <span>偏好设置</span>
            </a-menu-item>
            <a-menu-item key="password">
              <LockOutlined />
              <span>修改密码</span>
            </a-menu-item>
            <a-menu-item key="about">
              <InfoCircleOutlined />
              <span>关于</span>
            </a-menu-item>
          </a-menu>
        </a-card>
      </a-col>

      <!-- 右侧内容 -->
      <a-col :span="18">
        <!-- 个人资料 -->
        <a-card v-if="selectedKeys[0] === 'profile'" title="个人资料" :loading="profileLoading">
          <a-form :model="profileForm" layout="vertical">
            <a-form-item label="用户名" required>
              <a-input v-model:value="profileForm.name" placeholder="请输入用户名" />
            </a-form-item>

            <a-form-item label="邮箱">
              <a-input v-model:value="profileForm.email" placeholder="请输入邮箱" disabled />
            </a-form-item>

            <a-form-item>
              <a-button type="primary" @click="saveProfile" :loading="saving">
                保存修改
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- API 配置 -->
        <a-card v-if="selectedKeys[0] === 'api'" title="API 配置" :loading="settingsLoading">
          <a-alert
            message="API 密钥安全提示"
            description="请妥善保管您的 API 密钥，不要在公共场合泄露。"
            type="warning"
            show-icon
            style="margin-bottom: 24px"
          />

          <a-form :model="apiForm" layout="vertical">
            <a-form-item label="火山引擎 API Key">
              <a-input-password
                v-model:value="apiForm.doubaoApiKey"
                placeholder="请输入火山引擎 API Key"
              />
              <div class="form-hint">
                用于调用 Seedream 图片生成和 Seedance 视频生成服务
                <a href="https://console.volcengine.com/ark" target="_blank">获取 API Key</a>
              </div>
            </a-form-item>

            <a-form-item label="存储方式">
              <a-radio-group v-model:value="apiForm.storageType">
                <a-radio-button value="local">本地存储</a-radio-button>
                <a-radio-button value="oss" disabled>阿里云 OSS（暂未支持）</a-radio-button>
              </a-radio-group>
            </a-form-item>

            <a-form-item>
              <a-button type="primary" @click="saveApiConfig" :loading="saving">
                保存配置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 偏好设置 -->
        <a-card v-if="selectedKeys[0] === 'preferences'" title="偏好设置">
          <a-form :model="preferenceForm" layout="vertical">
            <a-form-item label="主题">
              <a-radio-group v-model:value="preferenceForm.theme">
                <a-radio-button value="light">
                  <SunOutlined /> 浅色
                </a-radio-button>
                <a-radio-button value="dark">
                  <MoonOutlined /> 深色
                </a-radio-button>
                <a-radio-button value="auto">
                  <DesktopOutlined /> 跟随系统
                </a-radio-button>
              </a-radio-group>
            </a-form-item>

            <a-form-item label="语言">
              <a-select v-model:value="preferenceForm.language">
                <a-select-option value="zh-CN">简体中文</a-select-option>
                <a-select-option value="en-US">English</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="默认视频比例">
              <a-radio-group v-model:value="preferenceForm.defaultRatio" button-style="solid">
                <a-radio-button value="9:16">9:16 (竖屏)</a-radio-button>
                <a-radio-button value="16:9">16:9 (横屏)</a-radio-button>
                <a-radio-button value="1:1">1:1 (方形)</a-radio-button>
              </a-radio-group>
            </a-form-item>

            <a-form-item label="默认视频时长">
              <a-slider v-model:value="preferenceForm.defaultDuration" :min="3" :max="10" />
              <span class="slider-value">{{ preferenceForm.defaultDuration }} 秒</span>
            </a-form-item>

            <a-form-item>
              <a-checkbox v-model:checked="preferenceForm.autoDownload">
                生成完成后自动下载
              </a-checkbox>
            </a-form-item>

            <a-form-item>
              <a-button type="primary" @click="savePreferences" :loading="saving">
                保存偏好
              </a-button>
              <a-button style="margin-left: 12px" @click="resetPreferences">
                恢复默认
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 修改密码 -->
        <a-card v-if="selectedKeys[0] === 'password'" title="修改密码">
          <a-form :model="passwordForm" layout="vertical" style="max-width: 400px;">
            <a-form-item label="当前密码" required>
              <a-input-password v-model:value="passwordForm.oldPassword" placeholder="请输入当前密码" />
            </a-form-item>

            <a-form-item label="新密码" required>
              <a-input-password v-model:value="passwordForm.newPassword" placeholder="请输入新密码" />
            </a-form-item>

            <a-form-item label="确认新密码" required>
              <a-input-password v-model:value="passwordForm.confirmPassword" placeholder="请再次输入新密码" />
            </a-form-item>

            <a-form-item>
              <a-button type="primary" @click="handleChangePassword" :loading="saving">
                修改密码
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 关于 -->
        <a-card v-if="selectedKeys[0] === 'about'" title="关于 CB_VideoCraft">
          <div class="about-content">
            <div class="logo-section">
              <img src="@/assets/logo.svg" alt="CB_VideoCraft" class="logo" />
              <h2>CB_VideoCraft</h2>
              <p class="version">版本 {{ version }}</p>
            </div>

            <a-divider />

            <div class="info-section">
              <p><strong>CB_VideoCraft</strong> 是一款专为电商内容创作者打造的 AI 视频生成工具。</p>
              <p>基于火山引擎 Seedream 和 Seedance 模型，帮助您快速生成高质量的商品图片和宣传视频。</p>
            </div>

            <a-divider />

            <div class="links-section">
              <a-row :gutter="16">
                <a-col :span="8">
                  <a-button block @click="openLink('https://github.com/shiyueliuchuanmei/video-craft')">
                    <GithubOutlined /> GitHub
                  </a-button>
                </a-col>
                <a-col :span="8">
                  <a-button block @click="openLink('https://www.volcengine.com/docs/82379')">
                    <BookOutlined /> 文档
                  </a-button>
                </a-col>
              </a-row>
            </div>

            <a-divider />

            <div class="copyright">
              <p>&copy; 2026 CB_VideoCraft. All rights reserved.</p>
              <p>广州十月六传媒有限公司</p>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  KeyOutlined,
  SettingOutlined,
  LockOutlined,
  InfoCircleOutlined,
  GithubOutlined,
  BookOutlined,
  SunOutlined,
  MoonOutlined,
  DesktopOutlined,
} from '@ant-design/icons-vue'
import {
  getUserInfo,
  updateUserInfo,
  changePassword,
  getUserSettings,
  updateUserSettings,
} from '@/api/user'

// 当前选中的菜单
const selectedKeys = ref(['profile'])

// 加载状态
const saving = ref(false)
const profileLoading = ref(false)
const settingsLoading = ref(false)

// 版本号
const version = ref('1.0.0')

// 个人资料表单
const profileForm = reactive({
  name: '',
  email: '',
})

// API 配置表单
const apiForm = reactive({
  doubaoApiKey: '',
  storageType: 'local',
})

// 偏好设置表单
const preferenceForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  defaultRatio: '9:16',
  defaultDuration: 5,
  autoDownload: false,
})

// 修改密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// 菜单点击
const handleMenuClick = ({ key }) => {
  selectedKeys.value = [key]
}

// 加载用户资料
const loadProfile = async () => {
  profileLoading.value = true
  try {
    const data = await getUserInfo()
    profileForm.name = data.name || ''
    profileForm.email = data.email || ''
  } catch (error) {
    // 静默失败
  } finally {
    profileLoading.value = false
  }
}

// 加载设置
const loadSettings = async () => {
  settingsLoading.value = true
  try {
    const data = await getUserSettings()
    apiForm.doubaoApiKey = data.doubao_api_key || ''
    apiForm.storageType = data.storage_type || 'local'
  } catch (error) {
    // 静默失败
  } finally {
    settingsLoading.value = false
  }
}

// 保存个人资料
const saveProfile = async () => {
  if (!profileForm.name.trim()) {
    message.warning('用户名不能为空')
    return
  }
  saving.value = true
  try {
    await updateUserInfo({ name: profileForm.name })
    message.success('个人资料已保存')
  } catch (error) {
    message.error('保存失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 保存 API 配置
const saveApiConfig = async () => {
  saving.value = true
  try {
    await updateUserSettings({
      doubao_api_key: apiForm.doubaoApiKey,
      storage_type: apiForm.storageType,
    })
    message.success('API 配置已保存')
  } catch (error) {
    message.error('保存失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    message.warning('请填写完整密码信息')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    message.error('两次输入的新密码不一致')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    message.error('新密码至少6位')
    return
  }
  saving.value = true
  try {
    await changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
    })
    message.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error) {
    message.error('密码修改失败：' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 保存偏好设置
const savePreferences = async () => {
  saving.value = true
  try {
    localStorage.setItem('preferences', JSON.stringify(preferenceForm))
    message.success('偏好设置已保存')
  } finally {
    saving.value = false
  }
}

// 恢复默认偏好
const resetPreferences = () => {
  preferenceForm.theme = 'light'
  preferenceForm.language = 'zh-CN'
  preferenceForm.defaultRatio = '9:16'
  preferenceForm.defaultDuration = 5
  preferenceForm.autoDownload = false
  message.success('已恢复默认设置')
}

// 打开链接
const openLink = (url) => {
  window.open(url, '_blank')
}

// 加载保存的偏好设置
onMounted(() => {
  loadProfile()
  loadSettings()

  const saved = localStorage.getItem('preferences')
  if (saved) {
    Object.assign(preferenceForm, JSON.parse(saved))
  }
})
</script>

<style scoped lang="less">
.settings-page {
  .form-hint {
    margin-top: 4px;
    font-size: 12px;
    color: #999;

    a {
      margin-left: 8px;
    }
  }

  .slider-value {
    margin-left: 8px;
    color: #666;
  }

  .about-content {
    text-align: center;

    .logo-section {
      padding: 24px 0;

      .logo {
        width: 80px;
        height: 80px;
        margin-bottom: 16px;
      }

      h2 {
        margin-bottom: 8px;
      }

      .version {
        color: #999;
      }
    }

    .info-section {
      padding: 16px 0;

      p {
        margin-bottom: 8px;
        color: #666;
      }
    }

    .links-section {
      padding: 16px 0;
    }

    .copyright {
      padding: 16px 0;
      color: #999;
      font-size: 12px;

      p {
        margin-bottom: 8px;
      }
    }
  }
}
</style>
