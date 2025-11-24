<template>
  <div class="admin-container">
    <h1>管理页面</h1>
    <div v-if="loading">加载配置中...</div>
    <div v-else>
      <div class="config-section">
        <h2>API 配置</h2>
        <div class="form-group">
          <label>域名：</label>
          <input v-model="config.api.domain" type="text" placeholder="请输入域名">
        </div>
        <div class="form-group">
          <label>端口：</label>
          <input v-model.number="config.api.port" type="number" placeholder="请输入端口">
        </div>
        <div class="form-group">
          <label>Token：</label>
          <input v-model="config.api.token" type="text" placeholder="请输入Token">
        </div>
      </div>

      <div class="config-section">
        <h2>日志配置</h2>
        <div class="form-group">
          <label>日志级别：</label>
          <select v-model="config.log.log_level">
            <option value="debug">Debug</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      <div class="config-section">
        <h2>存储配置</h2>
        <div class="form-group">
          <label>图片过期时间（秒）：</label>
          <input v-model.number="config.storage.image_expiry_time" type="number" placeholder="请输入过期时间">
        </div>
      </div>

      <div class="action-buttons">
        <button @click="saveConfig" :disabled="saving">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
        <button @click="loadConfig">重新加载</button>
        <button @click="goToGeneratePage" class="generate-btn">
          前往表情包生成页面
        </button>
      </div>

      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface Config {
  name: string
  work_dir: string
  log: {
    log_level: string
    output_path: string
    output_file: string
  }
  api: {
    route_root: string
    port: number
    host: string
    token: string
    domain: string
  }
  resource: {
    resource_paths: Record<string, string>
    chinese_font_path: string
    english_font_path: string
  }
  storage: {
    image_expiry_time: number
  }
}

const loading = ref(true)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')
const config = reactive<Config>({
  name: '',
  work_dir: '',
  log: {
    log_level: 'info',
    output_path: 'data/',
    output_file: 'log.txt'
  },
  api: {
    route_root: '/',
    port: 7210,
    host: '0.0.0.0',
    token: '',
    domain: 'www.example.com'
  },
  resource: {
    resource_paths: {},
    chinese_font_path: 'resource/fonts/STHeitiMedium.ttc',
    english_font_path: 'resource/fonts/Times New Roman.ttf'
  },
  storage: {
    image_expiry_time: 300
  }
})

// 加载配置
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await fetch('/config')
    if (response.ok) {
      const data = await response.json()
      Object.assign(config, data)
      showMessage('配置加载成功', 'success')
    } else {
      showMessage('配置加载失败', 'error')
    }
  } catch (error) {
    console.error('加载配置出错:', error)
    showMessage('加载配置时发生错误', 'error')
  } finally {
    loading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    const response = await fetch('/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    
    if (response.ok) {
      showMessage('配置保存成功并已热更新', 'success')
    } else {
      showMessage('配置保存失败', 'error')
    }
  } catch (error) {
    console.error('保存配置出错:', error)
    showMessage('保存配置时发生错误', 'error')
  } finally {
    saving.value = false
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

// 页面加载时获取配置
onMounted(() => {
  loadConfig()
})

// 跳转到生成页面
const goToGeneratePage = () => {
  window.location.href = '/webui';
}
</script>

<style scoped>
.admin-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
}

h2 {
  color: #34495e;
  margin-top: 30px;
  margin-bottom: 20px;
  font-size: 1.2em;
}

.config-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:first-child {
  background-color: #3498db;
  color: white;
}

button:first-child:hover:not(:disabled) {
  background-color: #2980b9;
}

button:first-child:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

button:last-child {
  background-color: #ecf0f1;
  color: #2c3e50;
}

button:last-child:hover {
  background-color: #bdc3c7;
}

.message {
  margin-top: 20px;
  padding: 10px 15px;
  border-radius: 4px;
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

.generate-btn {
  background-color: #27ae60;
  color: white;
}

.generate-btn:hover {
  background-color: #219a52;
}
</style>