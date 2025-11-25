<template>
  <div class="admin-container">
    <!-- 密码设置/登录模态框 -->
    <div v-if="showPasswordSetup || showLogin" class="modal-overlay" @click.self="handleBackdropClick">
      <div class="modal-content">
        <h2>{{ showPasswordSetup ? '设置管理员密码' : '管理员登录' }}</h2>
        <p v-if="showPasswordSetup" class="modal-description">首次访问，请设置一个管理员密码以保护您的配置页面</p>

        <div v-if="!showPasswordSetup" class="form-group">
          <label class="form-label">密码：</label>
          <input
            v-model="loginPassword"
            type="password"
            class="gray-input"
            placeholder="请输入密码"
            @keyup.enter="verifyPassword"
          >
        </div>

        <div v-if="showPasswordSetup" class="form-group">
          <label class="form-label">设置密码：</label>
          <input
            v-model="newPassword"
            type="password"
            class="gray-input"
            placeholder="请设置密码"
          >
        </div>

        <div v-if="showPasswordSetup" class="form-group">
          <label class="form-label">确认密码：</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="gray-input"
            placeholder="请再次输入密码"
            @keyup.enter="setPassword"
          >
          <div v-if="newPassword && confirmPassword && newPassword !== confirmPassword" class="error-message">
            两次输入的密码不一致
          </div>
        </div>

        <div class="modal-actions">
          <button
            v-if="showPasswordSetup"
            @click="setPassword"
            :disabled="!newPassword || !confirmPassword || newPassword !== confirmPassword || processing"
            class="primary-button"
          >
            {{ processing ? '设置中...' : '确认设置' }}
          </button>
          <button
            v-else
            @click="verifyPassword"
            :disabled="!loginPassword || processing"
            class="primary-button"
          >
            {{ processing ? '登录中...' : '登录' }}
          </button>
</div>

        <div v-if="modalError" class="error-message">{{ modalError }}</div>
      </div>
    </div>

    <!-- 密码重置模态框 -->
    <div v-if="showPasswordReset" class="modal-overlay" @click.self="cancelPasswordReset">
      <div class="modal-content">
        <h2>重置管理员密码</h2>

        <div class="form-group">
          <label class="form-label">旧密码：</label>
          <input
            v-model="resetOldPassword"
            type="password"
            class="gray-input"
            placeholder="请输入旧密码"
          >
        </div>

        <div class="form-group">
          <label class="form-label">新密码：</label>
          <input
            v-model="resetNewPassword"
            type="password"
            class="gray-input"
            placeholder="请输入新密码"
          >
        </div>

        <div class="form-group">
          <label class="form-label">确认新密码：</label>
          <input
            v-model="resetConfirmPassword"
            type="password"
            class="gray-input"
            placeholder="请再次输入新密码"
            @keyup.enter="resetPassword"
          >
        </div>

        <div class="error-message" v-if="resetPasswordError">{{ resetPasswordError }}</div>

        <div class="modal-actions">
          <button
            @click="resetPassword"
            :disabled="!resetOldPassword || !resetNewPassword || !resetConfirmPassword || processing"
            class="primary-button"
          >
            {{ processing ? '重置中...' : '确认重置' }}
          </button>
          <button @click="cancelPasswordReset" class="secondary-button">取消</button>
        </div>
      </div>
    </div>

    <h1 class="main-title"><span class="first-char">橘</span>雪莉 <span class="subtitle">表情包管理页面</span></h1>

    <div v-if="message" :class="['toast', messageType]">
      {{ message }}
    </div>

    <!-- 主要内容区域 - 桌面端左右布局 -->
    <div class="main-content" v-if="authenticated">
      <!-- 左侧：配置表单 -->
      <div class="left-panel">
        <div v-if="loading" class="loading">加载配置中...</div>
        <div v-else class="config-section">
          <div class="form-group">
            <h2>API 配置</h2>
            <div class="form-item">
              <label class="form-label">域名：</label>
              <input v-model="config.api.domain" type="text" class="gray-input" placeholder="请输入域名">
            </div>
            <div class="form-item">
              <label class="form-label">端口：</label>
              <div class="port-input-container">
                <input v-model.number="config.api.port" type="number" class="gray-input" placeholder="请输入端口">
                <div class="port-tip">修改端口需要重启服务</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <h2>存储配置</h2>
            <div class="form-item">
              <label class="form-label">图片过期时间（秒）：</label>
              <input v-model.number="config.storage.image_expiry_time" type="number" class="gray-input" placeholder="请输入过期时间">
            </div>
          </div>

          <div class="action-buttons">
            <button @click="saveConfig" :disabled="saving" class="primary-button">
              {{ saving ? '保存中...' : '保存配置' }}
            </button>
            <button @click="loadConfig" class="secondary-button">重新加载</button>
            <button @click="goToGeneratePage" class="primary-button generate-btn">
              前往表情包生成页面
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：日志显示 -->
      <div class="right-panel">
        <div class="logs-section">
          <div class="logs-header">
            <h3>实时日志</h3>
            <div class="logs-header-actions">
              <button @click="showResetPasswordModal" class="secondary-button reset-password-btn">
                重置密码
              </button>
              <button @click="refreshLogs" :disabled="loadingLogs || loadingMore" class="refresh-button">
                {{ loadingLogs ? '刷新中...' : (loadingMore ? '加载中...' : '刷新日志') }}
              </button>
            </div>
          </div>

          <!-- 日志过滤器 -->
          <div class="logs-filter">
            <div class="filter-item">
              <label class="filter-label">日志级别：</label>
              <select v-model="filterLevel" @change="applyFilters" class="filter-select gray-input">
                <option value="">全部</option>
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
              </select>
            </div>
            <div class="filter-item">
              <label class="filter-label">搜索关键词：</label>
              <input
                v-model="searchKeyword"
                @input="applyFilters"
                type="text"
                class="filter-input gray-input"
                placeholder="输入关键词搜索"
              >
            </div>
            <!-- 添加排序切换按钮 -->
            <div class="filter-item">
              <button @click="toggleSortOrder" class="sort-button gray-input">
                {{ isReverseOrder ? '排序：倒序' : '排序：顺序' }}
              </button>
            </div>
            <div class="filter-stats">
              显示 {{ displayLogs.length }}/{{ totalLogs }} 条日志
            </div>
          </div>

          <div class="logs-container">
            <div v-if="loadingLogs && !displayLogs.length" class="loading">加载日志中...</div>
            <div v-else-if="displayLogs.length > 0"
                 class="logs-content"
                 @scroll="handleScroll"
                 ref="logsContainerRef">
              <!-- 使用v-memo优化渲染性能 -->
              <div
                v-for="(log, index) in displayLogs"
                :key="index"
                class="log-entry"
                :class="getLogLevelClass(log)"
                v-memo="[log]">
                <!-- 将日志按格式解析并结构化显示 -->
                <template v-if="parseLogLine(log)">
                  <span class="log-timestamp">{{ parseLogLine(log)?.timestamp }}</span>
                  <span class="log-level">{{ parseLogLine(log)?.level }}</span>
                  <span class="log-content">{{ parseLogLine(log)?.content }}</span>
                </template>
                <template v-else>
                  {{ log }}
                </template>
              </div>
              <!-- 加载更多提示 -->
              <div v-if="loadingMore" class="loading-more">加载更多日志...</div>
              <!-- 没有更多日志提示 -->
              <div v-if="!hasMoreLogs && displayLogs.length > 0" class="no-more-logs">已经到顶啦！>_<</div>
            </div>
            <div v-else class="placeholder">
              {{ totalLogs > 0 ? '没有符合条件的日志' : '暂无日志内容' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'

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
  admin: {
    password_hash: string
  }
}

// 认证相关状态
const authenticated = ref(false)
const showPasswordSetup = ref(false)
const showLogin = ref(false)
const showPasswordReset = ref(false)
const processing = ref(false)
const modalError = ref('')

// 密码设置/登录表单
const loginPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// 密码重置表单
const resetOldPassword = ref('')
const resetNewPassword = ref('')
const resetConfirmPassword = ref('')
const resetPasswordError = ref('')

const loading = ref(true)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')
const rawLogs = ref<string[]>([])
const filteredLogs = ref<string[]>([])
const displayLogs = ref<string[]>([])
const totalLogs = ref(0)
const loadingLogs = ref(false)
const loadingMore = ref(false)
const logsInterval = ref<number | null>(null)
const logsContainerRef = ref<HTMLElement>()

// 懒加载相关状态
const pageSize = 200 // 每页显示的日志数量
const currentPage = ref(1)
const hasMoreLogs = ref(true)

// 过滤器状态
const filterLevel = ref('INFO'); // 将默认值从空字符串改为'INFO'
const searchKeyword = ref('');
const isReverseOrder = ref(true); // 添加排序控制变量，true表示倒序（最新在前）

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
  },
  admin: {
    password_hash: ''
  }
})

// 解析日志行格式
const parseLogLine = (logLine: string) => {
  // 尝试匹配常见的日志格式：[timestamp] [level] content 或 timestamp level content
  const regex = /^(\[?\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}[\.,]?\d*\]?)\s*(\[?(?:DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\]?)\s*(.*)$/i;
  const match = logLine.match(regex);

  if (match) {
    return {
      timestamp: match[1]?.replace(/[\[\]]/g, '').trim(),
      level: match[2]?.replace(/[\[\]]/g, '').trim(),
      content: match[3]?.trim()
    };
  }

  // 尝试匹配更简单的格式，如：timestamp [module] level: content
  const simpleRegex = /^(\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}[\.,]?\d*)\s*\[.*?\]\s*(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL):?\s*(.*)$/i;
  const simpleMatch = logLine.match(simpleRegex);

  if (simpleMatch) {
    return {
      timestamp: simpleMatch[1]?.trim(),
      level: simpleMatch[2]?.trim(),
      content: simpleMatch[3]?.trim()
    };
  }

  // 如果无法解析，返回null
  return null;
}

// 检查认证状态
const checkAuth = async () => {
  try {
    // 尝试从cookie获取令牌
    const token = getCookie('admin_token')
    if (token) {
      // 在实际应用中，这里应该验证token的有效性
      authenticated.value = true
      // 加载配置（已认证状态）
      await loadConfig()
      return
    }

    // 加载配置以检查是否存在密码hash
    await loadConfig()

    // 检查配置中是否存在密码hash
    if (!config.admin || !config.admin.password_hash) {
      // 密码hash不存在，需要设置密码
      showPasswordSetup.value = true
    } else {
      // 密码hash存在，需要登录
      showLogin.value = true
    }
  } catch (error) {
    console.error('检查认证状态失败:', error)
    showLogin.value = true
  }
}

// 设置密码
const setPassword = async () => {
  if (!newPassword.value || !confirmPassword.value || newPassword.value !== confirmPassword.value) {
    modalError.value = '两次输入的密码不一致'
    return
  }

  processing.value = true
  modalError.value = ''

  try {
    const response = await fetch('/admin/password/set', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password: newPassword.value })
    })

    const data = await response.json()

    if (data.code === 200) {
      showPasswordSetup.value = false
      authenticated.value = true
      showMessage('密码设置成功', 'success')
      // 清除表单
      newPassword.value = ''
      confirmPassword.value = ''
      // 加载配置
      loadConfig()
      loadLogs()
    } else {
      modalError.value = data.message || '设置密码失败'
    }
  } catch (error) {
    console.error('设置密码失败:', error)
    modalError.value = '设置密码失败，请重试'
  } finally {
    processing.value = false
  }
}

// 验证密码
const verifyPassword = async () => {
  if (!loginPassword.value) {
    modalError.value = '请输入密码'
    return
  }

  processing.value = true
  modalError.value = ''

  try {
    const response = await fetch('/admin/password/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ password: loginPassword.value })
    })

    const data = await response.json()

    if (data.code === 200) {
      // 设置cookie保存登录状态
      setCookie('admin_token', data.data.token, 24) // 有效期24小时
      showLogin.value = false
      authenticated.value = true
      // 清除表单
      loginPassword.value = ''
      // 加载配置
      loadConfig()
      loadLogs()
    } else if (data.code === 401 && data.data?.need_setup) {
      // 需要设置密码
      showLogin.value = false
      showPasswordSetup.value = true
    } else {
      modalError.value = data.message || '验证失败'
    }
  } catch (error) {
    console.error('验证密码失败:', error)
    modalError.value = '验证失败，请重试'
  } finally {
    processing.value = false
  }
}

// 显示重置密码模态框
const showResetPasswordModal = () => {
  showPasswordReset.value = true
  resetOldPassword.value = ''
  resetNewPassword.value = ''
  resetConfirmPassword.value = ''
  resetPasswordError.value = ''
}

// 取消重置密码
const cancelPasswordReset = () => {
  showPasswordReset.value = false
  resetOldPassword.value = ''
  resetNewPassword.value = ''
  resetConfirmPassword.value = ''
  resetPasswordError.value = ''
}

// 重置密码
const resetPassword = async () => {
  // 验证输入
  if (!resetOldPassword.value || !resetNewPassword.value || !resetConfirmPassword.value) {
    resetPasswordError.value = '请填写所有密码字段'
    return
  }

  if (resetNewPassword.value !== resetConfirmPassword.value) {
    resetPasswordError.value = '新密码和确认密码不一致'
    return
  }

  processing.value = true
  resetPasswordError.value = ''

  try {
    const response = await fetch('/admin/password/reset', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_password: resetOldPassword.value,
        new_password: resetNewPassword.value
      })
    })

    const data = await response.json()

    if (data.code === 200) {
      // 重置成功，需要重新登录
      cancelPasswordReset()
      authenticated.value = false
      showLogin.value = true
      showMessage('密码重置成功，请重新登录', 'success')
      // 清除cookie
      setCookie('admin_token', '', -1)
    } else {
      resetPasswordError.value = data.message || '重置密码失败'
    }
  } catch (error) {
    console.error('重置密码失败:', error)
    resetPasswordError.value = '重置密码失败，请重试'
  } finally {
    processing.value = false
  }
}

// 模态框背景点击处理
const handleBackdropClick = () => {
  if (!authenticated.value) return // 未认证时不允许关闭
  showPasswordSetup.value = false
  showLogin.value = false
}

// Cookie操作函数
const setCookie = (name: string, value: string, hours: number) => {
  const expires = new Date()
  expires.setTime(expires.getTime() + hours * 60 * 60 * 1000)
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`
}

const getCookie = (name: string): string => {
  // 添加对 document.cookie 的检查
  if (!document.cookie) {
    return ''
  }

  const cookieName = `${name}=`
  const cookies = document.cookie.split(';')

  for (let i = 0; i < cookies.length; i++) {
    // 添加对 cookies[i] 的安全检查
    const cookie = cookies[i]?.trim() || ''
    if (cookie.indexOf(cookieName) === 0) {
      return cookie.substring(cookieName.length, cookie.length)
    }
  }
  return ''
}

// 加载配置
const loadConfig = async () => {
  loading.value = true
  try {
    const response = await fetch('/config')
    if (response.ok) {
      const data = await response.json()
      Object.assign(config, data)
      // 不显示消息，因为这可能是在验证前调用的
    } else {
      console.error('配置加载失败')
    }
  } catch (error) {
    console.error('加载配置出错:', error)
  } finally {
    loading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  if (!authenticated.value) return

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
      const data = await response.json()
      if (data.status === 'success') {
        showMessage('配置保存成功', 'success')
        // 如果修改了端口，提示需要重启服务
        if (data.portChanged) {
          showMessage('端口已修改，需要重启服务才能生效', 'warning')
        }
      } else {
        showMessage(`配置保存失败: ${data.message || '未知错误'}`, 'error')
      }
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

// 加载日志
const loadLogs = async () => {
  if (!authenticated.value) return

  // 保存当前滚动位置和状态
  const logsContentElement = document.querySelector('.logs-content');
  let scrollPosition = 0;
  let isScrolledToTop = true;

  if (logsContentElement) {
    scrollPosition = logsContentElement.scrollTop;
    // 判断用户是否在顶部（顶部5px内都视为在顶部）
    isScrolledToTop = scrollPosition < 5;
  }

  loadingLogs.value = true;
  try {
    const response = await fetch('/logs');
    if (response.ok) {
      const data = await response.json();
      // 将日志按行分割并过滤空行，然后反转数组使最新日志在顶部
      rawLogs.value = data.data.logs.split('\n')
        .filter((line: string) => line.trim())
        .reverse(); // 反转数组顺序，使最新日志在顶部

      // 重置分页状态
      currentPage.value = 1;
      totalLogs.value = rawLogs.value.length;

      // 应用过滤器并加载第一页
      applyFilters();

      // 使用Vue的nextTick确保DOM完全更新
      await nextTick();

      // 恢复滚动位置
      if (logsContentElement) {
        if (isScrolledToTop) {
          // 如果之前在顶部，则保持在顶部（显示最新日志）
          logsContentElement.scrollTop = 0;
        } else {
          // 否则保持相对位置，确保用户查看的内容大致不变
          logsContentElement.scrollTop = scrollPosition;
        }
      }
    } else {
      console.error('加载日志失败');
    }
  } catch (error) {
    console.error('加载日志出错:', error);
  } finally {
    loadingLogs.value = false;
  }
}

// 加载更多日志
const loadMoreLogs = async () => {
  if (!authenticated.value || loadingMore.value || !hasMoreLogs.value) return;

  loadingMore.value = true;
  try {
    // 计算新的页面
    const nextPage = currentPage.value + 1;

    // 计算新页面的起始和结束索引
    const startIndex = (nextPage - 1) * pageSize;
    const endIndex = Math.min(nextPage * pageSize, filteredLogs.value.length);

    // 检查是否还有更多日志
    if (startIndex >= filteredLogs.value.length) {
      hasMoreLogs.value = false;
      return;
    }

    // 获取新页面的日志
    const newLogs = filteredLogs.value.slice(startIndex, endIndex);

    // 保留当前滚动位置
    const logsContainer = logsContainerRef.value;
    const currentScrollHeight = logsContainer?.scrollHeight || 0;

    // 添加新日志到显示列表
    displayLogs.value = [...displayLogs.value, ...newLogs];

    // 更新页码
    currentPage.value = nextPage;

    // 检查是否还有更多日志
    if (endIndex >= filteredLogs.value.length) {
      hasMoreLogs.value = false;
    }

    // 使用nextTick保持滚动位置
    await nextTick();

    // 恢复滚动位置，避免页面跳动
    if (logsContainer) {
      const newScrollHeight = logsContainer.scrollHeight;
      const heightDiff = newScrollHeight - currentScrollHeight;
      logsContainer.scrollTop += heightDiff;
    }
  } catch (error) {
    console.error('加载更多日志出错:', error);
  } finally {
    loadingMore.value = false;
  }
}

// 定义日志级别优先级（数值越大，级别越高）
const LOG_LEVEL_PRIORITY = {
  'DEBUG': 1,
  'INFO': 2,
  'WARNING': 3,
  'ERROR': 4,
  'CRITICAL': 5
};

// 获取日志行的级别
const getLogLevel = (line: string): string => {
  if (line.includes('ERROR') || line.includes('ERROR -')) return 'ERROR';
  if (line.includes('WARNING') || line.includes('WARNING -')) return 'WARNING';
  if (line.includes('INFO') || line.includes('INFO -')) return 'INFO';
  if (line.includes('DEBUG') || line.includes('DEBUG -')) return 'DEBUG';
  if (line.includes('CRITICAL') || line.includes('CRITICAL -')) return 'CRITICAL';
  return 'DEBUG'; // 默认最低级别
};

// 应用日志过滤器
const applyFilters = () => {
  if (!authenticated.value) return;

  let filtered = [...rawLogs.value];

  // 按日志级别过滤
  if (filterLevel.value) {
    const selectedPriority = LOG_LEVEL_PRIORITY[filterLevel.value as keyof typeof LOG_LEVEL_PRIORITY];
    filtered = filtered.filter(line => {
      const logLevel = getLogLevel(line);
      const logPriority = LOG_LEVEL_PRIORITY[logLevel as keyof typeof LOG_LEVEL_PRIORITY];
      // 只保留大于等于所选级别的日志（过滤更低级别的日志）
      return logPriority >= selectedPriority;
    });
  }

  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase();
    filtered = filtered.filter(line => line.toLowerCase().includes(keyword));
  }

  // 根据排序设置决定是否反转日志顺序
  filteredLogs.value = isReverseOrder.value ? filtered : [...filtered].reverse();

  // 重置分页状态
  currentPage.value = 1;
  hasMoreLogs.value = filteredLogs.value.length > pageSize;

  // 加载第一页日志
  displayLogs.value = filteredLogs.value.slice(0, pageSize);

  // 使用nextTick滚动到顶部
  nextTick(() => {
    const logsContainer = logsContainerRef.value;
    if (logsContainer) {
      logsContainer.scrollTop = 0;
    }
  });
};

// 处理滚动事件，实现懒加载
const handleScroll = () => {
  if (!authenticated.value) return;

  const logsContainer = logsContainerRef.value;
  if (!logsContainer || loadingMore.value || !hasMoreLogs.value) return;

  const { scrollTop, clientHeight, scrollHeight } = logsContainer;

  // 当滚动到距离底部50px时加载更多
  if (scrollHeight - scrollTop - clientHeight < 50) {
    loadMoreLogs();
  }
};

// 获取日志级别对应的CSS类
const getLogLevelClass = (logLine: string) => {
  // 尝试使用解析后的日志级别
  const parsedLog = parseLogLine(logLine);
  if (parsedLog) {
    const level = parsedLog.level?.toUpperCase() || '';
    if (level === 'ERROR') return 'log-error';
    if (level === 'WARNING') return 'log-warning';
    if (level === 'INFO') return 'log-info';
    if (level === 'DEBUG') return 'log-debug';
    if (level === 'CRITICAL') return 'log-error'; //  critical 错误也显示为错误样式
  }

  // 回退到原始检测逻辑
  if (logLine.includes('ERROR') || logLine.includes('ERROR -')) return 'log-error';
  if (logLine.includes('WARNING') || logLine.includes('WARNING -')) return 'log-warning';
  if (logLine.includes('INFO') || logLine.includes('INFO -')) return 'log-info';
  if (logLine.includes('DEBUG') || logLine.includes('DEBUG -')) return 'log-debug';
  return 'log-default';
};

// 刷新日志
const refreshLogs = () => {
  loadLogs();
};

// 显示消息
const showMessage = (text: string, type: string) => {
  message.value = text;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 3000);
};

// 切换排序方式
const toggleSortOrder = () => {
  isReverseOrder.value = !isReverseOrder.value;
  applyFilters(); // 切换后重新应用过滤器和排序
};

// 监听过滤条件变化，自动重新计算是否有更多日志
watch([filterLevel, searchKeyword, isReverseOrder], () => {
  hasMoreLogs.value = displayLogs.value.length < filteredLogs.value.length;
});

// 页面加载时检查认证状态
onMounted(() => {
  checkAuth();
});

// 页面卸载时清除定时器
onUnmounted(() => {
  if (logsInterval.value) {
    clearInterval(logsInterval.value);
  }
});

// 跳转到生成页面
const goToGeneratePage = () => {
  window.location.href = '/webui';
};
</script>

<style scoped>
/* 添加模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 400px;
  text-align: center;
}

.modal-content h2 {
  color: #2d3748;
  margin-bottom: 15px;
}

.modal-description {
  color: #718096;
  margin-bottom: 25px;
  text-align: left;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-top: 10px;
  text-align: left;
}

/* 日志头部操作区域 */
.logs-header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.reset-password-btn {
  padding: 6px 12px;
  font-size: 12px;
}

/* 保留原有的样式 */
.admin-container {
  max-width: 1400px;
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

/* 左侧面板 - 包含配置表单 */
.left-panel {
  flex: 1;
  min-width: 320px;
  max-width: 400px;
}

/* 右侧面板 - 包含日志显示 */
.right-panel {
  flex: 2;
  min-width: 480px;
  width: 100%;
}

/* 配置区域样式 */
.config-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group h2 {
  color: #2d3748;
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 1.4rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 10px;
}

/* 表单项样式 */
.form-item {
  margin-bottom: 20px;
}

/* 表单标签样式 */
.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2d3748;
  font-size: 1rem;
  text-align: left;
}

/* 灰白底黑字输入框 */
.gray-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
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

/* 操作按钮容器 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 30px;
}

/* 主要按钮样式 */
.primary-button {
  text-align: center;
  text-decoration: none;
  padding: 14px 24px;
  font-size: 16px;
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
.primary-button:hover:not(:disabled) {
  background-color: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(66, 153, 225, 0.4);
}

/* 次要按钮样式 */
.secondary-button {
  text-align: center;
  text-decoration: none;
  padding: 14px 24px;
  font-size: 16px;
  background-color: #f7fafc;
  color: #2d3748;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.3s;
  min-width: 180px;
  cursor: pointer;
  font-weight: 600;
  display: inline-block;
  width: 100%;
}

/* 次要按钮hover效果 */
.secondary-button:hover:not(:disabled) {
  background-color: #e2e8f0;
  transform: translateY(-2px);
}

/* 禁用状态的按钮 */
.primary-button:disabled,
.secondary-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

/* 日志相关样式 */
.logs-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.logs-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.filter-select {
  min-width: 120px;
}

.filter-input {
  min-width: 200px;
}

.filter-stats {
  margin-left: auto;
  font-size: 14px;
  color: #718096;
}

.logs-container {
  height: 400px;
  overflow: hidden;
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.logs-content {
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}

/* 结构化日志样式 */
.log-entry {
  padding: 8px 12px;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.log-timestamp {
  color: #718096;
  font-family: monospace;
  min-width: 180px;
  font-size: 12px;
}

.log-level {
  font-weight: 600;
  min-width: 60px;
  text-align: center;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.log-content {
  flex: 1;
  min-width: 0;
}

/* 日志级别样式 */
.log-error {
  background-color: #fed7d7;
  border-left: 4px solid #f56565;
}

.log-error .log-level {
  background-color: #f56565;
  color: white;
}

.log-warning {
  background-color: #fffaf0;
  border-left: 4px solid #ed8936;
}

.log-warning .log-level {
  background-color: #ed8936;
  color: white;
}

.log-info {
  background-color: #ebf8ff;
  border-left: 4px solid #4299e1;
}

.log-info .log-level {
  background-color: #4299e1;
  color: white;
}

.log-debug {
  background-color: #f7fafc;
  border-left: 4px solid #a0aec0;
}

.log-debug .log-level {
  background-color: #a0aec0;
  color: white;
}

.log-default {
  background-color: #ffffff;
  border-left: 4px solid #e2e8f0;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 40px;
  color: #718096;
}

.loading-more {
  text-align: center;
  padding: 10px;
  color: #718096;
  font-size: 14px;
}

.no-more-logs {
  text-align: center;
  padding: 10px;
  color: #718096;
  font-size: 14px;
  font-style: italic;
}

.placeholder {
  text-align: center;
  padding: 40px;
  color: #a0aec0;
}

/* Toast消息样式 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 2000;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  background-color: #48bb78;
}

.toast.error {
  background-color: #f56565;
}

.toast.warning {
  background-color: #ed8936;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .left-panel,
  .right-panel {
    min-width: 100%;
  }

  .logs-filter {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    justify-content: space-between;
  }

  .filter-stats {
    margin-left: 0;
    text-align: center;
  }
}

/* 其他原有样式保持不变 */
</style>