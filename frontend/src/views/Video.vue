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
            <a-spin size="large" tip="正在生成视频..." />
            <p class="generating-hint">视频生成可能需要 1-5 分钟，请耐心等待</p>
          </div>

          <!-- 结果列表 -->
          <a-row :gutter="16" v-else>
            <a-col
              :span="12"
              v-for="(item, index) in results"
              :key="index"
              class="result-item"
            >
              <div class="video-wrapper">
                <video :src="item.url" controls poster="@/assets/video-poster.svg"></video>
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
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'
import {
  InboxOutlined,
  VideoCameraOutlined,
  DownloadOutlined,
  CopyOutlined,
} from '@ant-design/icons-vue'
import { createVideoTask } from '@/api/video'
import MultimodalInput from '@/components/MultimodalInput.vue'

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

// 生成状态
const generating = ref(false)
const results = ref([])

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
const customRequest = ({ file, onSuccess }) => {
  setTimeout(() => {
    onSuccess({ url: URL.createObjectURL(file) })
  }, 1000)
}

// 生成视频
const handleGenerate = async () => {
  if (!multimodalContent.text.trim()) {
    message.warning('请输入提示词')
    return
  }

  generating.value = true
  try {
    const res = await createVideoTask({
      model: form.model,
      prompt: multimodalContent.text,
      negative_prompt: form.negativePrompt,
      ratio: form.ratio,
      resolution: form.resolution,
      duration: form.duration,
      num: form.num,
      with_audio: form.withAudio,
      mode: form.mode,
      image_url: multimodalContent.images[0] || undefined,
      video_url: multimodalContent.video || undefined,
      audio_url: multimodalContent.audio || undefined,
    })
    
    message.success('生成任务已创建')
    
    // 添加结果到列表
    if (res && res.task_id) {
      results.value.unshift({
        url: res.url || 'https://example.com/video.mp4',
        prompt: multimodalContent.text,
        createdAt: new Date().toISOString(),
      })
    }
  } catch (error) {
    message.error('生成失败：' + error.message)
  } finally {
    generating.value = false
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

      .generating-hint {
        margin-top: 16px;
        color: #666;
      }
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
