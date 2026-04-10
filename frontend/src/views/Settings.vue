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
            <a-menu-item key="storage">
              <CloudOutlined />
              <span>存储设置</span>
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
        <a-card v-if="selectedKeys[0] === 'profile'" title="个人资料">
          <a-form :model="profileForm" layout="vertical">
            <a-form-item label="头像">
              <a-upload
                v-model:fileList="avatarList"
                list-type="picture-card"
                :before-upload="beforeAvatarUpload"
                :custom-request="uploadAvatar"
              >
                <div v-if="avatarList.length < 1">
                  <PlusOutlined />
                  <div style="margin-top: 8px">上传头像</div>
                </div>
              </a-upload>
            </a-form-item>
            
            <a-form-item label="用户名" required>
              <a-input v-model:value="profileForm.username" placeholder="请输入用户名" />
            </a-form-item>
            
            <a-form-item label="昵称">
              <a-input v-model:value="profileForm.nickname" placeholder="请输入昵称" />
            </a-form-item>
            
            <a-form-item label="邮箱" required>
              <a-input v-model:value="profileForm.email" placeholder="请输入邮箱" />
            </a-form-item>
            
            <a-form-item label="手机号">
              <a-input v-model:value="profileForm.phone" placeholder="请输入手机号" />
            </a-form-item>
            
            <a-form-item label="个人简介">
              <a-textarea
                v-model:value="profileForm.bio"
                :rows="4"
                placeholder="介绍一下你自己..."
                show-count
                :maxlength="200"
              />
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" @click="saveProfile" :loading="saving">
                保存修改
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- API 配置 -->
        <a-card v-if="selectedKeys[0] === 'api'" title="API 配置">
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
            
            <a-form-item label="默认图片模型">
              <a-select v-model:value="apiForm.defaultImageModel">
                <a-select-option value="doubao-seedream-4-0-250828">Seedream 4.0</a-select-option>
                <a-select-option value="doubao-seedream-4-5-251128">Seedream 4.5</a-select-option>
                <a-select-option value="doubao-seedream-5-0-260128">Seedream 5.0</a-select-option>
              </a-select>
            </a-form-item>
            
            <a-form-item label="默认视频模型">
              <a-select v-model:value="apiForm.defaultVideoModel">
                <a-select-option value="doubao-seedance-2-0-260128">Seedance 2.0</a-select-option>
                <a-select-option value="doubao-seedance-2-0-fast-260128">Seedance 2.0 Fast</a-select-option>
              </a-select>
            </a-form-item>
            
            <a-form-item label="API 请求超时（秒）">
              <a-slider v-model:value="apiForm.timeout" :min="30" :max="300" :step="10" />
              <span class="slider-value">{{ apiForm.timeout }} 秒</span>
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" @click="testApiConnection" :loading="testing">
                测试连接
              </a-button>
              <a-button style="margin-left: 12px" @click="saveApiConfig" :loading="saving">
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
              <a-checkbox v-model:checked="preferenceForm.soundEffect">
                开启音效提示
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

        <!-- 存储设置 -->
        <a-card v-if="selectedKeys[0] === 'storage'" title="存储设置">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="本地存储使用">
              <a-progress :percent="storagePercent" :status="storageStatus" />
              <span>{{ formatSize(storageUsed) }} / {{ formatSize(storageTotal) }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="图片文件">
              {{ storageStats.imageCount }} 个 ({{ formatSize(storageStats.imageSize) }})
            </a-descriptions-item>
            <a-descriptions-item label="视频文件">
              {{ storageStats.videoCount }} 个 ({{ formatSize(storageStats.videoSize) }})
            </a-descriptions-item>
          </a-descriptions>
          
          <div class="storage-actions">
            <a-button danger @click="clearCache">
              <DeleteOutlined /> 清理缓存
            </a-button>
            <a-button style="margin-left: 12px" @click="exportData">
              <ExportOutlined /> 导出数据
            </a-button>
          </div>
        </a-card>

        <!-- 关于 -->
        <a-card v-if="selectedKeys[0] === 'about'" title="关于 VideoCraft">
          <div class="about-content">
            <div class="logo-section">
              <img src="@/assets/logo.svg" alt="VideoCraft" class="logo" />
              <h2>VideoCraft</h2>
              <p class="version">版本 {{ version }}</p>
            </div>
            
            <a-divider />
            
            <div class="info-section">
              <p><strong>VideoCraft</strong> 是一款专为电商内容创作者打造的 AI 视频生成工具。</p>
              <p>基于火山引擎 Seedream 和 Seedance 模型，帮助您快速生成高质量的商品图片和宣传视频。</p>
            </div>
            
            <a-divider />
            
            <div class="links-section">
              <a-row :gutter="16">
                <a-col :span="8">
                  <a-button block @click="openLink('https://github.com/videocraft')">
                    <GithubOutlined /> GitHub
                  </a-button>
                </a-col>
                <a-col :span="8">
                  <a-button block @click="openLink('https://videocraft.cc/docs')">
                    <BookOutlined /> 文档
                  </a-button>
                </a-col>
                <a-col :span="8">
                  <a-button block @click="openLink('https://videocraft.cc/support')">
                    <CustomerServiceOutlined /> 支持
                  </a-button>
                </a-col>
              </a-row>
            </div>
            
            <a-divider />
            
            <div class="copyright">
              <p>© 2026 VideoCraft. All rights reserved.</p>
              <p>
                <a @click="openLink('https://videocraft.cc/privacy')">隐私政策</a>
                <a-divider type="vertical" />
                <a @click="openLink('https://videocraft.cc/terms')">服务条款</a>
              </p>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  KeyOutlined,
  SettingOutlined,
  CloudOutlined,
  InfoCircleOutlined,
  PlusOutlined,
  DeleteOutlined,
  ExportOutlined,
  GithubOutlined,
  BookOutlined,
  CustomerServiceOutlined,
  SunOutlined,
  MoonOutlined,
  DesktopOutlined,
} from '@ant-design/icons-vue'

// 当前选中的菜单
const selectedKeys = ref(['profile'])

// 加载状态
const saving = ref(false)
const testing = ref(false)

// 头像列表
const avatarList = ref([])

// 版本号
const version = ref('1.0.0')

// 个人资料表单
const profileForm = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  bio: '',
})

// API 配置表单
const apiForm = reactive({
  doubaoApiKey: '',
  defaultImageModel: 'doubao-seedream-4-0-250828',
  defaultVideoModel: 'doubao-seedance-2-0-260128',
  timeout: 120,
})

// 偏好设置表单
const preferenceForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  defaultRatio: '9:16',
  defaultDuration: 5,
  autoDownload: false,
  soundEffect: true,
})

// 存储统计
const storageUsed = ref(1024 * 1024 * 500) // 500MB
const storageTotal = ref(1024 * 1024 * 1024 * 5) // 5GB
const storageStats = reactive({
  imageCount: 128,
  imageSize: 1024 * 1024 * 200,
  videoCount: 45,
  videoSize: 1024 * 1024 * 300,
})

// 计算存储百分比
const storagePercent = computed(() => {
  return Math.round((storageUsed.value / storageTotal.value) * 100)
})

// 存储状态
const storageStatus = computed(() => {
  if (storagePercent.value > 90) return 'exception'
  if (storagePercent.value > 70) return 'warning'
  return 'normal'
})

// 菜单点击
const handleMenuClick = ({ key }) => {
  selectedKeys.value = [key]
}

// 头像上传前检查
const beforeAvatarUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    message.error('只支持 JPG/PNG 格式的图片!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// 上传头像
const uploadAvatar = ({ file, onSuccess }) => {
  setTimeout(() => {
    onSuccess({ url: URL.createObjectURL(file) })
    message.success('头像上传成功')
  }, 1000)
}

// 保存个人资料
const saveProfile = async () => {
  saving.value = true
  try {
    // 模拟保存
    await new Promise(resolve => setTimeout(resolve, 1000))
    message.success('个人资料已保存')
  } finally {
    saving.value = false
  }
}

// 测试 API 连接
const testApiConnection = async () => {
  testing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    message.success('API 连接测试成功')
  } catch (error) {
    message.error('API 连接测试失败')
  } finally {
    testing.value = false
  }
}

// 保存 API 配置
const saveApiConfig = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    message.success('API 配置已保存')
  } finally {
    saving.value = false
  }
}

// 保存偏好设置
const savePreferences = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
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
  preferenceForm.soundEffect = true
  message.success('已恢复默认设置')
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 清理缓存
const clearCache = () => {
  message.success('缓存已清理')
}

// 导出数据
const exportData = () => {
  message.success('数据导出成功')
}

// 打开链接
const openLink = (url) => {
  window.open(url, '_blank')
}

// 加载保存的偏好设置
onMounted(() => {
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
  
  .storage-actions {
    margin-top: 24px;
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
