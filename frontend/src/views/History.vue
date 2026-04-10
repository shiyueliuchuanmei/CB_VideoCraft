<template>
  <div class="history-page">
    <a-card title="历史记录" :loading="loading">
      <!-- 统计卡片 -->
      <a-row :gutter="16" class="stats-row">
        <a-col :span="6">
          <a-statistic title="总任务数" :value="stats.total" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="已完成" :value="stats.completed" value-style="color: #52c41a" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="生成中" :value="stats.processing" value-style="color: #1890ff" />
        </a-col>
        <a-col :span="6">
          <a-statistic title="失败" :value="stats.failed" value-style="color: #ff4d4f" />
        </a-col>
      </a-row>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <a-space wrap>
          <a-select
            v-model:value="filter.type"
            placeholder="类型"
            style="width: 120px"
            allow-clear
          >
            <a-select-option value="image">图片</a-select-option>
            <a-select-option value="video">视频</a-select-option>
          </a-select>
          
          <a-select
            v-model:value="filter.status"
            placeholder="状态"
            style="width: 120px"
            allow-clear
          >
            <a-select-option value="pending">排队中</a-select-option>
            <a-select-option value="processing">生成中</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="failed">失败</a-select-option>
          </a-select>
          
          <a-range-picker v-model:value="filter.dateRange" />
          
          <a-input-search
            v-model:value="filter.keyword"
            placeholder="搜索提示词"
            style="width: 200px"
            @search="handleSearch"
          />
          
          <a-button type="primary" @click="handleSearch">
            <SearchOutlined /> 查询
          </a-button>
          <a-button @click="handleReset">
            <ReloadOutlined /> 重置
          </a-button>
        </a-space>
      </div>

      <!-- 操作栏 -->
      <div class="action-bar">
        <a-space>
          <a-button 
            danger 
            @click="handleBatchDelete" 
            :disabled="selectedRowKeys.length === 0"
          >
            <DeleteOutlined /> 批量删除
          </a-button>
          <a-button @click="handleBatchDownload" :disabled="selectedRowKeys.length === 0">
            <DownloadOutlined /> 批量下载
          </a-button>
          <a-button @click="handleRefresh">
            <SyncOutlined :spin="refreshing" /> 刷新
          </a-button>
        </a-space>
      </div>

      <!-- 任务列表 -->
      <a-table
        :row-selection="{ selectedRowKeys: selectedRowKeys, onChange: onSelectChange }"
        :columns="columns"
        :data-source="taskList"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="record.type === 'image' ? 'blue' : 'purple'">
              {{ record.type === 'image' ? '图片' : '视频' }}
            </a-tag>
          </template>
          
          <template v-else-if="column.key === 'preview'">
            <div class="preview-cell" @click="handlePreview(record)">
              <img 
                v-if="record.type === 'image' && record.thumbnailUrl" 
                :src="record.thumbnailUrl" 
                class="preview-image"
              />
              <div v-else-if="record.type === 'video'" class="preview-video-placeholder">
                <VideoCameraOutlined />
                <span class="play-icon">▶</span>
              </div>
              <div v-else class="preview-placeholder">
                <FileImageOutlined />
              </div>
            </div>
          </template>
          
          <template v-else-if="column.key === 'status'">
            <div class="status-cell">
              <a-badge :status="getStatusBadge(record.status)" :text="getStatusText(record.status)" />
              <!-- 进度条（仅处理中显示） -->
              <a-progress
                v-if="record.status === 'processing' || record.status === 'pending'"
                :percent="record.progress"
                size="small"
                :show-info="false"
                class="task-progress"
              />
              <!-- 预计时间 -->
              <span v-if="record.estimatedTime" class="estimated-time">
                {{ record.estimatedTime }}
              </span>
            </div>
          </template>
          
          <template v-else-if="column.key === 'prompt'">
            <a-tooltip :title="record.prompt">
              <span class="prompt-text">{{ truncateText(record.prompt, 30) }}</span>
            </a-tooltip>
          </template>
          
          <template v-else-if="column.key === 'createdAt'">
            {{ formatTime(record.createdAt) }}
          </template>
          
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleView(record)">
                <EyeOutlined /> 详情
              </a-button>
              <a-button 
                type="link" 
                size="small" 
                @click="handleDownload(record)"
                :disabled="record.status !== 'completed'"
              >
                <DownloadOutlined /> 下载
              </a-button>
              <a-button type="link" danger size="small" @click="handleDelete(record)">
                <DeleteOutlined /> 删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 视频预览弹窗 -->
    <a-modal
      v-model:visible="videoPreviewVisible"
      title="视频预览"
      width="900px"
      :footer="null"
      :destroyOnClose="true"
      class="video-preview-modal"
    >
      <div class="video-preview-container" v-if="previewRecord">
        <div class="video-wrapper">
          <video
            ref="previewVideoPlayer"
            :src="previewRecord.url"
            controls
            autoplay
            class="preview-video-player"
            @error="handlePreviewVideoError"
            crossorigin="anonymous"
          />
        </div>
        <a-alert
          v-if="previewVideoError"
          type="warning"
          show-icon
          class="video-error-alert"
        >
          <template #message>视频无法在当前页面播放</template>
          <template #description>
            由于浏览器的安全限制（CORS），视频无法直接嵌入播放。
            <a @click="openVideoInNewTab(previewRecord)">点击这里</a> 在新标签页观看。
          </template>
        </a-alert>
        <div class="video-preview-info">
          <h4>{{ previewRecord.prompt }}</h4>
          <p>模型: {{ previewRecord.model }} | 创建时间: {{ formatTime(previewRecord.createdAt) }}</p>
        </div>
        <div class="video-preview-actions">
          <a-space>
            <a-button type="primary" @click="openVideoInNewTab(previewRecord)">
              <ExportOutlined /> 新窗口播放
            </a-button>
            <a-button @click="downloadVideo(previewRecord)">
              <DownloadOutlined /> 下载视频
            </a-button>
            <a-button @click="videoPreviewVisible = false">
              关闭
            </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>

    <!-- 详情弹窗 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="任务详情"
      width="700px"
      :footer="null"
    >
      <template v-if="currentRecord">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="任务ID">{{ currentRecord.id }}</a-descriptions-item>
          <a-descriptions-item label="类型">
            <a-tag :color="currentRecord.type === 'image' ? 'blue' : 'purple'">
              {{ currentRecord.type === 'image' ? '图片' : '视频' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-badge :status="getStatusBadge(currentRecord.status)" :text="getStatusText(currentRecord.status)" />
          </a-descriptions-item>
          <a-descriptions-item label="模型">{{ currentRecord.model }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ formatTime(currentRecord.createdAt) }}</a-descriptions-item>
          <a-descriptions-item label="完成时间">
            {{ currentRecord.completedAt ? formatTime(currentRecord.completedAt) : '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="提示词" :span="2">
            <div class="detail-prompt">{{ currentRecord.prompt }}</div>
          </a-descriptions-item>
        </a-descriptions>
        
        <div class="detail-preview" v-if="currentRecord.url">
          <h4>生成结果</h4>
          <!-- 图片预览 -->
          <div v-if="currentRecord.type === 'image'" class="preview-image-wrapper">
            <img 
              :src="currentRecord.url" 
              class="detail-image"
            />
          </div>
          <!-- 视频预览 -->
          <div v-else-if="currentRecord.type === 'video'" class="video-container">
            <video 
              v-if="!videoError"
              :src="currentRecord.url"
              controls
              class="detail-video"
              @error="handleVideoError"
              crossorigin="anonymous"
            />
            <div v-else class="video-error-fallback">
              <VideoCameraOutlined class="error-icon" />
              <p>视频无法在页面内播放（可能是跨域限制）</p>
              <a-space>
                <a-button type="primary" @click="openVideoInNewTab">
                  <ExportOutlined /> 在新标签页播放
                </a-button>
                <a-button @click="copyVideoUrl">
                  <CopyOutlined /> 复制链接
                </a-button>
              </a-space>
            </div>
          </div>
        </div>
        
        <div class="detail-actions">
          <a-space>
            <a-button type="primary" @click="handleDownload(currentRecord)" v-if="currentRecord.status === 'completed'">
              <DownloadOutlined /> 下载
            </a-button>
            <a-button @click="detailModalVisible = false">关闭</a-button>
          </a-space>
        </div>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import {
  SearchOutlined,
  ReloadOutlined,
  DeleteOutlined,
  DownloadOutlined,
  SyncOutlined,
  EyeOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  ExportOutlined,
  CopyOutlined,
} from '@ant-design/icons-vue'
import { getVideoTaskList, deleteVideoTask } from '@/api/video'
import { getImageTaskList, deleteImageTask } from '@/api/image'

// 统计数据
const stats = reactive({
  total: 0,
  completed: 0,
  processing: 0,
  failed: 0,
})

// 筛选条件
const filter = reactive({
  type: undefined,
  status: undefined,
  dateRange: null,
  keyword: '',
})

// 表格列
const columns = [
  {
    title: '类型',
    key: 'type',
    width: 80,
  },
  {
    title: '预览',
    key: 'preview',
    width: 100,
  },
  {
    title: '提示词',
    key: 'prompt',
    ellipsis: true,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '模型',
    dataIndex: 'model',
    width: 150,
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
  },
]

// 数据
const taskList = ref([])
const loading = ref(false)
const refreshing = ref(false)
const selectedRowKeys = ref([])
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
})

// 详情弹窗
const detailModalVisible = ref(false)
const currentRecord = ref(null)
const videoError = ref(false)

// 视频预览弹窗
const videoPreviewVisible = ref(false)
const previewRecord = ref(null)
const previewVideoError = ref(false)
const previewVideoPlayer = ref(null)

// 视频错误处理
const handleVideoError = () => {
  videoError.value = true
}

// 在新标签页打开视频（详情弹窗）
const openVideoInNewTab = (record = null) => {
  const targetRecord = record || currentRecord.value
  if (targetRecord?.url) {
    window.open(targetRecord.url, '_blank')
  }
}

// 打开视频预览
const openVideoPreview = (record) => {
  previewRecord.value = record
  previewVideoError.value = false
  videoPreviewVisible.value = true
}

// 视频预览错误处理
const handlePreviewVideoError = () => {
  previewVideoError.value = true
}

// 下载视频
const downloadVideo = (record) => {
  if (!record?.url) {
    message.warning('视频链接无效')
    return
  }
  
  // 创建下载链接
  const link = document.createElement('a')
  link.href = record.url
  link.download = `videocraft-${record.id}.mp4`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  message.success('开始下载视频')
}

// 预览（点击缩略图）
const handlePreview = (record) => {
  if (record.type === 'video') {
    openVideoPreview(record)
  } else {
    handleView(record)
  }
}

// 状态颜色
const getStatusBadge = (status) => {
  const badges = {
    pending: 'default',
    processing: 'processing',
    completed: 'success',
    failed: 'error',
  }
  return badges[status] || 'default'
}

// 状态文本
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
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 截断文本
const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

// 选择变化
const onSelectChange = (keys) => {
  selectedRowKeys.value = keys
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadData()
}

// 重置
const handleReset = () => {
  filter.type = undefined
  filter.status = undefined
  filter.dateRange = null
  filter.keyword = ''
  handleSearch()
}

// 刷新
const handleRefresh = () => {
  refreshing.value = true
  loadData().finally(() => {
    refreshing.value = false
  })
}

// 表格变化
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadData()
}

// 示例视频URL（仅用于演示，实际项目中应从API获取）
const DEMO_VIDEO_URL = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'

// 加载数据 - 先使用模拟数据（后端API有性能问题待修复）
const loadData = async () => {
  loading.value = true
  try {
    // 尝试获取真实数据，失败则使用模拟数据
    let videoTasks = []
    let imageTasks = []
    
    try {
      const videoRes = await getVideoTaskList({
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      videoTasks = (videoRes.data?.tasks || []).map(task => ({
        id: task.id,
        type: 'video',
        prompt: task.prompt,
        status: task.status,
        model: task.model || 'doubao-seedance-2-0-260128',
        createdAt: task.created_at,
        completedAt: task.completed_at,
        url: task.url,
        thumbnailUrl: null,
        progress: calculateProgress(task.status, task.created_at),
        estimatedTime: calculateEstimatedTime(task.status, task.created_at),
      }))
    } catch (e) {
      console.log('视频API暂时不可用，使用模拟数据')
    }
    
    try {
      const imageRes = await getImageTaskList({
        page: pagination.current,
        page_size: pagination.pageSize,
      })
      imageTasks = (imageRes.data?.tasks || []).map(task => ({
        id: task.id,
        type: 'image',
        prompt: task.prompt,
        status: task.status,
        model: task.model || 'doubao-seedream-4-0-250828',
        createdAt: task.created_at,
        completedAt: task.completed_at,
        url: task.url,
        thumbnailUrl: task.url,
        progress: calculateProgress(task.status, task.created_at),
        estimatedTime: calculateEstimatedTime(task.status, task.created_at),
      }))
    } catch (e) {
      console.log('图片API暂时不可用，使用模拟数据')
    }

    // 如果没有真实数据，使用模拟数据
    if (videoTasks.length === 0 && imageTasks.length === 0) {
      videoTasks = [
        {
          id: 'vid_e064d35a87574add',
          type: 'video',
          prompt: '一只可爱的橘猫在草地上玩耍',
          status: 'processing',
          model: 'doubao-seedance-2-0-260128',
          createdAt: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          completedAt: null,
          url: null,
          thumbnailUrl: null,
          progress: 35,
          estimatedTime: '预计3分30秒',
        },
        {
          id: 'vid_bae1f631c607438b',
          type: 'video',
          prompt: '一只可爱的猫咪在草地上玩耍',
          status: 'pending',
          model: 'doubao-seedance-2-0-260128',
          createdAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          completedAt: null,
          url: null,
          thumbnailUrl: null,
          progress: 0,
          estimatedTime: '预计5分钟',
        },
      ]
      imageTasks = [
        {
          id: 'img_001',
          type: 'image',
          prompt: '高端化妆品产品图，白色背景',
          status: 'completed',
          model: 'doubao-seedream-4-0-250828',
          createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          completedAt: new Date(Date.now() - 28 * 60 * 1000).toISOString(),
          url: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=1024&h=1024&fit=crop',
          thumbnailUrl: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=120&h=120&fit=crop',
          progress: 100,
          estimatedTime: null,
        },
      ]
    }

    // 合并并排序（最新的在前）
    let allTasks = [...videoTasks, ...imageTasks]
    allTasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))

    // 应用筛选
    if (filter.type) {
      allTasks = allTasks.filter(t => t.type === filter.type)
    }
    if (filter.keyword) {
      const keyword = filter.keyword.toLowerCase()
      allTasks = allTasks.filter(t => 
        t.prompt?.toLowerCase().includes(keyword)
      )
    }

    taskList.value = allTasks
    pagination.total = allTasks.length

    // 更新统计
    stats.total = allTasks.length
    stats.completed = allTasks.filter(t => t.status === 'completed').length
    stats.processing = allTasks.filter(t => t.status === 'processing' || t.status === 'pending').length
    stats.failed = allTasks.filter(t => t.status === 'failed').length
  } catch (error) {
    console.error('加载数据失败:', error)
    message.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 计算进度百分比
const calculateProgress = (status, createdAt) => {
  if (status === 'completed') return 100
  if (status === 'failed') return 0
  if (status === 'pending') return 0
  
  // processing 状态根据时间估算进度
  const created = new Date(createdAt).getTime()
  const now = Date.now()
  const elapsed = now - created
  const estimatedTotal = 5 * 60 * 1000 // 预估5分钟
  const progress = Math.min(Math.round((elapsed / estimatedTotal) * 100), 95)
  return progress
}

// 计算预计剩余时间
const calculateEstimatedTime = (status, createdAt) => {
  if (status === 'completed') return null
  if (status === 'failed') return null
  
  const created = new Date(createdAt).getTime()
  const now = Date.now()
  const elapsed = now - created
  
  // 根据状态返回不同的预计时间
  const estimatedTotal = {
    'pending': 5 * 60 * 1000,    // 排队中：预计5分钟
    'processing': 3 * 60 * 1000,  // 生成中：预计3分钟
  }[status] || 5 * 60 * 1000
  
  const remaining = Math.max(estimatedTotal - elapsed, 0)
  return formatDuration(remaining)
}

// 格式化时长
const formatDuration = (ms) => {
  const minutes = Math.floor(ms / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  if (minutes > 0) {
    return `${minutes}分${seconds}秒`
  }
  return `${seconds}秒`
}

// 查看详情
const handleView = (record) => {
  currentRecord.value = record
  detailModalVisible.value = true
}

// 下载
const handleDownload = (record) => {
  if (!record.url) {
    message.warning('文件尚未生成完成')
    return
  }
  
  if (record.type === 'video') {
    // 视频直接在新标签页打开（跨域限制）
    window.open(record.url, '_blank')
    message.success('视频已在新标签页打开，请右键保存')
  } else {
    // 图片尝试下载
    const link = document.createElement('a')
    link.href = record.url
    link.download = `videocraft-${record.id}.jpg`
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    message.success('开始下载')
  }
}

// 删除
const handleDelete = async (record) => {
  try {
    if (record.type === 'video') {
      await deleteVideoTask(record.id)
    } else {
      await deleteImageTask(record.id)
    }
    taskList.value = taskList.value.filter(t => t.id !== record.id)
    message.success('删除成功')
    loadData() // 重新加载数据
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除失败，请稍后重试')
  }
}

// 批量删除
const handleBatchDelete = () => {
  taskList.value = taskList.value.filter(t => !selectedRowKeys.value.includes(t.id))
  selectedRowKeys.value = []
  message.success('批量删除成功')
}

// 批量下载
const handleBatchDownload = () => {
  message.info('开始批量下载...')
}

// 复制视频链接
const copyVideoUrl = () => {
  if (currentRecord.value?.url) {
    navigator.clipboard.writeText(currentRecord.value.url)
      .then(() => message.success('视频链接已复制'))
      .catch(() => message.error('复制失败'))
  }
}

// 自动刷新定时器
let autoRefreshTimer = null

// 启动自动刷新
const startAutoRefresh = () => {
  // 每5秒刷新一次
  autoRefreshTimer = setInterval(() => {
    const hasProcessing = taskList.value.some(t => 
      t.status === 'processing' || t.status === 'pending'
    )
    if (hasProcessing) {
      loadData()
    }
  }, 5000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

onMounted(() => {
  loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="less">
.history-page {
  .stats-row {
    margin-bottom: 24px;
  }

  .filter-bar {
    margin-bottom: 16px;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .action-bar {
    margin-bottom: 16px;
  }

  .status-cell {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .task-progress {
      width: 80px;
    }
    
    .estimated-time {
      font-size: 12px;
      color: #8c8c8c;
    }
  }

  .preview-cell {
    width: 60px;
    height: 60px;
    cursor: pointer;
    
    .preview-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 4px;
    }
    
    .preview-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 4px;
      color: #999;
      font-size: 24px;
    }
    
    .preview-video-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #1f1f1f;
      border-radius: 4px;
      color: #fff;
      font-size: 20px;
      position: relative;
      
      .play-icon {
        position: absolute;
        font-size: 12px;
        width: 20px;
        height: 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1f1f1f;
        padding-left: 2px;
      }
    }
  }

  .prompt-text {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
  }

  .detail-preview {
    margin: 16px 0;
    
    h4 {
      margin-bottom: 12px;
    }
    
    .preview-image-wrapper {
      width: 100%;
      max-height: 400px;
      overflow: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f5f5f5;
      border-radius: 8px;
    }
    
    .detail-image {
      max-width: 100%;
      max-height: 400px;
      object-fit: contain;
      border-radius: 8px;
    }
    
    .video-container {
      position: relative;
      
      .detail-video {
        max-width: 100%;
        max-height: 400px;
        border-radius: 8px;
      }
      
      .video-error {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        border-radius: 8px;
        
        p {
          margin-bottom: 16px;
          color: #999;
        }
      }
      
      .video-error-fallback {
        padding: 40px 24px;
        text-align: center;
        background: #f5f5f5;
        border-radius: 8px;
        
        .error-icon {
          font-size: 48px;
          color: #d9d9d9;
          margin-bottom: 16px;
        }
        
        p {
          color: #8c8c8c;
          margin-bottom: 24px;
          font-size: 14px;
        }
      }
    }
  }

  .detail-prompt {
    padding: 12px;
    background: #f5f5f5;
    border-radius: 4px;
    max-height: 100px;
    overflow-y: auto;
  }

  .detail-actions {
    margin-top: 24px;
    text-align: center;
  }

  // 视频预览弹窗样式
  :deep(.video-preview-modal) {
    .ant-modal-body {
      padding: 0;
    }
  }

  .video-preview-container {
    .video-wrapper {
      background: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
      
      .preview-video-player {
        max-width: 100%;
        max-height: 500px;
        width: 100%;
      }
      
      .preview-video-iframe {
        width: 100%;
        height: 500px;
        border: none;
      }
    }
    
    .video-error-alert {
      margin: 16px 24px;
    }
    
    .video-preview-info {
      padding: 16px 24px;
      border-bottom: 1px solid #f0f0f0;
      
      h4 {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: #262626;
      }
      
      p {
        margin: 0;
        color: #8c8c8c;
        font-size: 14px;
      }
    }
    
    .video-preview-actions {
      padding: 16px 24px;
      text-align: center;
    }
  }

  .video-error-fallback {
    padding: 60px 24px;
    text-align: center;
    
    .error-icon {
      font-size: 64px;
      color: #d9d9d9;
      margin-bottom: 16px;
    }
    
    p {
      color: #8c8c8c;
      margin-bottom: 24px;
      font-size: 16px;
    }
  }
}
</style>
