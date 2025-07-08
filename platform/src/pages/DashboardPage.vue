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
      <!-- 环境监控区域 - 左列（1份） -->
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
        </div>
      </div>

      <!-- 设备运行状态区域 - 右列（1份） -->
      <div class="device-status-section">
        <div class="section-header">
          <h2 class="section-title">设备运行状态</h2>
          <span class="section-badge">监控</span>
        </div>
        <DeviceStatusCard />
      </div>

      <!-- 地图区域 - 跨两列 -->
      <div class="map-section">
        <div class="section-header">
          <h2 class="section-title">设备地理分布</h2>
          <span class="section-badge">地图</span>
        </div>
        <div class="under">
          <iframe
              src="/map_with_random_points.html"
              width="100%"
              height="100%"
          ></iframe>
        </div>
      </div>

      <!-- 2:3比例区域容器 -->
      <div class="ratio-section">
        <!-- AI预警系统区域 - 占2份 -->
        <div class="growth-section">
          <div class="section-header">
            <h2 class="section-title">AI预警系统</h2>
            <span class="section-badge">分析</span>
          </div>
          <div class="body-foot">
            <div class="body-under-box">
              <div class="box002">
                <AIyujing />
              </div>
            </div>
          </div>
        </div>

        <!-- 生长趋势分析区域 - 占3份 -->
        <div class="personnel-section">
          <div class="section-header">
            <h2 class="section-title">生长趋势分析</h2>
            <span class="section-badge">分析</span>
          </div>
          <div class="xx">
            <Shengzhang />
          </div>
        </div>
      </div>
    </div>
    <div>
      <!-- 你的页面内容 -->
      <askai />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AIyujing from "./AIyujing.vue";
import Shengzhang from "./shengzhang.vue";
import StatCards from '../components/dashboard/StatCards.vue';
import TemperatureMonitor from '../components/features/monitoring/TemperatureMonitor.vue';
import DeviceStatusCard from '../components/features/devices/DeviceStatusCard.vue';
import Askai from "../components1/askai.vue";

// 类型定义
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

// 方法：刷新所有数据
const refreshAllData = async () => {
  isRefreshing.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 2000));
    addNotification('success', '数据刷新成功');
  } catch (error) {
    addNotification('error', '数据刷新失败');
  } finally {
    isRefreshing.value = false;
  }
};

// 方法：导出报告
const exportReport = async () => {
  isExporting.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 3000));
    addNotification('success', '报告导出成功');
  } catch (error) {
    addNotification('error', '报告导出失败');
  } finally {
    isExporting.value = false;
  }
};

// 处理温度告警
const handleTemperatureAlert = (alert: any) => {
  addNotification('warning', `温度告警: ${alert.message}`);
};

// 处理湿度告警
const handleHumidityAlert = (alert: any) => {
  addNotification('warning', `湿度告警: ${alert.message}`);
};

// 处理温度更新
const handleTemperatureUpdate = (temperature: number) => {
  console.log('温度更新:', temperature);
};

// 处理湿度更新
const handleHumidityUpdate = (humidity: number) => {
  console.log('湿度更新:', humidity);
};

// 处理用户创建
const handleUserCreated = (user: any) => {
  addNotification('success', `用户 ${user.username} 创建成功`);
};

// 处理用户更新
const handleUserUpdated = (user: any) => {
  addNotification('success', `用户 ${user.username} 更新成功`);
};

// 处理用户删除
const handleUserDeleted = (username: string) => {
  addNotification('info', `用户 ${username} 已删除`);
};

// 添加通知
const addNotification = (type: Notification['type'], message: string) => {
  const notification: Notification = {
    id: Date.now().toString(),
    type,
    message,
    icon: getNotificationIcon(type),
    timestamp: new Date()
  };
  notifications.value.unshift(notification);

  // 5秒后自动移除
  setTimeout(() => {
    removeNotification(notification.id);
  }, 5000);
};

// 移除通知
const removeNotification = (id: string) => {
  notifications.value = notifications.value.filter(n => n.id !== id);
};

// 获取通知图标
const getNotificationIcon = (type: Notification['type']): string => {
  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️'
  };
  return icons[type];
};

// 生命周期：挂载时
onMounted(() => {
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

/* 统计区域 */
.stats-section {
  margin-bottom: var(--spacing-3xl);
  padding-left: 5px;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 环境监控和设备状态1:1 */
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-3xl);
  padding-left: 6px;
}

/* 2:3比例区域容器 */
.ratio-section {
  grid-column: 1 / -1; /* 跨两列 */
  display: grid;
  grid-template-columns: 2fr 3fr; /* AI预警和生长趋势2:3 */
  gap: var(--spacing-3xl);
}

/* 地图区域 */
.map-section {
  grid-column: 1 / -1; /* 跨两列 */
  margin-bottom: var(--spacing-3xl);
  margin-top: -40px;
}

/* 环境监控和设备状态区域 */
.monitoring-section,
.device-status-section {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: var(--spacing-2xl);
}

/* AI预警和生长趋势区域 */
.growth-section,
.personnel-section {
  margin-bottom: 0;
  grid-column: auto;
  margin-top: -20px;
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

/* 生长趋势容器 */
.xx {
  background-color: #FFFFFF;
  padding: 20px 20px;
  text-align: center;
  background: var(--bg-card-hover);
  border-radius: 15px;
  box-shadow: var(--shadow-md);
  box-sizing: border-box;
}

/* 区域徽章 */
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

/* 地图容器 */
.under {
  width: 100%;
  height: 635px;
  background-color: #FFFFFF;
  padding: 22px 22px;
  text-align: center;
  background: var(--bg-card-hover);
  border-radius: 14px;
  box-shadow: var(--shadow-md);
  box-sizing: border-box;
}

/* 监控区域网格 */
.monitoring-grid {
  display: grid;
  gap: var(--spacing-xl);
}

/* AI预警容器 */
.body-foot {
  width: 100%;
  height: 560px;
  margin-top: 21.5px;
  display: flex;
  gap: 20px;
  background: var(--bg-card-hover);
  border-radius: 15px;
  box-shadow: var(--shadow-md);
}

.body-under-box {
  flex: 1;
}

.box002 {
  width: 100%;
  height: 572px;
  background-color: #FFFFFF;

  background: var(--bg-card-hover);
  border-radius: 15px;
  box-shadow: var(--shadow-md);
  box-sizing: border-box;
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
@media (max-width: 1200px) {
  .main-content,
  .ratio-section {
    grid-template-columns: 1fr; /* 小屏幕单列 */
    gap: var(--spacing-2xl);
  }

  .map-section,
  .monitoring-section,
  .growth-section,
  .device-status-section,
  .personnel-section,
  .ratio-section {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacing-lg);
  }

  .main-content {
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }

  .section-title {
    font-size: var(--font-size-lg);
  }
}

@media (max-width: 480px) {
  .dashboard-page {
    padding: var(--spacing-md);
  }

  .monitoring-grid {
    gap: var(--spacing-md);
  }
}
</style>