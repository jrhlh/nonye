<template>
  <div class="device-status-card">
    <div class="card-header">
      <div class="header-content">
        <div class="title-section">
          <h3 class="card-title">设备运行状态</h3>
          <p class="card-subtitle">实时监控设备运行情况</p>
        </div>
        <div class="status-badge">
          <div class="status-dot" :class="overallStatus"></div>
          <span class="status-text">{{ statusText }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-refresh" @click="refreshData" :disabled="loading">
          <RefreshCw :size="16" :class="{ 'spinning': loading }" />
        </button>
        <button class="btn-expand" @click="showDetails = !showDetails">
          <ChevronDown :size="16" :class="{ 'rotated': showDetails }" />
        </button>
      </div>
    </div>

    <div class="card-body">
      <!-- 设备状态概览 -->
      <div class="status-overview">
        <div class="overview-item total">
          <div class="overview-icon">
            <Server :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">设备总数</span>
            <span class="overview-value">{{ deviceStats.total }}</span>
          </div>
        </div>
        
        <div class="overview-item online">
          <div class="overview-icon">
            <Wifi :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">在线设备</span>
            <span class="overview-value">{{ deviceStats.online }}</span>
          </div>
        </div>
        
        <div class="overview-item offline">
          <div class="overview-icon">
            <WifiOff :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">离线设备</span>
            <span class="overview-value">{{ deviceStats.offline }}</span>
          </div>
        </div>
        
        <div class="overview-item fault">
          <div class="overview-icon">
            <AlertTriangle :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">故障设备</span>
            <span class="overview-value">{{ deviceStats.fault }}</span>
          </div>
        </div>
      </div>

      <!-- 设备类型分布 -->
      <div class="device-types">
        <h4 class="section-title">设备类型分布</h4>
        <div class="type-grid">
          <div 
            v-for="type in deviceTypes" 
            :key="type.name"
            class="type-item"
            :class="type.status"
          >
            <div class="type-icon">
              <component :is="type.icon" :size="16" />
            </div>
            <div class="type-info">
              <span class="type-name">{{ type.name }}</span>
              <span class="type-count">{{ type.count }}台</span>
            </div>
            <div class="type-status">
              <span class="status-indicator" :class="type.status"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 可展开的详细信息 -->
      <Transition name="slide-down">
        <div v-if="showDetails" class="details-section">
          <div class="details-header">
            <h4>最近故障设备</h4>
            <button class="btn-view-all">查看全部</button>
          </div>
          <div class="fault-list">
            <div 
              v-for="device in faultDevices" 
              :key="device.id"
              class="fault-item"
            >
              <div class="device-info">
                <div class="device-icon">
                  <component :is="device.icon" :size="16" />
                </div>
                <div class="device-details">
                  <h5>{{ device.name }}</h5>
                  <p>{{ device.location }}</p>
                </div>
              </div>
              <div class="fault-info">
                <span class="fault-type">{{ device.faultType }}</span>
                <span class="fault-time">{{ device.faultTime }}</span>
              </div>
              <div class="fault-actions">
                <button class="btn-action">
                  <Eye :size="14" />
                </button>
                <button class="btn-action">
                  <Wrench :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { 
  RefreshCw, 
  ChevronDown, 
  Server, 
  Wifi, 
  WifiOff, 
  AlertTriangle,
  Eye,
  Wrench,
  Thermometer,
  Droplets,
  Camera,
  Zap
} from 'lucide-vue-next';

// 响应式数据
const loading = ref(false);
const showDetails = ref(false);

// 设备统计数据
const deviceStats = ref({
  total: 24,
  online: 22,
  offline: 1,
  fault: 1
});

// 设备类型数据
const deviceTypes = ref([
  { name: '温度传感器', count: 8, status: 'online', icon: Thermometer },
  { name: '湿度传感器', count: 6, status: 'online', icon: Droplets },
  { name: '监控摄像头', count: 4, status: 'online', icon: Camera },
  { name: '控制设备', count: 3, status: 'fault', icon: Zap },
  { name: '数据采集器', count: 3, status: 'offline', icon: Server }
]);

// 故障设备列表
const faultDevices = ref([
  {
    id: 1,
    name: '北田温控器',
    location: '村北农田',
    faultType: '温度异常',
    faultTime: '2小时前',
    icon: Zap
  },
  {
    id: 2,
    name: '东园数据采集器',
    location: '村东果园',
    faultType: '通信中断',
    faultTime: '5小时前',
    icon: Server
  }
]);

// 计算整体状态
const overallStatus = computed(() => {
  const faultRate = deviceStats.value.fault / deviceStats.value.total;
  if (faultRate > 0.1) return 'fault';
  if (deviceStats.value.offline > 0) return 'warning';
  return 'online';
});

const statusText = computed(() => {
  switch (overallStatus.value) {
    case 'fault': return '故障';
    case 'warning': return '异常';
    case 'online': return '正常';
    default: return '未知';
  }
});

// 刷新数据
const refreshData = async () => {
  loading.value = true;
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 更新设备统计数据
    deviceStats.value = {
      total: 24,
      online: Math.floor(Math.random() * 3) + 20,
      offline: Math.floor(Math.random() * 3),
      fault: Math.floor(Math.random() * 2)
    };
    
    // 更新设备类型状态
    deviceTypes.value.forEach(type => {
      const random = Math.random();
      if (random > 0.8) type.status = 'fault';
      else if (random > 0.6) type.status = 'offline';
      else type.status = 'online';
    });
    
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // 组件挂载后的初始化
});
</script>

<style scoped>
.device-status-card {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
  margin-bottom: 20px;
}

.device-status-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 255, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.5);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  flex: 1;
}

.title-section {
  flex: 1;
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: var(--success-color);
}

.status-dot.warning {
  background: var(--warning-color);
}

.status-dot.fault {
  background: var(--error-color);
}

.status-text {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-refresh,
.btn-expand {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-refresh:hover,
.btn-expand:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

.rotated {
  transform: rotate(180deg);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.card-body {
  padding: var(--spacing-2xl);
}

.status-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.overview-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
}

.overview-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.overview-item.total .overview-icon {
  background: var(--gradient-primary);
}

.overview-item.online .overview-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.overview-item.offline .overview-icon {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.overview-item.fault .overview-icon {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.overview-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  color: white;
}

.overview-content {
  display: flex;
  flex-direction: column;
}

.overview-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.overview-value {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.device-types {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-lg) 0;
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--spacing-md);
}

.type-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
}

.type-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-1px);
}

.type-item.online {
  border-left: 3px solid #10b981;
}

.type-item.offline {
  border-left: 3px solid #6b7280;
}

.type-item.fault {
  border-left: 3px solid #ef4444;
}

.type-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.type-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.type-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.type-count {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #10b981;
}

.status-indicator.offline {
  background: #6b7280;
}

.status-indicator.fault {
  background: #ef4444;
}

.details-section {
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-2xl);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.details-header h4 {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.btn-view-all {
  font-size: var(--font-size-sm);
  color: var(--primary-color);
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition-fast);
}

.btn-view-all:hover {
  color: var(--primary-color-dark);
}

.fault-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.fault-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(239, 68, 68, 0.05);
  border-radius: var(--radius-md);
  border: 1px solid rgba(239, 68, 68, 0.1);
}

.device-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
}

.device-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
  color: #ef4444;
}

.device-details h5 {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.device-details p {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0;
}

.fault-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--spacing-xs);
}

.fault-type {
  font-size: var(--font-size-xs);
  color: #ef4444;
  font-weight: 500;
}

.fault-time {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.fault-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-action:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

/* 过渡动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .status-overview {
    grid-template-columns: 1fr;
  }
  
  .type-grid {
    grid-template-columns: 1fr;
  }
  
  .fault-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .fault-info {
    align-items: flex-start;
  }
  
  .fault-actions {
    align-self: flex-end;
  }
}
</style> 