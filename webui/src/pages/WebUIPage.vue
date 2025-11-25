<template>
  <div class="webui-container">
    <h1 class="main-title"><span class="first-char">橘</span>雪莉 <span class="subtitle">表情包生成器</span></h1>

    <!-- 移动端生成结果区域（仅在有图片时显示） -->
    <div class="generated-section mobile-only" v-if="generatedImage || loading">
      <h3>生成结果</h3>
      <div class="result-container">
        <div v-if="loading" class="loading">生成中...</div>
        <img v-else :src="generatedImage" alt="生成的表情包">
      </div>
      <div class="actions">
        <button
          @click="downloadImage"
          class="primary-button download-button"
          :class="{ disabled: !generatedImage }"
          :disabled="!generatedImage"
        >
          下载图片
        </button>
      </div>
    </div>

    <!-- 主要内容区域 - 桌面端左右布局 -->
    <div class="main-content">
      <!-- 左侧：编辑区 -->
      <div class="left-panel">
        <div class="input-section">
          <div class="form-group">
            <label class="form-label">选择表情：</label>
            <!-- 胶囊形按钮 -->
            <div class="background-buttons">
              <button
                v-for="bg in backgrounds"
                :key="bg"
                :class="['bg-button', { active: selectedBackground === bg }]"
                @click="selectBackground(bg)"
                :disabled="loading"
              >
                {{ bg }}
              </button>
            </div>

            <!-- 底图预览整合到选择按钮下方 -->
            <div class="integrated-preview">
              <div v-if="loading" class="loading">加载中...</div>
              <img v-else-if="previewImage" :src="previewImage" alt="表情包预览">
              <div v-else class="placeholder">请选择表情</div>
            </div>
          </div>

          <div class="form-group">
            <div class="input-header">
              <label class="form-label highlight-text">表情包显示文字：</label>
              <button
                class="clear-btn"
                @click="clearAll"
                :disabled="!inputText.trim() && !generatedImage"
                :class="{ active: inputText.trim() || generatedImage }"
              >
                清除
              </button>
            </div>
            <textarea
              v-model="inputText"
              placeholder="请输入要添加的文字（不支持换行）"
              @input="updatePreview"
              rows="4"
              class="gray-input"
            ></textarea>
          </div>

          <button @click="generateMeme" :disabled="loading" class="primary-button generate-btn">
            {{ loading ? '生成中...' : '立即生成表情包' }}
          </button>
        </div>
      </div>

      <!-- 右侧：生成结果（桌面端） -->
      <div class="right-panel desktop-only">
        <div class="generated-section enhanced">
          <h3>表情包生成结果</h3>
          <div class="result-container">
            <div v-if="loading" class="loading">正在生成表情包，请稍候...</div>
            <img v-else-if="generatedImage" :src="generatedImage" alt="生成的表情包">
            <div v-else class="placeholder">点击左侧【立即生成表情包】按钮开始创作</div>
          </div>
          <div class="actions">
            <button
              @click="downloadImage"
              class="primary-button download-button"
              :class="{ disabled: !generatedImage }"
              :disabled="!generatedImage"
            >
              下载表情包
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast通知组件 -->
    <div v-if="showToast" :class="['toast', toastType]">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const backgrounds = ref<string[]>([])
const selectedBackground = ref<string>('')
const inputText = ref('')
const loading = ref(false)
const previewImage = ref('')
const generatedImage = ref('')

// Toast相关状态
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')
const showToast = ref(false)

// 从API获取背景列表
const fetchBackgrounds = async () => {
  try {
    const response = await fetch('/list')
    if (response.ok) {
      const data = await response.json()
      backgrounds.value = data.data.background_list
      // 设置默认选中的背景
      if (backgrounds.value.length > 0 && backgrounds.value[0]) {
        selectedBackground.value = backgrounds.value[0]
        updatePreview()
      }
    } else {
      showToastMessage('获取背景列表失败', 'error')
      // 如果API调用失败，使用备用列表
      backgrounds.value = [
        '哭', '慌张', '点赞', '震惊', '惊讶',
        '灵机一动', '好吃', '愣住', '恍悟', '得意'
      ]
      // 添加额外的非空检查
      if (backgrounds.value.length > 0 && backgrounds.value[0]) {
selectedBackground.value = backgrounds.value[0]
        updatePreview()
      }
    }
  } catch (error) {
    console.error('获取背景列表出错:', error)
    showToastMessage('获取背景列表时发生错误', 'error')
    // 使用备用列表
    backgrounds.value = [
      '哭', '慌张', '点赞', '震惊', '惊讶',
      '灵机一动', '好吃', '愣住', '恍悟', '得意'
    ]
    // 添加额外的非空检查
    if (backgrounds.value.length > 0 && backgrounds.value[0]) {
      selectedBackground.value = backgrounds.value[0]
      updatePreview()
    }
  }
}

// 选择背景并更新预览
const selectBackground = (bg: string) => {
  selectedBackground.value = bg
  updatePreview()
}

// 生成表情包
const generateMeme = async () => {
  if (!inputText.value.trim()) {
    showToastMessage('请输入文字内容', 'error')
    return
  }

  loading.value = true
  try {
    const response = await fetch('/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        background: selectedBackground.value,
        text: inputText.value.trim()
      })
    })

    if (response.ok) {
      const data = await response.json()
      generatedImage.value = data.data.img_url
      showToastMessage('表情包生成成功！', 'success')
    } else {
      showToastMessage('表情包生成失败，请重试', 'error')
    }
  } catch (error) {
    console.error('生成表情包出错:', error)
    showToastMessage('生成表情包时发生错误', 'error')
  } finally {
    loading.value = false
  }
}

// 更新预览（使用真实的背景图片）
const updatePreview = async () => {
  if (!selectedBackground.value) return

  try {
    // 使用新的背景图片接口
    previewImage.value = `/background/${selectedBackground.value}`
  } catch (error) {
    console.error('更新预览出错:', error)
    // 失败时使用备用预览
    previewImage.value = `https://picsum.photos/400/600?random=${Math.random()}`
  }
}

// 清除所有内容
const clearAll = () => {
  inputText.value = ''
  generatedImage.value = ''
  showToastMessage('已清除内容', 'success')
}

// Toast消息显示函数
const showToastMessage = (text: string, type: 'success' | 'error') => {
  toastMessage.value = text
  toastType.value = type
  showToast.value = true

  // 3秒后自动隐藏
  setTimeout(() => {
    // 淡出动画
    showToast.value = false
  }, 3000)
}

// 页面加载时获取背景列表
onMounted(() => {
  fetchBackgrounds()
})

// 添加下载表情包函数
const downloadImage = async () => {
  if (!inputText.value.trim()) {
    showToastMessage('请输入文字内容', 'error')
    return
  }

  loading.value = true
  try {
    // 直接调用与生成相同的API接口
    const response = await fetch('/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        background: selectedBackground.value,
        text: inputText.value.trim()
      })
    })

    if (response.ok) {
      const data = await response.json()
      const imgUrl = data.data.img_url

      // 直接打开图片URL，让浏览器处理下载
      window.open(imgUrl, '_blank')
      showToastMessage('表情包下载链接已打开！', 'success')
    } else {
      showToastMessage('获取下载链接失败，请重试', 'error')
    }
  } catch (error) {
    console.error('获取下载链接出错:', error)
    showToastMessage('获取下载链接时发生错误', 'error')
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.webui-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主标题样式 - 蓝色 */
.main-title {
  /* 修改为衬线字体 */
  font-family: 'Times New Roman', 'STZhongsong', serif;
  text-align: center;
  margin-bottom: 30px;
  font-weight: 700;
  font-size: 2.8rem;
  letter-spacing: -0.5px;
  /* 设置默认颜色为白色 */
  color: white;
  /* 添加黑色描边 */
  -webkit-text-stroke: 1px black;
  text-shadow: 0 0 2px black;
}

/* 第一个字样式 - 放大且蓝色 */
.main-title .first-char {
  /* 放大字体 */
  font-size: 1.5em;
  /* 设置为蓝色 */
  color: #4299e1;
  /* 重置描边，只保留蓝色 */
  -webkit-text-stroke: 0 black;
  text-shadow: none;
}

/* 副标题样式 - 蓝色无衬线字体 */
.main-title .subtitle {
  /* 使用无衬线字体 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  /* 设置为蓝色 */
  color: #2d3748;
  /* 重置描边，只保留蓝色 */
  -webkit-text-stroke: 0 black;
  text-shadow: none;
}

/* 主要内容布局 */
.main-content {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

/* 左侧面板 - 包含输入区 */
.left-panel {
  flex: 1;
  min-width: 300px;
}

/* 右侧面板 - 包含生成结果 */
.right-panel {
  flex: 2;
  min-width: 400px;
}

/* 编辑区样式 */
.input-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
}

/* 生成结果区域样式 */
.generated-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 30px;
  text-align: center;
  border: 1px solid #f0f0f0;
}

/* 增强版生成结果区域 */
.generated-section.enhanced {
  padding: 30px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.generated-section.mobile-only {
  margin-bottom: 20px;
}

.generated-section h3 {
  color: #2d3748;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 600;
  font-size: 1.6rem;
}

/* 结果容器样式 - 用于显示生成结果或占位符 */
.result-container {
  background: #fafafa;
  border-radius: 8px;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.generated-section.enhanced .result-container {
  min-height: 550px;
  border: 2px solid #e8e8e8;
}

.result-container img {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.generated-section.enhanced .result-container img {
  max-height: 550px;
}

.actions {
  display: flex;
  justify-content: center;
}

/* 主要按钮样式 - 统一应用于生成和下载按钮 */
.primary-button {
  text-align: center;
  text-decoration: none;
  padding: 16px 36px;
  font-size: 18px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  transition: all 0.3s;
  min-width: 180px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(66, 153, 225, 0.3);
  position: relative;
  overflow: hidden;
  display: inline-block;
  width: 100%;
}

/* 主要按钮hover效果 */
.primary-button:hover:not(.disabled) {
  background-color: #3182ce;
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 16px rgba(66, 153, 225, 0.4);
}

/* 按钮点击波纹效果 */
.primary-button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%);
  transform-origin: 50% 50%;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 1;
  }
  20% {
    transform: scale(25, 25);
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: scale(40, 40);
  }
}

.primary-button:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

/* 禁用状态的按钮 */
.primary-button.disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

/* 禁用链接的默认行为 */
.primary-button[disabled] {
  pointer-events: none;
}

h3 {
  color: #2d3748;
  margin-bottom: 15px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 24px;
}

/* 表单标签样式增强 */
.form-label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2d3748;
  font-size: 1.1rem;
}

/* 高亮文本（蓝色） */
.highlight-text {
  color: #4299e1; /* 主题蓝色 */
}

/* 输入框头部（标签+清除按钮） */
.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 清除按钮样式 */
.clear-btn {
  background: transparent;
  border: none;
  color: #cccccc;
  font-size: 14px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.2s ease;
  width: auto;
}

.clear-btn.active {
  color: #e53e3e; /* 红色 */
  cursor: pointer;
}

.clear-btn.active:hover {
  background-color: #fef2f2;
}

.clear-btn:disabled {
  cursor: not-allowed;
}

/* 胶囊形按钮样式 */
.background-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 16px;
}

.bg-button {
  border-radius: 24px;
  padding: 10px 20px;
  background-color: #f7fafc;
  color: #2d3748;
  border: 1px solid #e2e8f0;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  width: auto;
  flex-shrink: 0;
  font-weight: 500;
}

.bg-button:hover:not(:disabled) {
  background-color: #4299e1;
  color: white;
  border-color: #4299e1;
  transform: translateY(-1px);
}

.bg-button.active {
  background-color: #4299e1;
  color: white;
  border-color: #4299e1;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(66, 153, 225, 0.3);
}

.bg-button:disabled {
  background-color: #e2e8f0;
  cursor: not-allowed;
  opacity: 0.6;
}

/* 灰白底黑字输入框 */
.gray-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 17px;
  resize: vertical;
  background-color: #f7fafc;
  color: #1a202c;
  transition: border 0.3s ease, box-shadow 0.3s ease;
  line-height: 1.5;
}

.gray-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.gray-input::placeholder {
  color: #a0aec0;
  font-size: 16px;
}

/* 输入提示文字 */
.input-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #718096;
  margin-bottom: 0;
}

/* 整合的预览区域 */
.integrated-preview {
  background: #fafafa;
  border-radius: 8px;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: 1px solid #e8e8e8;
}

.integrated-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.placeholder {
  color: #718096;
  font-style: italic;
  font-size: 15px;
  line-height: 1.5;
  padding: 20px;
}

.loading {
  color: #4299e1;
  font-weight: 600;
  font-size: 17px;
}

/* Toast样式 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 28px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 15px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: fadeIn 0.3s ease-in-out, fadeOut 0.3s ease-in-out 2.7s;
  max-width: 90%;
  text-align: center;
}

.toast.success {
  background-color: #48bb78;
}

.toast.error {
  background-color: #e53e3e;
}

/* Toast动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
    transform: translate(-50%, 0);
  }
  to {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
}

/* 响应式设计 - 适配电脑端和手机端 */
/* 默认隐藏移动端内容 */
.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  /* 移动端布局 */
  .main-content {
    flex-direction: column;
  }

  /* 显示移动端生成结果（仅在有内容时） */
  .mobile-only {
    display: block;
  }

  /* 隐藏桌面端内容 */
  .desktop-only {
    display: none;
  }

  /* 左侧面板占据整个宽度 */
  .left-panel {
    min-width: 100%;
  }

  .input-section {
    min-width: 100%;
    margin-bottom: 0;
  }

  /* 手机端胶囊按钮优化 */
  .bg-button {
    font-size: 14px;
    padding: 8px 16px;
  }

  /* 减小标签间距 */
  .background-buttons {
    gap: 8px;
  }

  .webui-container {
    padding: 15px;
  }

  .main-title {
    font-size: 2.2rem;
    margin-bottom: 20px;
  }

  .generated-section {
    padding: 20px;
    margin-bottom: 20px;
  }

  .generated-section h3 {
    font-size: 1.4rem;
  }

  .result-container img,
  .generated-section img {
    max-height: 400px;
  }

  .result-container {
    min-height: 400px;
  }

  .primary-button {
    padding: 14px 28px;
    font-size: 16px;
  }

  /* 手机端Toast样式 */
  .toast {
    top: 15px;
    padding: 12px 24px;
    font-size: 14px;
  }

  .integrated-preview {
    min-height: 180px;
  }

  .integrated-preview img {
    max-height: 180px;
  }
}

@media (max-width: 480px) {
  /* 小屏手机优化 */
  .bg-button {
    font-size: 13px;
    padding: 7px 14px;
  }

  /* 减小间距 */
  .background-buttons {
    gap: 6px;
  }

  .result-container {
    min-height: 300px;
  }

  .result-container img,
  .generated-section img {
    max-height: 300px;
  }

  .integrated-preview {
    min-height: 150px;
  }

  .integrated-preview img {
    max-height: 150px;
  }
}

@media (min-width: 769px) {
  /* 电脑端优化 */
  .main-content {
    align-items: flex-start;
  }

  .left-panel {
    flex: 1;
  }

  .right-panel {
    flex: 2;
  }
}
</style>