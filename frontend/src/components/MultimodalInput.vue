<template>
  <div class="multimodal-input">
    <!-- 文本输入 -->
    <a-form-item label="提示词">
      <a-textarea
        v-model:value="content.text"
        :rows="4"
        placeholder="描述你想要生成的内容..."
        show-count
        :maxlength="2000"
      />
    </a-form-item>

    <!-- 参考图片 -->
    <a-form-item label="参考图片">
      <a-upload-dragger
        v-model:fileList="imageFileList"
        :before-upload="beforeImageUpload"
        :custom-request="customImageUpload"
        accept="image/*"
        :max-count="maxImages"
        list-type="picture-card"
        @preview="handleImagePreview"
      >
        <div v-if="imageFileList.length < maxImages">
          <PlusOutlined />
          <div style="margin-top: 8px">上传图片</div>
        </div>
      </a-upload-dragger>
      <div class="upload-hint">支持 JPG、PNG 格式，最多 {{ maxImages }} 张</div>
    </a-form-item>

    <!-- 参考视频 -->
    <a-form-item label="参考视频">
      <a-upload-dragger
        v-model:fileList="videoFileList"
        :before-upload="beforeVideoUpload"
        :custom-request="customVideoUpload"
        accept="video/*"
        :max-count="1"
      >
        <p class="ant-upload-drag-icon">
          <VideoCameraOutlined />
        </p>
        <p class="ant-upload-text">点击或拖拽视频到此处</p>
        <p class="ant-upload-hint">支持 MP4、MOV 格式</p>
      </a-upload-dragger>
    </a-form-item>

    <!-- 参考音频 -->
    <a-form-item label="参考音频">
      <a-upload-dragger
        v-model:fileList="audioFileList"
        :before-upload="beforeAudioUpload"
        :custom-request="customAudioUpload"
        accept="audio/*"
        :max-count="1"
      >
        <p class="ant-upload-drag-icon">
          <AudioOutlined />
        </p>
        <p class="ant-upload-text">点击或拖拽音频到此处</p>
        <p class="ant-upload-hint">支持 MP3、WAV 格式</p>
      </a-upload-dragger>
    </a-form-item>

    <!-- 图片预览 -->
    <a-image
      :style="{ display: 'none' }"
      :preview="{
        visible: previewVisible,
        onVisibleChange: (visible) => previewVisible = visible,
      }"
      :src="previewImage"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, VideoCameraOutlined, AudioOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      text: '',
      images: [],
      video: null,
      audio: null
    })
  },
  maxImages: {
    type: Number,
    default: 2
  }
})

const emit = defineEmits(['update:modelValue'])

// 内容数据
const content = reactive({
  text: props.modelValue.text || '',
  images: props.modelValue.images || [],
  video: props.modelValue.video || null,
  audio: props.modelValue.audio || null
})

// 文件列表
const imageFileList = ref([])
const videoFileList = ref([])
const audioFileList = ref([])

// 预览
const previewVisible = ref(false)
const previewImage = ref('')

// 监听变化
watch(() => props.modelValue, (newVal) => {
  content.text = newVal.text || ''
  content.images = newVal.images || []
  content.video = newVal.video || null
  content.audio = newVal.audio || null
}, { deep: true })

watch(content, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

// 图片上传前检查
const beforeImageUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    message.error('只支持 JPG/PNG 格式的图片!')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 视频上传前检查
const beforeVideoUpload = (file) => {
  const isVideo = file.type.startsWith('video/')
  if (!isVideo) {
    message.error('只支持视频文件!')
    return false
  }
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    message.error('视频大小不能超过 100MB!')
    return false
  }
  return true
}

// 音频上传前检查
const beforeAudioUpload = (file) => {
  const isAudio = file.type.startsWith('audio/')
  if (!isAudio) {
    message.error('只支持音频文件!')
    return false
  }
  const isLt20M = file.size / 1024 / 1024 < 20
  if (!isLt20M) {
    message.error('音频大小不能超过 20MB!')
    return false
  }
  return true
}

// 自定义图片上传
const customImageUpload = async ({ file, onSuccess, onError }) => {
  try {
    // 这里应该调用实际上传API
    // 模拟上传成功
    const url = URL.createObjectURL(file)
    content.images.push(url)
    onSuccess?.({ url })
    message.success('图片上传成功')
  } catch (error) {
    onError?.(error)
    message.error('图片上传失败')
  }
}

// 自定义视频上传
const customVideoUpload = async ({ file, onSuccess, onError }) => {
  try {
    const url = URL.createObjectURL(file)
    content.video = url
    onSuccess?.({ url })
    message.success('视频上传成功')
  } catch (error) {
    onError?.(error)
    message.error('视频上传失败')
  }
}

// 自定义音频上传
const customAudioUpload = async ({ file, onSuccess, onError }) => {
  try {
    const url = URL.createObjectURL(file)
    content.audio = url
    onSuccess?.({ url })
    message.success('音频上传成功')
  } catch (error) {
    onError?.(error)
    message.error('音频上传失败')
  }
}

// 图片预览
const handleImagePreview = (file) => {
  previewImage.value = file.url || file.thumbUrl
  previewVisible.value = true
}
</script>

<style scoped lang="less">
.multimodal-input {
  .upload-hint {
    margin-top: 8px;
    color: #999;
    font-size: 12px;
  }

  :deep(.ant-upload-list-picture-card) {
    .ant-upload-list-item {
      width: 120px;
      height: 120px;
    }
  }
}
</style>
