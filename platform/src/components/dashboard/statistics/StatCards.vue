<template>
  <div class="statistics-dashboard-container">
    <div class="statistics-dashboard-header">
      <h2 class="statistics-dashboard-title">统计数据</h2>
    </div>
    <div class="statistics-cards-grid">
      <StatCardItem
        icon="user"
        :iconComp="UserIcon"
        :value="totalUserCount"
        trend="up"
        trendValue="+8.2%"
        label="总注册员工数"
        desc="今日新增 12 人"
        :progress="userProgressPercentage"
        iconColor="#667eea"
        progressColor="#667eea"
        :loading="isDataLoading"
      />
      <StatCardItem
        icon="device"
        :iconComp="ServerIcon"
        :value="onlineDeviceCount"
        trend="up"
        trendValue="+2.1%"
        label="在线设备数"
        desc="同比增长"
        :progress="deviceProgressPercentage"
        iconColor="#764ba2"
        progressColor="#764ba2"
        :loading="isDataLoading"
      />
      <StatCardItem
        icon="temp"
        :iconComp="ThermometerIcon"
        :value="currentTemperatureValue"
        trend="down"
        trendValue="-1.3%"
        label="当前温度值"
        desc="较昨日下降"
        :progress="temperatureProgressPercentage"
        iconColor="#f093fb"
        progressColor="#f093fb"
        :loading="isDataLoading"
      />
      <StatCardItem
        icon="fault"
        :iconComp="AlertTriangleIcon"
        :value="faultDeviceCount"
        trend="up"
        trendValue="+0.7%"
        label="故障设备总数"
        desc="需重点关注"
        :progress="faultProgressPercentage"
        iconColor="#ff4d4f"
        progressColor="#ff4d4f"
        danger
        :loading="isDataLoading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { User, Server, Thermometer, AlertTriangle } from 'lucide-vue-next';
import StatCardItem from './StatCardItem.vue';

// 定义组件属性
interface StatisticsProps {
  userCount: number;
  deviceCount: number;
  temperature: number;
  faultCount: number;
  stats?: any[];
  loading?: boolean;
}

const props = withDefaults(defineProps<StatisticsProps>(), {
  userCount: 0,
  deviceCount: 0,
  temperature: 0,
  faultCount: 0,
  loading: false
});

// 响应式数据
const isDataLoading = ref(props.loading);
const refreshInterval = ref<number | null>(null);

// 计算属性 - 优化变量名称
const totalUserCount = computed(() => props.userCount);
const onlineDeviceCount = computed(() => props.deviceCount);
const currentTemperatureValue = computed(() => props.temperature);
const faultDeviceCount = computed(() => props.faultCount);

// 进度百分比计算
const userProgressPercentage = computed(() => Math.min((totalUserCount.value / 100) * 100, 100));
const deviceProgressPercentage = computed(() => Math.min((onlineDeviceCount.value / 50) * 100, 100));
const temperatureProgressPercentage = computed(() => Math.min((currentTemperatureValue.value / 40) * 100, 100));
const faultProgressPercentage = computed(() => Math.min((faultDeviceCount.value / 10) * 100, 100));

// 图标组件别名 - 更清晰的命名
const UserIcon = User;
const ServerIcon = Server;
const ThermometerIcon = Thermometer;
const AlertTriangleIcon = AlertTriangle;

// 自动刷新数据
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    // 这里可以添加实际的数据刷新逻辑
    console.log('统计数据自动刷新中...');
  }, 60000); // 一分钟刷新一次
};

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
    refreshInterval.value = null;
  }
};

// 生命周期
onMounted(() => {
  startAutoRefresh();
});

onUnmounted(() => {
  stopAutoRefresh();
});
</script>

<style scoped>
.statistics-dashboard-container {
  width: 100%;
}
.statistics-dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}
.statistics-dashboard-title{
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.statistics-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-xl);
  width: 100%;
}

/* 响应式容器设计 */
@media (max-width: 1600px) {
  .statistics-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: var(--spacing-lg);
  }
}

@media (max-width: 1400px) {
  .statistics-dashboard-container {
    padding: var(--spacing-md);
  }
  
  .statistics-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--spacing-md);
  }
}

@media (max-width: 1200px) {
  .statistics-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--spacing-sm);
  }
}

@media (max-width: 768px) {
  .statistics-dashboard-container {
    padding: var(--spacing-sm);
  }
  
  .statistics-cards-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .statistics-dashboard-container {
    padding: var(--spacing-xs);
  }
  
  .statistics-cards-grid {
    gap: var(--spacing-sm);
  }
}



/* 加载状态样式 */
.statistics-dashboard-container.loading {
  opacity: 0.7;
  pointer-events: none;
}
</style> 