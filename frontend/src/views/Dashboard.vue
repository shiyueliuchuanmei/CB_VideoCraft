<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1>欢迎使用 VideoCraft</h1>
      <p>一站式 AI 驱动的电商视频内容创作平台</p>
    </div>

    <!-- 快捷操作 -->
    <a-row :gutter="24" class="quick-actions">
      <a-col :span="12">
        <a-card class="action-card image-card" @click="goToImage">
          <div class="action-content">
            <PictureOutlined class="action-icon" />
            <div class="action-info">
              <h3>图片生成</h3>
              <p>使用豆包 Seedream 生成商品图片</p>
              <a-button type="primary" size="small">立即生成</a-button>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card class="action-card video-card" @click="goToVideo">
          <div class="action-content">
            <VideoCameraOutlined class="action-icon" />
            <div class="action-info">
              <h3>视频生成</h3>
              <p>使用豆包 Seedance 生成商品视频</p>
              <a-button type="primary" size="small" danger>立即生成</a-button>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 统计卡片 -->
    <a-row :gutter="24" class="statistics">
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic
            title="今日生成图片"
            :value="stats.todayImages"
            suffix="张"
            :value-style="{ color: '#1890ff' }"
          >
            <template #prefix>
              <PictureOutlined />
            </template>
          </a-statistic>
          <div class="stat-trend" :class="{ 'up': stats.imageTrend > 0 }">
            <ArrowUpOutlined v-if="stats.imageTrend > 0" />
            <ArrowDownOutlined v-else />
            {{ Math.abs(stats.imageTrend) }}% 较昨日
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic
            title="今日生成视频"
            :value="stats.todayVideos"
            suffix="个"
            :value-style="{ color: '#52c41a' }"
          >
            <template #prefix>
              <VideoCameraOutlined />
            </template>
          </a-statistic>
          <div class="stat-trend" :class="{ 'up': stats.videoTrend > 0 }">
            <ArrowUpOutlined v-if="stats.videoTrend > 0" />
            <ArrowDownOutlined v-else />
            {{ Math.abs(stats.videoTrend) }}% 较昨日
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic
            title="累计生成"
            :value="stats.totalTasks"
            suffix="次"
            :value-style="{ color: '#722ed1' }"
          >
            <template #prefix>
              <BarChartOutlined />
            </template>
          </a-statistic>
          <div class="stat-trend">
            成功率 {{ stats.successRate }}%
          </div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <a-statistic
            title="节省时长"
            :value="stats.savedTime"
            suffix="小时"
            :value-style="{ color: '#fa8c16' }"
          >
            <template #prefix>
              <ClockCircleOutlined />
            </template>
          </a-statistic>
          <div class="stat-trend">
            效率提升 {{ stats.efficiency }}%
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 最近任务和趋势图表 -->
    <a-row :gutter="24" class="main-content">
      <!-- 最近任务 -->
      <a-col :span="12">
        <a-card title="最近任务" class="recent-tasks">
          <template #extra>
            <a-button type="link" @click="goToHistory">查看全部</a-button>
          </template>
          <a-list :data-source="recentTasks" :loading="loading">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: item.type === 'image' ? '#1890ff' : '#52c41a' }">
                      <PictureOutlined v-if="item.type === 'image'" />
                      <VideoCameraOutlined v-else />
                    </a-avatar>
                  </template>
                  <template #title>
                    <span class="task-title">{{ truncateText(item.prompt, 20) }}</span>
                    <a-tag :color="getStatusColor(item.status)" size="small">
                      {{ getStatusText(item.status) }}
                    </a-tag>
                  </template>
                  <template #description>
                    {{ formatTime(item.createdAt) }}
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="link" size="small" @click="previewTask(item)">
                    <EyeOutlined />
                  </a-button>
                  <a-button type="link" size="small" @click="downloadTask(item)" v-if="item.status === 'completed'">
                    <DownloadOutlined />
                  </a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>

      <!-- 生成趋势 -->
      <a-col :span="12">
        <a-card title="生成趋势" class="trend-chart">
          <template #extra>
            <a-radio-group v-model:value="trendPeriod" size="small" @change="loadTrendData">
              <a-radio-button value="week">本周</a-radio-button>
              <a-radio-button value="month">本月</a-radio-button>
            </a-radio-group>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              <BarChartOutlined style="font-size: 48px; color: #d9d9d9;" />
              <p>图表加载中...</p>
            </div>
          </div>
          <div class="trend-summary">
            <a-row :gutter="16">
              <a-col :span="12">
                <div class="trend-item">
                  <div class="trend-label">图片生成</div>
                  <div class="trend-value">{{ trendData.images }} 张</div>
                </div>
              </a-col>
              <a-col :span="12">
                <div class="trend-item">
                  <div class="trend-label">视频生成</div>
                  <div class="trend-value">{{ trendData.videos }} 个</div>
                </div>
              </a-col>
            </a-row>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 使用提示 -->
    <a-row :gutter="24" class="tips-section">
      <a-col :span="24">
        <a-card title="💡 使用技巧">
          <a-row :gutter="16">
            <a-col :span="8">
              <div class="tip-item">
                <BulbOutlined class="tip-icon" />
                <h4>提示词优化</h4>
                <p>使用详细的描述，包含场景、风格、光线等关键词，可以获得更好的生成效果。</p>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="tip-item">
                <PictureOutlined class="tip-icon" />
                <h4>图生视频</h4>
                <p>上传高质量的首帧图片，配合详细的动作描述，可以生成更流畅的视频。</p>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="tip-item">
                <SoundOutlined class="tip-icon" />
                <h4>多模态输入</h4>
                <p>结合图片、视频、音频等多种输入，可以创造出更丰富的内容。</p>
              </div>
            </a-col>
          </a-row>
        </a-card>
      </a-col>
    </a-row>

    <!-- 预览弹窗 -->
    <a-modal
      v-model:visible="previewVisible"
      title="预览"
      width="600px"
      :footer="null"
    >
      <div class="preview-content">
        <img v-if="previewItem?.type === 'image'" :src="previewItem.url" class="preview-media" />
        <video v-else-if="previewItem?.type === 'video'" :src="previewItem.url" controls class="preview-media" />
        <p class="preview-prompt">{{ previewItem?.prompt }}</p>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import {
  PictureOutlined,
  VideoCameraOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  EyeOutlined,
  DownloadOutlined,
  BulbOutlined,
  SoundOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()

// 统计数据
const stats = reactive({
  todayImages: 12,
  todayVideos: 5,
  imageTrend: 20,
  videoTrend: -5,
  totalTasks: 128,
  successRate: 96,
  savedTime: 48,
  efficiency: 300,
})

// 趋势数据
const trendPeriod = ref('week')
const trendData = reactive({
  images: 45,
  videos: 18,
})

// 最近任务
const recentTasks = ref([])
const loading = ref(false)

// 预览
const previewVisible = ref(false)
const previewItem = ref(null)

// 页面跳转
const goToImage = () => router.push('/image')
const goToVideo = () => router.push('/video')
const goToHistory = () => router.push('/history')

// 加载最近任务
const loadRecentTasks = async () => {
  loading.value = true
  try {
    // 模拟数据
    recentTasks.value = [
      {
        id: 'task-001',
        type: 'video',
        prompt: '一只可爱的猫咪在草地上玩耍',
        status: 'completed',
        createdAt: new Date().toISOString(),
        url: 'https://via.placeholder.com/720x1280',
      },
      {
        id: 'task-002',
        type: 'image',
        prompt: '高端化妆品产品图，白色背景',
        status: 'completed',
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        url: 'https://via.placeholder.com/1024x1024',
      },
      {
        id: 'task-003',
        type: 'video',
        prompt: '果茶宣传广告，清新风格',
        status: 'processing',
        createdAt: new Date(Date.now() - 7200000).toISOString(),
        url: null,
      },
      {
        id: 'task-004',
        type: 'image',
        prompt: '运动鞋产品展示图',
        status: 'completed',
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        url: 'https://via.placeholder.com/1024x1024',
      },
    ]
  } finally {
    loading.value = false
  }
}

// 加载趋势数据
const loadTrendData = () => {
  // 模拟数据
  if (trendPeriod.value === 'week') {
    trendData.images = 45
    trendData.videos = 18
  } else {
    trendData.images = 180
    trendData.videos = 72
  }
}

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    pending: 'default',
    processing: 'processing',
    completed: 'success',
    failed: 'error',
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    pending: '排队中',
    processing: '生成中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

// 格式化时间
const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// 截断文本
const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

// 预览任务
const previewTask = (item) => {
  previewItem.value = item
  previewVisible.value = true
}

// 下载任务
const downloadTask = (item) => {
  if (!item.url) return
  const link = document.createElement('a')
  link.href = item.url
  link.download = `task-${item.id}.${item.type === 'image' ? 'jpg' : 'mp4'}`
  link.click()
  message.success('开始下载')
}

onMounted(() => {
  loadRecentTasks()
  loadTrendData()
})
</script>

<style scoped lang="less">
.dashboard {
  .welcome-section {
    margin-bottom: 24px;
    
    h1 {
      font-size: 28px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    
    p {
      color: #666;
      font-size: 16px;
    }
  }

  .quick-actions {
    margin-bottom: 24px;
    
    .action-card {
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      &.image-card:hover {
        border-color: #1890ff;
      }
      
      &.video-card:hover {
        border-color: #52c41a;
      }
      
      .action-content {
        display: flex;
        align-items: center;
        padding: 16px;
        
        .action-icon {
          font-size: 48px;
          margin-right: 16px;
          color: #1890ff;
        }
        
        .action-info {
          flex: 1;
          
          h3 {
            margin-bottom: 8px;
            font-size: 18px;
          }
          
          p {
            color: #666;
            margin-bottom: 12px;
          }
        }
      }
    }
  }

  .statistics {
    margin-bottom: 24px;
    
    .stat-card {
      .stat-trend {
        margin-top: 8px;
        font-size: 12px;
        color: #999;
        
        &.up {
          color: #52c41a;
        }
        
        &:not(.up) {
          color: #ff4d4f;
        }
      }
    }
  }

  .main-content {
    margin-bottom: 24px;
    
    .recent-tasks {
      .task-title {
        margin-right: 8px;
      }
    }
    
    .trend-chart {
      .chart-container {
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        border-radius: 8px;
        margin-bottom: 16px;
        
        .chart-placeholder {
          text-align: center;
          
          p {
            margin-top: 8px;
            color: #999;
          }
        }
      }
      
      .trend-summary {
        .trend-item {
          text-align: center;
          padding: 12px;
          background: #f5f5f5;
          border-radius: 8px;
          
          .trend-label {
            color: #666;
            font-size: 12px;
            margin-bottom: 4px;
          }
          
          .trend-value {
            font-size: 20px;
            font-weight: 600;
            color: #1890ff;
          }
        }
      }
    }
  }

  .tips-section {
    .tip-item {
      text-align: center;
      padding: 16px;
      
      .tip-icon {
        font-size: 32px;
        color: #1890ff;
        margin-bottom: 12px;
      }
      
      h4 {
        margin-bottom: 8px;
        font-size: 16px;
      }
      
      p {
        color: #666;
        font-size: 14px;
        line-height: 1.6;
      }
    }
  }

  .preview-content {
    text-align: center;
    
    .preview-media {
      max-width: 100%;
      max-height: 400px;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    
    .preview-prompt {
      color: #666;
      padding: 12px;
      background: #f5f5f5;
      border-radius: 8px;
    }
  }
}
</style>
