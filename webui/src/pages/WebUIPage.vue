<template>
  <div class="webui-container">
    <h1>橘雪莉表情包生成器</h1>
    
    <div class="meme-generator">
      <div class="input-section">
        <div class="form-group">
          <label>选择表情：</label>
          <select v-model="selectedBackground" @change="updatePreview">
            <option v-for="bg in backgrounds" :key="bg" :value="bg">{{ bg }}</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>输入文字：</label>
          <textarea 
            v-model="inputText" 
            placeholder="请输入要添加的文字"
            @input="updatePreview"
            rows="3"
          ></textarea>
        </div>
        
        <button @click="generateMeme" :disabled="loading">
          {{ loading ? '生成中...' : '生成表情包' }}
        </button>
      </div>
      
      <div class="preview-section">
        <h3>预览</h3>
        <div class="preview-container">
          <div v-if="loading" class="loading">生成中...</div>
          <img v-else-if="previewImage" :src="previewImage" alt="表情包预览">
          <div v-else class="placeholder">请选择表情</div>
        </div>
        
        <div v-if="generatedImage" class="generated-section">
          <h3>生成结果</h3>
          <img :src="generatedImage" alt="生成的表情包">
          <div class="actions">
            <button @click="copyImageUrl">复制图片链接</button>
            <a :href="generatedImage" target="_blank" download>下载图片</a>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 修改类型定义，允许selectedBackground为undefined
const backgrounds = ref<string[]>([])
const selectedBackground = ref<string>('') // 保持非空字符串类型，但确保总是有值
const inputText = ref('我一根手指就能扣晕你')
const loading = ref(false)
const previewImage = ref('')
const generatedImage = ref('')
const message = ref('')
const messageType = ref('success')

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
      showMessage('获取背景列表失败', 'error')
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
    showMessage('获取背景列表时发生错误', 'error')
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

// 生成表情包
const generateMeme = async () => {
  if (!inputText.value.trim()) {
    showMessage('请输入文字内容', 'error')
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
      showMessage('表情包生成成功', 'success')
    } else {
      showMessage('表情包生成失败', 'error')
    }
  } catch (error) {
    console.error('生成表情包出错:', error)
    showMessage('生成表情包时发生错误', 'error')
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

// 复制图片链接
const copyImageUrl = async () => {
  if (!generatedImage.value) {
    showMessage('没有可复制的图片链接', 'error')
    return
  }
  
  try {
    await navigator.clipboard.writeText(generatedImage.value)
    showMessage('图片链接已复制到剪贴板', 'success')
  } catch (error) {
    showMessage('复制失败，请手动复制', 'error')
  }
}

// 显示消息
const showMessage = (text: string, type: string) => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// 页面加载时获取背景列表
onMounted(() => {
  fetchBackgrounds()
})
</script>

<style scoped>
.webui-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
}

.meme-generator {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.input-section,
.preview-section {
  flex: 1;
  min-width: 300px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h3 {
  color: #34495e;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  resize: vertical;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.preview-container {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.preview-container img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.placeholder {
  color: #95a5a6;
  font-style: italic;
}

.loading {
  color: #3498db;
  font-weight: bold;
}

.generated-section {
  margin-top: 30px;
  background: white;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.generated-section img {
  max-width: 100%;
  display: block;
  margin: 0 auto 15px;
}

.actions {
  display: flex;
  gap: 10px;
}

.actions button,
.actions a {
  flex: 1;
  text-align: center;
  text-decoration: none;
  padding: 10px;
  font-size: 14px;
}

.actions a {
  background-color: #2ecc71;
  color: white;
  border-radius: 4px;
}

.actions a:hover {
  background-color: #27ae60;
}

.message {
  margin-top: 20px;
  padding: 10px 15px;
  border-radius: 4px;
  text-align: center;
}

.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .meme-generator {
    flex-direction: column;
  }
}
</style>