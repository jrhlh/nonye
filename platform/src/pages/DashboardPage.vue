<template>
  <div class="dashboard-page">

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <StatCards 
        :user-count="0"
        :device-count="0"
        :temperature="0"
        :fault-count="0"
        :stats="statistics"
        :loading="isStatsLoading"
      />
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧列 -->
      <div class="left-column">
        <!-- 环境监控区域 -->
        <div class="monitoring-section">
          <div class="section-header">
            <h2 class="section-title">环境监控</h2>
            <span class="section-badge">实时</span>
          </div>
          <div class="monitoring-grid">
            <TemperatureMonitor 
              :device-id="'temp-001'"
              :threshold="{ warning: 30, critical: 35 }"
              @alert="handleTemperatureAlert"
              @data-update="handleTemperatureUpdate"
            />
            <HumidityMonitor 
              :device-id="'humidity-001'"
              :threshold="{ low: 30, high: 80 }"
              @alert="handleHumidityAlert"
              @data-update="handleHumidityUpdate"
            />
          </div>
        </div>

        <!-- 设备地图区域 -->
        <div class="map-section">
          <div class="section-header">
            <h2 class="section-title">设备地理分布</h2>
            <span class="section-badge">地图</span>
          </div>
          <MapSection />
        </div>

        <!-- 生长趋势分析区域 -->
        <div class="growth-section">
          <div class="section-header">
            <h2 class="section-title">生长趋势分析</h2>
            <span class="section-badge">分析</span>
          </div>
          <GrowthTrendAnalysis />
        </div>
      </div>

      <!-- 右侧列 -->
      <div class="right-column">
        <!-- 设备运行状态区域 -->
        <div class="device-status-section">
          <div class="section-header">
            <h2 class="section-title">设备运行状态</h2>
            <span class="section-badge">监控</span>
          </div>
          <DeviceStatusCard />
        </div>

        <!-- 人员管理区域 -->
        <div class="personnel-section">
          <div class="section-header">
            <h2 class="section-title">人员管理</h2>
            <span class="section-badge">管理</span>
          </div>
          <PersonnelManagement 
            :current-user="currentUser"
            @user-created="handleUserCreated"
            @user-updated="handleUserUpdated"
            @user-deleted="handleUserDeleted"
          />
        </div>

        <!-- AI助手区域 -->
        <div class="ai-section">
          <div class="section-header">
            <h2 class="section-title">AI智能助手</h2>
            <span class="section-badge">AI</span>
          </div>
          <AISection />
        </div>
      </div>
    </div>

    <!-- 通知区域 -->
    <div class="notifications" v-if="notifications.length > 0">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="notification-item"
        :class="`notification-${notification.type}`"
      >
        <span class="notification-icon">{{ notification.icon }}</span>
        <span class="notification-message">{{ notification.message }}</span>
        <button 
          class="notification-close"
          @click="removeNotification(notification.id)"
        >
          <X :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RefreshCw, Download, X } from 'lucide-vue-next';
import BaseButton from '../components/ui/BaseButton.vue';
import StatCards from '../components/dashboard/StatCards.vue';
import TemperatureMonitor from '../components/features/monitoring/TemperatureMonitor.vue';
import HumidityMonitor from '../components/features/monitoring/HumidityMonitor.vue';
import MapSection from '../components/dashboard/MapSection.vue';
import GrowthTrendAnalysis from '../components/features/analysis/GrowthTrendAnalysis.vue';
import DeviceStatusCard from '../components/features/devices/DeviceStatusCard.vue';
import PersonnelManagement from '../components/features/personnel/PersonnelManagement.vue';
import AISection from '../components/dashboard/AISection.vue';

interface Statistic {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'stable';
  icon: string;
}

interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  icon: string;
  timestamp: Date;
}

interface CurrentUser {
  username: string;
  permissionLevel: string;
}

// 响应式数据
const isRefreshing = ref(false);
const isExporting = ref(false);
const isStatsLoading = ref(false);
const notifications = ref<Notification[]>([]);

// 模拟当前用户
const currentUser: CurrentUser = {
  username: 'admin001',
  permissionLevel: 'Admin'
};

// 统计数据
const statistics = ref<Statistic[]>([
  {
    title: '设备总数',
    value: 24,
    change: '+12%',
    trend: 'up',
    icon: '📱'
  },
  {
    title: '在线设备',
    value: 22,
    change: '+8%',
    trend: 'up',
    icon: '🟢'
  },
  {
    title: '告警数量',
    value: 3,
    change: '-2',
    trend: 'down',
    icon: '⚠️'
  },
  {
    title: '数据采集',
    value: '2.4K',
    change: '+15%',
    trend: 'up',
    icon: '📊'
  }
]);

// 方法
const refreshAllData = async () => {
  isRefreshing.value = true;
  try {
    // 模拟刷新所有数据
    await new Promise(resolve => setTimeout(resolve, 2000));
    addNotification('success', '数据刷新成功');
  } catch (error) {
    addNotification('error', '数据刷新失败');
  } finally {
    isRefreshing.value = false;
  }
};

const exportReport = async () => {
  isExporting.value = true;
  try {
    // 模拟导出报告
    await new Promise(resolve => setTimeout(resolve, 3000));
    addNotification('success', '报告导出成功');
  } catch (error) {
    addNotification('error', '报告导出失败');
  } finally {
    isExporting.value = false;
  }
};

const handleTemperatureAlert = (alert: any) => {
  addNotification('warning', `温度告警: ${alert.message}`);
};

const handleHumidityAlert = (alert: any) => {
  addNotification('warning', `湿度告警: ${alert.message}`);
};

const handleTemperatureUpdate = (temperature: number) => {
  // 更新统计数据
  console.log('温度更新:', temperature);
};

const handleHumidityUpdate = (humidity: number) => {
  // 更新统计数据
  console.log('湿度更新:', humidity);
};

const handleUserCreated = (user: any) => {
  addNotification('success', `用户 ${user.username} 创建成功`);
};

const handleUserUpdated = (user: any) => {
  addNotification('success', `用户 ${user.username} 更新成功`);
};

const handleUserDeleted = (username: string) => {
  addNotification('info', `用户 ${username} 已删除`);
};

const addNotification = (type: Notification['type'], message: string) => {
  const notification: Notification = {
    id: Date.now().toString(),
    type,
    message,
    icon: getNotificationIcon(type),
    timestamp: new Date()
  };
  
  notifications.value.unshift(notification);
  
  // 5秒后自动移除通知
  setTimeout(() => {
    removeNotification(notification.id);
  }, 5000);
};

const removeNotification = (id: string) => {
  notifications.value = notifications.value.filter(n => n.id !== id);
};

const getNotificationIcon = (type: Notification['type']): string => {
  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️'
  };
  return icons[type];
};

// 生命周期
onMounted(() => {
  // 初始化数据
  console.log('仪表板页面已加载');
});
</script>

<style scoped>
.dashboard-page {
  padding: var(--spacing-3xl);
  background: var(--bg-main);
  min-height: 100vh;
  font-family: var(--font-family);
}

/* 页面头部 */
.dashboard-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: var(--spacing-3xl);
  padding: var(--spacing-2xl);
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-card);
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

/* 统计区域 */
.stats-section {
  margin-bottom: var(--spacing-3xl);
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-3xl);
}

/* 区域标题 */
.section-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.section-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--gradient-primary);
  color: var(--text-white);
  border-radius: var(--radius-2xl);
  font-size: var(--font-size-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 监控区域 */
.monitoring-section {
  margin-bottom: var(--spacing-3xl);
}

.monitoring-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

/* 地图区域 */
.map-section {
  margin-bottom: var(--spacing-3xl);
}

/* 人员管理区域 */
.personnel-section {
  margin-bottom: var(--spacing-3xl);
}

/* AI助手区域 */
.ai-section {
  margin-bottom: var(--spacing-3xl);
}

/* 通知区域 */
.notifications {
  position: fixed;
  top: var(--spacing-2xl);
  right: var(--spacing-2xl);
  z-index: var(--z-index-modal);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 400px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-radius: var(--radius-lg);
  color: var(--text-white);
  font-size: var(--font-size-sm);
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.notification-success {
  background: linear-gradient(135deg, var(--success-color) 0%, #73d13d 100%);
}

.notification-warning {
  background: linear-gradient(135deg, var(--warning-color) 0%, #ffc53d 100%);
}

.notification-error {
  background: linear-gradient(135deg, var(--error-color) 0%, #ff7875 100%);
}

.notification-info {
  background: linear-gradient(135deg, var(--info-color) 0%, #40a9ff 100%);
}

.notification-icon {
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.notification-message {
  flex: 1;
  line-height: 1.4;
}

.notification-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: var(--text-white);
  cursor: pointer;
  padding: var(--spacing-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.notification-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

@keyframes slideIn {
  from {
    transform: translateX(100%) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateX(0) scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .dashboard-page {
    padding: var(--spacing-2xl);
  }
  
  .main-content {
    gap: var(--spacing-2xl);
  }
  
  .monitoring-grid {
    gap: var(--spacing-lg);
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-2xl);
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: var(--spacing-xl);
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacing-lg);
  }
  
  .dashboard-header {
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }
  
  .main-content {
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }
  
  .monitoring-section,
  .map-section,
  .personnel-section,
  .ai-section {
    margin-bottom: var(--spacing-2xl);
  }
  
  .section-title {
    font-size: var(--font-size-lg);
  }
  
  .notifications {
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    left: var(--spacing-lg);
    max-width: none;
  }
}

@media (max-width: 480px) {
  .dashboard-page {
    padding: var(--spacing-md);
  }
  
  .dashboard-header {
    padding: var(--spacing-lg);
  }
  
  .header-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .monitoring-grid {
    gap: var(--spacing-md);
  }
}
</style>