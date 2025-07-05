<template>
  <div class="ai-alert-system">
    <!-- 预警统计 -->
    <div class="alert-stats">
      <div class="stat-item">
        <div class="stat-number">{{ totalAlerts }}</div>
        <div class="stat-label">总预警</div>
      </div>
      <div class="stat-item">
        <div class="stat-number pending">{{ pendingAlerts }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="stat-item">
        <div class="stat-number processing">{{ processingAlerts }}</div>
        <div class="stat-label">处理中</div>
      </div>
      <div class="stat-item">
        <div class="stat-number resolved">{{ resolvedAlerts }}</div>
        <div class="stat-label">已解决</div>
      </div>
    </div>

    <!-- 预警列表 -->
    <div class="alert-list">
      <div class="list-header">
        <h3 class="list-title">实时预警</h3>
        <div class="list-actions">
          <button class="action-btn" @click="refreshAlerts">
            <RefreshCw :size="16" />
            <span>刷新</span>
          </button>
        </div>
      </div>
      
      <div class="alerts-container">
        <div 
          v-for="alert in alerts" 
          :key="alert.id" 
          class="alert-card"
          :class="`alert-severity-${alert.severity}`"
          @click="showAlertDetail(alert)"
        >
          <div class="alert-header">
            <div class="severity-badge" :class="severityClass(alert.severity)">
              <div class="severity-dot"></div>
              <span class="severity-text">{{ severityText(alert.severity) }}</span>
            </div>
            <div class="alert-time">{{ formatTime(alert.time) }}</div>
          </div>
          
          <div class="alert-body">
            <div class="alert-type">
              <span class="type-icon">
                <Thermometer v-if="alert.type === '温度'" :size="16" />
                <Droplets v-else-if="alert.type === '土壤湿度'" :size="16" />
                <Zap v-else :size="16" />
              </span>
              <span class="type-text">{{ alert.type }}</span>
            </div>
            
            <div class="alert-values">
              <span class="current-value">{{ alert.currentValue }}</span>
              <span class="separator">/</span>
              <span class="threshold-value">阈值: {{ alert.threshold }}</span>
            </div>
            
            <div class="alert-device">
              <span class="device-label">设备:</span>
              <span class="device-id">{{ alert.deviceId }}</span>
            </div>
          </div>
          
          <div class="alert-footer">
            <div class="status-badge" :class="`status-${getStatusClass(alert.status)}`">
              <div class="status-dot"></div>
              <span class="status-text">{{ alert.status }}</span>
            </div>
            <button class="detail-btn">
              <ChevronRight :size="14" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 预警详情模态框 -->
    <div v-if="showDetail" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title">
            <h3>预警详情</h3>
            <div class="severity-badge" :class="severityClass(currentAlert?.severity || 1)">
              <div class="severity-dot"></div>
              <span class="severity-text">{{ severityText(currentAlert?.severity || 1) }}</span>
            </div>
          </div>
          <button class="close-btn" @click="closeModal">
            <X :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h4 class="section-title">基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">预警类型</span>
                <span class="detail-value">{{ currentAlert?.type }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">设备编号</span>
                <span class="detail-value">{{ currentAlert?.deviceId }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">当前值</span>
                <span class="detail-value">{{ currentAlert?.currentValue }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">阈值</span>
                <span class="detail-value">{{ currentAlert?.threshold }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">状态</span>
                <span class="detail-value status-badge" :class="`status-${getStatusClass(currentAlert?.status || '')}`">
                  {{ currentAlert?.status }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">发生时间</span>
                <span class="detail-value">{{ formatDate(currentAlert?.time || new Date()) }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4 class="section-title">预警分析</h4>
            <div class="analysis-content">
              <div class="analysis-item">
                <span class="analysis-label">预警原因</span>
                <p class="analysis-text">{{ currentAlert?.reason }}</p>
              </div>
              <div class="analysis-item">
                <span class="analysis-label">影响说明</span>
                <p class="analysis-text">{{ currentAlert?.impact }}</p>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4 class="section-title">处理建议</h4>
            <div class="suggestion-content">
              <p class="suggestion-text">{{ currentAlert?.suggestion }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">关闭</button>
          <button 
            class="btn-primary" 
            @click="notifyResponsible"
            :disabled="notifyLoading"
          >
            <Send v-if="!notifyLoading" :size="16" />
            <Loader2 v-else :size="16" class="spinning" />
            <span>{{ notifyLoading ? '发送中...' : '通知负责人' }}</span>
          </button>
        </div>
        
        <div v-if="notifyMessage" class="notify-message" :class="{ success: notifySuccess, error: !notifySuccess }">
          {{ notifyMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  RefreshCw, 
  Thermometer, 
  Droplets, 
  Zap, 
  ChevronRight, 
  X, 
  Send, 
  Loader2 
} from 'lucide-vue-next'

interface Alert {
  id: number
  type: string
  severity: number // 1: 轻微, 2: 中等, 3: 严重
  currentValue: string
  threshold: string
  status: string // '待处理' | '处理中' | '已解决'
  time: Date
  deviceId: string
  reason: string
  impact: string
  suggestion: string
}

// 预警数据
const alerts = ref<Alert[]>([
  {
    id: 1,
    type: '土壤湿度',
    severity: 3,
    currentValue: '91%',
    threshold: '75%',
    status: '待处理',
    time: new Date(),
    deviceId: 'DEV-2023-001',
    reason: '土壤湿度过高，可能导致植物根部腐烂',
    impact: '影响植物正常生长，可能导致作物减产',
    suggestion: '1. 立即停止灌溉系统运行，检查灌溉设备阀门是否完全关闭\n2. 检查排水泵是否正常工作，清理排水管道堵塞物\n3. 启用土壤湿度监测设备，每30分钟记录一次数据'
  },
  {
    id: 2,
    type: '温度',
    severity: 2,
    currentValue: '30°C',
    threshold: '28°C',
    status: '已解决',
    time: new Date('2025-05-27 14:30'),
    deviceId: 'DEV-2023-002',
    reason: '环境温度超过阈值',
    impact: '高温可能影响设备性能和作物生长',
    suggestion: '1. 检查温度传感器是否正常工作，清洁传感器表面\n2. 开启智能通风系统，设置为自动模式\n3. 检查温控设备制冷模块，确认压缩机工作状态'
  },
  {
    id: 3,
    type: '温度',
    severity: 1,
    currentValue: '32°C',
    threshold: '28°C',
    status: '处理中',
    time: new Date(new Date().setDate(new Date().getDate() - 1)),
    deviceId: 'DEV-2023-003',
    reason: '温度略高于设定阈值',
    impact: '轻微影响，需关注温度变化趋势',
    suggestion: '1. 检查温度传感器校准状态，对比相邻设备数据\n2. 检查温控设备风扇是否正常运转，清理散热孔\n3. 调整智能遮阳设备角度，减少阳光直射'
  }
])

// 弹窗相关状态
const showDetail = ref(false)
const currentAlert = ref<Alert | null>(null)
const notifyLoading = ref(false)
const notifyMessage = ref('')
const notifySuccess = ref(false)

// 计算属性
const totalAlerts = computed(() => alerts.value.length)
const pendingAlerts = computed(() => alerts.value.filter(a => a.status === '待处理').length)
const processingAlerts = computed(() => alerts.value.filter(a => a.status === '处理中').length)
const resolvedAlerts = computed(() => alerts.value.filter(a => a.status === '已解决').length)

// 格式化时间
const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const formatDate = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 根据严重程度返回对应的样式类
const severityClass = (severity: number) => {
  switch (severity) {
    case 1: return 'severity-low'
    case 2: return 'severity-medium'
    case 3: return 'severity-high'
    default: return 'severity-low'
  }
}

// 根据严重程度返回对应的文本
const severityText = (severity: number) => {
  switch (severity) {
    case 1: return '轻微'
    case 2: return '中等'
    case 3: return '严重'
    default: return '轻微'
  }
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  switch (status) {
    case '已解决': return 'resolved'
    case '处理中': return 'processing'
    case '待处理': return 'pending'
    default: return 'pending'
  }
}

// 显示预警详情
const showAlertDetail = (alert: Alert) => {
  currentAlert.value = alert
  showDetail.value = true
  notifyMessage.value = ''
}

// 关闭弹窗
const closeModal = () => {
  showDetail.value = false
  currentAlert.value = null
}

// 刷新预警列表
const refreshAlerts = () => {
  // 模拟刷新数据
  console.log('刷新预警数据')
}

// 通知负责人
const notifyResponsible = async () => {
  if (!currentAlert.value) return

  notifyLoading.value = true
  notifyMessage.value = ''

  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    notifyMessage.value = '通知已成功发送给负责人'
    notifySuccess.value = true
    
    // 3秒后清除消息
    setTimeout(() => {
      notifyMessage.value = ''
    }, 3000)
    
  } catch (error) {
    notifyMessage.value = '通知发送失败，请重试'
    notifySuccess.value = false
  } finally {
    notifyLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始化逻辑
})

onUnmounted(() => {
  // 清理逻辑
})
</script>

<style scoped>
.ai-alert-system {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  height: 100%;
}

/* 预警统计 */
.alert-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.5);
  transition: var(--transition-fast);
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.stat-number {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
}

.stat-number.pending {
  color: var(--error-color);
}

.stat-number.processing {
  color: var(--warning-color);
}

.stat-number.resolved {
  color: var(--success-color);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 预警列表 */
.alert-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.5);
}

.list-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.list-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

/* 预警卡片 */
.alerts-container {
  flex: 1;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  overflow-y: auto;
}

.alert-card {
  background: var(--bg-main);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: var(--transition-base);
  position: relative;
  overflow: hidden;
}

.alert-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--warning-color);
  transition: var(--transition-fast);
}

.alert-card.alert-severity-1::before {
  background: var(--warning-color);
}

.alert-card.alert-severity-2::before {
  background: var(--error-color);
}

.alert-card.alert-severity-3::before {
  background: #ff1744;
}

.alert-card:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.severity-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-2xl);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.severity-badge.severity-low {
  background: rgba(250, 173, 20, 0.1);
  color: var(--warning-color);
}

.severity-badge.severity-medium {
  background: rgba(255, 77, 79, 0.1);
  color: var(--error-color);
}

.severity-badge.severity-high {
  background: rgba(255, 23, 68, 0.1);
  color: #ff1744;
}

.severity-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.severity-text {
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.alert-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.alert-body {
  margin-bottom: var(--spacing-md);
}

.alert-type {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.type-icon {
  color: var(--primary-color);
}

.type-text {
  font-weight: 600;
  color: var(--text-primary);
}

.alert-values {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.current-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.separator {
  color: var(--text-tertiary);
}

.threshold-value {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.alert-device {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.device-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.device-id {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
}

.alert-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-2xl);
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.status-badge.status-pending {
  background: rgba(255, 77, 79, 0.1);
  color: var(--error-color);
}

.status-badge.status-processing {
  background: rgba(250, 173, 20, 0.1);
  color: var(--warning-color);
}

.status-badge.status-resolved {
  background: rgba(82, 196, 26, 0.1);
  color: var(--success-color);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.detail-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.05);
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.detail-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-primary);
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal);
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 600px;
  width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.modal-title h3 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.05);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  padding: var(--spacing-2xl);
  overflow-y: auto;
}

.detail-section {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-lg) 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.detail-label {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  font-weight: 500;
}

.detail-value {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.analysis-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.analysis-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

.analysis-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
}

.suggestion-content {
  background: rgba(24, 144, 255, 0.05);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid rgba(24, 144, 255, 0.1);
}

.suggestion-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
  white-space: pre-line;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: var(--gradient-primary);
  border: none;
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--text-white);
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}

.btn-primary:hover:not(:disabled) {
  background: var(--gradient-primary-hover);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

.notify-message {
  position: absolute;
  bottom: var(--spacing-lg);
  left: 50%;
  transform: translateX(-50%);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  font-weight: 500;
  animation: slideUp 0.3s ease;
}

.notify-message.success {
  background: rgba(82, 196, 26, 0.1);
  color: var(--success-color);
  border: 1px solid rgba(82, 196, 26, 0.2);
}

.notify-message.error {
  background: rgba(255, 77, 79, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(255, 77, 79, 0.2);
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .alert-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
  }
  
  .stat-number {
    font-size: var(--font-size-xl);
  }
  
  .list-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .modal-content {
    width: 95vw;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: var(--spacing-lg) var(--spacing-xl);
  }
  
  .modal-body {
    padding: var(--spacing-xl);
  }
  
  .modal-footer {
    padding: var(--spacing-lg) var(--spacing-xl);
  }
}

@media (max-width: 480px) {
  .alert-stats {
    grid-template-columns: 1fr;
  }
  
  .alert-card {
    padding: var(--spacing-md);
  }
  
  .alert-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
  }
  
  .alert-footer {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
  }
}
</style>