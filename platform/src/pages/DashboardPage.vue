<template>
  <div class="dashboard-page-container">

    <!-- 统计卡片区域 -->
    <div class="statistics-section-container">
      <StatCards 
        :user-count="totalUserCount"
        :device-count="onlineDeviceCount"
        :temperature="currentTemperatureValue"
        :fault-count="faultDeviceCount"
        :stats="statisticsData"
        :loading="isStatisticsLoading"
      />
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content-container">
      <!-- 左侧列 -->
      <div class="left-column-container">
        <!-- 环境监控区域 -->
        <div class="environment-monitoring-section">
          <div class="section-header-container">
            <h2 class="section-title-text">环境监控</h2>
            <span class="section-badge-text">实时</span>
          </div>
          <div class="monitoring-grid-container">
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
        <div class="device-map-section">
          <div class="section-header-container">
            <h2 class="section-title-text">设备地理分布</h2>
            <span class="section-badge-text">地图</span>
          </div>
          <MapSection />
        </div>

        <!-- 生长趋势分析区域 -->
        <div class="growth-analysis-section">
          <div class="section-header-container">
            <h2 class="section-title-text">生长趋势分析</h2>
            <span class="section-badge-text">分析</span>
          </div>
          <GrowthTrendAnalysis />
        </div>
      </div>

      <!-- 右侧列 -->
      <div class="right-column-container">
        <!-- 设备运行状态区域 -->
        <div class="device-status-section">
          <div class="section-header-container">
            <h2 class="section-title-text">设备运行状态</h2>
            <span class="section-badge-text">监控</span>
          </div>
          <DeviceStatusCard />
        </div>

        <!-- 人员管理区域 -->
        <div class="personnel-management-section">
          <div class="section-header-container">
            <h2 class="section-title-text">人员管理</h2>
            <span class="section-badge-text">管理</span>
          </div>
          <PersonnelManagement 
            :current-user="currentUserData"
            @user-created="handleUserCreated"
            @user-updated="handleUserUpdated"
            @user-deleted="handleUserDeleted"
          />
        </div>

        <!-- AI助手区域 -->
        <div class="ai-assistant-section">
          <div class="section-header-container">
            <h2 class="section-title-text">AI智能助手</h2>
            <span class="section-badge-text">AI</span>
          </div>
          <AISection />
        </div>
      </div>
    </div>

    <!-- 通知区域 -->
    <div class="notifications-container" v-if="notificationList.length > 0">
      <div 
        v-for="notification in notificationList" 
        :key="notification.id"
        class="notification-item-container"
        :class="`notification-${notification.type}`"
      >
        <span class="notification-icon-text">{{ notification.icon }}</span>
        <span class="notification-message-text">{{ notification.message }}</span>
        <button 
          class="notification-close-button"
          @click="removeNotification(notification.id)"
        >
          <X :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { RefreshCw, Download, X } from 'lucide-vue-next';
import BaseButton from '../components/ui/BaseButton.vue';
import StatCards from '../components/dashboard/statistics/StatCards.vue';
import TemperatureMonitor from '../components/dashboard/monitoring/TemperatureMonitor.vue';
import HumidityMonitor from '../components/dashboard/monitoring/HumidityMonitor.vue';
import MapSection from '../components/dashboard/visualization/MapSection.vue';
import GrowthTrendAnalysis from '../components/dashboard/visualization/GrowthTrendAnalysis.vue';
import DeviceStatusCard from '../components/dashboard/management/DeviceStatusCard.vue';
import PersonnelManagement from '../components/dashboard/management/PersonnelManagement.vue';
import AISection from '../components/dashboard/ai/AISection.vue';

// 定义接口
interface StatisticData {
  title: string;
  value: string | number;
  change: string;
  trend: 'up' | 'down' | 'stable';
  icon: string;
}

interface NotificationData {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  icon: string;
  timestamp: Date;
}

interface CurrentUserData {
  username: string;
  permissionLevel: string;
}

// 响应式数据 - 优化变量名称
const isRefreshing = ref(false);
const isExporting = ref(false);
const isStatisticsLoading = ref(false);
const notificationList = ref<NotificationData[]>([]);
const refreshInterval = ref<number | null>(null);

// 模拟当前用户数据
const currentUserData: CurrentUserData = {
  username: 'admin001',
  permissionLevel: 'Admin'
};

// 统计数据 - 优化变量名称
const statisticsData = ref<StatisticData[]>([
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

// 计算属性 - 优化变量名称
const totalUserCount = computed(() => 156);
const onlineDeviceCount = computed(() => 22);
const currentTemperatureValue = computed(() => 25.6);
const faultDeviceCount = computed(() => 3);

// 自动刷新功能
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    console.log('仪表板数据自动刷新中...');
    // 这里可以添加实际的数据刷新逻辑
  }, 60000); // 一分钟刷新一次
};

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
    refreshInterval.value = null;
  }
};

// 方法 - 优化变量名称
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

const addNotification = (type: NotificationData['type'], message: string) => {
  const notification: NotificationData = {
    id: Date.now().toString(),
    type,
    message,
    icon: getNotificationIcon(type),
    timestamp: new Date()
  };
  
  notificationList.value.unshift(notification);
  
  // 5秒后自动移除通知
  setTimeout(() => {
    removeNotification(notification.id);
  }, 5000);
};

const removeNotification = (id: string) => {
  notificationList.value = notificationList.value.filter(n => n.id !== id);
};

const getNotificationIcon = (type: NotificationData['type']): string => {
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
  startAutoRefresh();
});

onUnmounted(() => {
  stopAutoRefresh();
});
</script>

<style scoped>
.dashboard-page-container {
  padding: var(--spacing-3xl);
  background: var(--bg-main);
  min-height: 100vh;
  font-family: var(--font-family);
}

/* 页面头部 */
.dashboard-header-container {
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

.header-actions-container {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

/* 统计区域 */
.statistics-section-container {
  margin-bottom: var(--spacing-3xl);
}

/* 主要内容区域 */
.main-content-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-3xl);
}

/* 区域标题 */
.section-header-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.section-title-text {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.section-badge-text {
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
.environment-monitoring-section {
  margin-bottom: var(--spacing-3xl);
}

.monitoring-grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

/* 地图区域 */
.device-map-section {
  margin-bottom: var(--spacing-3xl);
}

/* 生长分析区域 */
.growth-analysis-section {
  margin-bottom: var(--spacing-3xl);
}

/* 设备状态区域 */
.device-status-section {
  margin-bottom: var(--spacing-3xl);
}

/* 人员管理区域 */
.personnel-management-section {
  margin-bottom: var(--spacing-3xl);
}

/* AI助手区域 */
.ai-assistant-section {
  margin-bottom: var(--spacing-3xl);
}

/* 通知区域 */
.notifications-container {
  position: fixed;
  top: var(--spacing-2xl);
  right: var(--spacing-2xl);
  z-index: var(--z-index-modal);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 400px;
}

.notification-item-container {
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

.notification-icon-text {
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

.notification-message-text {
  flex: 1;
  line-height: 1.4;
}

.notification-close-button {
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

.notification-close-button:hover {
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

/* 响应式容器设计 */
@media (max-width: 1600px) {
  .dashboard-page-container {
    padding: var(--spacing-2xl);
  }
  
  .main-content-container {
    gap: var(--spacing-2xl);
  }
  
  .monitoring-grid-container {
    gap: var(--spacing-lg);
  }
}

@media (max-width: 1400px) {
  .dashboard-page-container {
    padding: var(--spacing-xl);
  }
  
  .main-content-container {
    gap: var(--spacing-xl);
  }
  
  .monitoring-grid-container {
    gap: var(--spacing-md);
  }
}

@media (max-width: 1200px) {
  .main-content-container {
    grid-template-columns: 1fr;
    gap: var(--spacing-2xl);
  }
  
  .monitoring-grid-container {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header-container {
    flex-direction: column;
    gap: var(--spacing-xl);
    align-items: stretch;
  }
  
  .header-actions-container {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .dashboard-page-container {
    padding: var(--spacing-lg);
  }
  
  .dashboard-header-container {
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }
  
  .main-content-container {
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }
  
  .environment-monitoring-section,
  .device-map-section,
  .growth-analysis-section,
  .device-status-section,
  .personnel-management-section,
  .ai-assistant-section {
    margin-bottom: var(--spacing-2xl);
  }
  
  .section-title-text {
    font-size: var(--font-size-lg);
  }
  
  .notifications-container {
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    left: var(--spacing-lg);
    max-width: none;
  }
}

@media (max-width: 480px) {
  .dashboard-page-container {
    padding: var(--spacing-md);
  }
  
  .dashboard-header-container {
    padding: var(--spacing-lg);
  }
  
  .header-actions-container {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .monitoring-grid-container {
    gap: var(--spacing-md);
  }
  
  .section-header-container {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
}
</style>