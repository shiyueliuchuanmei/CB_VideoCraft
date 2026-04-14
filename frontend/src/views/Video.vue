<template>
  <div class="video-page">
    <a-row :gutter="24">
      <!-- 左侧：参数配置 -->
      <a-col :span="8">
        <a-card title="视频生成" class="param-card">
          <a-form :model="form" layout="vertical">
            <!-- 生成模式 -->
            <a-form-item label="生成模式">
              <a-radio-group v-model:value="form.mode">
                <a-radio-button value="text2video">文生视频</a-radio-button>
                <a-radio-button value="image2video">图生视频</a-radio-button>
              </a-radio-group>
            </a-form-item>

            <!-- 模型选择 -->
            <a-form-item label="模型">
              <a-select v-model:value="form.model" placeholder="选择模型">
                <a-select-option value="doubao-seedance-2-0-260128">Seedance 2.0</a-select-option>
                <a-select-option value="doubao-seedance-2-0-fast-260128">Seedance 2.0 Fast</a-select-option>
              </a-select>
            </a-form-item>

            <!-- 图片上传（图生视频模式） -->
            <a-form-item label="首帧图片" v-if="form.mode === 'image2video'">
              <a-upload-dragger
                v-model:fileList="fileList"
                :before-upload="beforeUpload"
                :custom-request="customRequest"
                accept="image/*"
                :max-count="1"
              >
                <p class="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p class="ant-upload-text">点击或拖拽图片到此处</p>
                <p class="ant-upload-hint">支持 JPG、PNG 格式，建议 9:16 比例</p>
              </a-upload-dragger>
            </a-form-item>

            <!-- 多模态输入 -->
            <MultimodalInput v-model="multimodalContent" :max-images="2" />

            <!-- 反向提示词 -->
            <a-form-item label="反向提示词">
              <a-textarea
                v-model:value="form.negativePrompt"
                :rows="2"
                placeholder="描述你不想要的内容..."
              />
            </a-form-item>

            <!-- 高级设置 -->
            <a-form-item>
              <a-collapse ghost>
                <a-collapse-panel key="1" header="高级设置">
                  <!-- 视频比例 -->
                  <a-form-item label="视频比例">
                    <a-radio-group v-model:value="form.ratio" button-style="solid">
                      <a-radio-button value="9:16">9:16 (竖屏)</a-radio-button>
                      <a-radio-button value="16:9">16:9 (横屏)</a-radio-button>
                      <a-radio-button value="1:1">1:1 (方形)</a-radio-button>
                    </a-radio-group>
                  </a-form-item>

                  <!-- 分辨率 -->
                  <a-form-item label="分辨率">
                    <a-select v-model:value="form.resolution">
                      <a-select-option value="480p">480p</a-select-option>
                      <a-select-option value="720p">720p</a-select-option>
                      <a-select-option value="1080p">1080p</a-select-option>
                    </a-select>
                  </a-form-item>

                  <!-- 视频时长 -->
                  <a-form-item label="视频时长">
                    <a-slider v-model:value="form.duration" :min="3" :max="10" :step="1" />
                    <span class="duration-hint">{{ form.duration }} 秒</span>
                  </a-form-item>

                  <!-- 生成数量 -->
                  <a-form-item label="生成数量">
                    <a-slider v-model:value="form.num" :min="1" :max="4" />
                  </a-form-item>

                  <!-- 同步声音 -->
                  <a-form-item>
                    <a-checkbox v-model:checked="form.withAudio">
                      同步生成音效
                    </a-checkbox>
                  </a-form-item>
                </a-collapse-panel>
              </a-collapse>
            </a-form-item>

            <!-- 生成按钮 -->
            <a-form-item>
              <a-button
                type="primary"
                size="large"
                block
                :loading="generating"
                @click="handleGenerate"
              >
                <template #icon><VideoCameraOutlined /></template>
                开始生成
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <!-- 右侧：结果展示 -->
      <a-col :span="16">
        <a-card title="生成结果" class="result-card">
          <!-- 空状态 -->
          <a-empty
            v-if="results.length === 0 && !generating"
            description="暂无生成结果"
          >
            <template #image>
              <VideoCameraOutlined style="font-size: 64px; color: #d9d9d9;" />
            </template>
          </a-empty>

          <!-- 生成中 -->
          <div v-if="generating" class="generating">
            <a-spin size="large" />
            <p class="generating-hint">正在生成视频，请耐心等待...</p>
            <a-progress :percent="progress" :status="progress < 100 ? 'active' : 'success'" style="max-width: 400px;" />
            <p class="generating-sub-hint">视频生成可能需要 1-5 分钟</p>
            <p v-if="currentTaskId" class="task-id-hint">
              任务ID: <a-typography-text copyable>{{ currentTaskId }}</a-typography-text>
            </p>
          </div>

          <!-- 结果列表 -->
          <a-row :gutter="16" v-if="!generating && results.length > 0">
            <a-col
              :span="12"
              v-for="(item, index) in results"
              :key="index"
              class="result-item"
            >
              <div class="video-wrapper">
                <video :src="item.url" controls :poster="videoPoster"></video>
                <div class="video-actions">
                  <a-button type="primary" shape="circle" @click="downloadVideo(item.url)">
                    <DownloadOutlined />
                  </a-button>
                  <a-button shape="circle" @click="copyPrompt(item.prompt)">
                    <CopyOutlined />
                  </a-button>
                </div>
              </div>
              <p class="video-prompt">{{ item.prompt }}</p>
            </a-col>
          </a-row>

          <!-- 最近任务 -->
          <a-divider v-if="recentTasks.length > 0 && !generating && results.length === 0" />
          <div v-if="recentTasks.length > 0 && !generating && results.length === 0">
            <h4 style="margin-bottom: 12px;">最近任务</h4>
            <a-list :data-source="recentTasks" size="small">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      {{ truncateText(item.prompt, 30) }}
                      <a-tag :color="getStatusColor(item.status)" size="small" style="margin-left: 8px;">
                        {{ getStatusText(item.status) }}
                      </a-tag>
                    </template>
                    <template #description>
                      <span class="task-id-label">ID: {{ item.task_id || item.id }}</span> · {{ formatTime(item.created_at) }}
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-button type="link" size="small" @click="copyTaskId(item.task_id || item.id)">复制ID</a-button>
                    <a-button type="link" size="small" @click="viewResult(item)" v-if="item.status === 'completed' && item.output_urls?.length">查看结果</a-button>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  InboxOutlined,
  VideoCameraOutlined,
  DownloadOutlined,
  CopyOutlined,
} from '@ant-design/icons-vue'
import { createVideoTask, getVideoTask, getVideoTaskList } from '@/api/video'
import MultimodalInput from '@/components/MultimodalInput.vue'
import videoPoster from '@/assets/video-poster.svg'
import dayjs from 'dayjs'

// 表单数据
const form = reactive({
  mode: 'text2video',
  model: 'doubao-seedance-2-0-260128',
  prompt: '',
  negativePrompt: '',
  ratio: '9:16',
  resolution: '720p',
  duration: 5,
  num: 1,
  withAudio: false,
})

// 多模态内容
const multimodalContent = reactive({
  text: '',
  images: [],
  video: null,
  audio: null
})

// 文件列表
const fileList = ref([])
const uploadedImageUrl = ref('')

// 生成状态
const generating = ref(false)
const progress = ref(0)
const results = ref([])
const recentTasks = ref([])
const currentTaskId = ref('')
let pollTimer = null

// 上传前检查
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件！')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB！')
    return false
  }
  return true
}

// 自定义上传
const customRequest = async ({ file, onSuccess, onError }) => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      if (data.code === 200) {
        uploadedImageUrl.value = data.data.url
        onSuccess({ url: data.data.url })
        message.success('图片上传成功')
      } else {
        onError(new Error(data.message || '上传失败'))
        message.error('上传失败')
      }
    } else {
      uploadedImageUrl.value = URL.createObjectURL(file)
      onSuccess({ url: uploadedImageUrl.value })
    }
  } catch (error) {
    uploadedImageUrl.value = URL.createObjectURL(file)
    onSuccess({ url: uploadedImageUrl.value })
  }
}

// 轮询任务状态
const pollTaskStatus = async (taskId) => {
  const maxAttempts = 120
  const interval = 5000
  let attempts = 0

  const poll = async () => {
    try {
      attempts++
      const data = await getVideoTask(taskId)

      if (data.status === 'completed') {
        generating.value = false
        progress.value = 100
        if (data.output_urls && data.output_urls.length > 0) {
          results.value = data.output_urls.map(url => ({
            url,
            prompt: multimodalContent.text || form.negativePrompt,
          }))
          message.success('视频生成完成')
        }
        loadRecentTasks()
        return
      }

      if (data.status === 'failed') {
        generating.value = false
        progress.value = 0
        message.error(data.error_message || '视频生成失败')
        loadRecentTasks()
        return
      }

      if (data.status === 'cancelled') {
        generating.value = false
        progress.value = 0
        message.info('任务已取消')
        loadRecentTasks()
        return
      }

      // 更新进度
      if (data.status === 'processing') {
        progress.value = Math.min(90, 20 + attempts)
      } else if (data.status === 'pending') {
        progress.value = Math.min(20, 5 + attempts)
      }

      if (attempts < maxAttempts) {
        pollTimer = setTimeout(poll, interval)
      } else {
        generating.value = false
        message.warning('查询超时，请稍后在历史记录中查看')
        loadRecentTasks()
      }
    } catch (error) {
      if (attempts < maxAttempts) {
        pollTimer = setTimeout(poll, interval)
      } else {
        generating.value = false
        message.error('查询任务状态失败')
      }
    }
  }

  poll()
}

// 生成视频
const handleGenerate = async () => {
  if (!multimodalContent.text.trim()) {
    message.warning('请输入提示词')
    return
  }

  if (form.mode === 'image2video' && !uploadedImageUrl.value && !multimodalContent.images.length) {
    message.warning('请上传首帧图片')
    return
  }

  generating.value = true
  progress.value = 5
  results.value = []

  try {
    const data = await createVideoTask({
      model: form.model,
      prompt: multimodalContent.text,
      negative_prompt: form.negativePrompt,
      ratio: form.ratio,
      resolution: form.resolution,
      duration: form.duration,
      num: form.num,
      with_audio: form.withAudio,
      mode: form.mode,
      image_url: form.mode === 'image2video' ? (uploadedImageUrl.value || multimodalContent.images[0]) : undefined,
      video_url: multimodalContent.video || undefined,
      audio_url: multimodalContent.audio || undefined,
    })

    message.success('生成任务已创建')
    progress.value = 10
    currentTaskId.value = data.task_id || ''

    // 开始轮询任务状态
    if (data.task_id) {
      pollTaskStatus(data.task_id)
    }
  } catch (error) {
    generating.value = false
    progress.value = 0
    message.error('生成失败：' + (error.message || '未知错误'))
  }
}

// 加载最近任务
const loadRecentTasks = async () => {
  try {
    const data = await getVideoTaskList({ page: 1, page_size: 5 })
    recentTasks.value = data.tasks || data.items || []
  } catch (error) {
    // 静默失败
  }
}

// 查看结果
const viewResult = (item) => {
  if (item.output_urls && item.output_urls.length > 0) {
    results.value = item.output_urls.map(url => ({
      url,
      prompt: item.prompt,
    }))
  }
}

// 下载视频
const downloadVideo = (url) => {
  const link = document.createElement('a')
  link.href = url
  link.download = `generated-${Date.now()}.mp4`
  link.click()
}

// 复制提示词
const copyPrompt = (prompt) => {
  navigator.clipboard.writeText(prompt)
  message.success('提示词已复制')
}

// 复制任务ID
const copyTaskId = (taskId) => {
  navigator.clipboard.writeText(taskId)
  message.success('任务ID已复制')
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

onMounted(() => {
  loadRecentTasks()
})

onUnmounted(() => {
  if (pollTimer) {
    clearTimeout(pollTimer)
  }
})
</script>

<style scoped lang="less">
.video-page {
  .param-card {
    .ant-upload-drag-icon {
      font-size: 48px;
      color: #1890ff;
    }

    .duration-hint {
      color: #666;
      font-size: 12px;
    }
  }

  .result-card {
    min-height: 600px;

    .generating {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 400px;
      gap: 12px;

      .generating-hint {
        color: #333;
        font-size: 16px;
      }

      .generating-sub-hint {
        color: #999;
        font-size: 12px;
      }

      .task-id-hint {
        color: #999;
        font-size: 12px;
        margin-top: 4px;
      }
    }

    .task-id-label {
      font-family: monospace;
      font-size: 11px;
      color: #999;
    }

    .result-item {
      margin-bottom: 16px;

      .video-wrapper {
        position: relative;
        border-radius: 8px;
        overflow: hidden;
        background: #f5f5f5;

        video {
          width: 100%;
          aspect-ratio: 9/16;
          object-fit: cover;
          display: block;
        }

        .video-actions {
          position: absolute;
          bottom: 8px;
          right: 8px;
          display: flex;
          gap: 8px;
          opacity: 0;
          transition: opacity 0.3s;
        }

        &:hover .video-actions {
          opacity: 1;
        }
      }

      .video-prompt {
        margin-top: 8px;
        font-size: 12px;
        color: #666;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style>
