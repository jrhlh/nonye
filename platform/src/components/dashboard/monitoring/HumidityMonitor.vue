<template>
  <div class="humidity-monitor">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="header-content">
        <div class="title-section">
          <h3 class="card-title">湿度监控</h3>
          <p class="card-subtitle">实时监测环境湿度变化</p>
        </div>
        <div class="device-info">
          <span class="device-id">设备: {{ deviceId }}</span>
          <span class="update-time">{{ lastUpdateTime }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button 
          class="action-btn refresh-btn" 
          @click="refreshData"
          :class="{ loading: isLoading }"
          :disabled="isLoading"
        >
          <RefreshCw :size="16" />
          <span>刷新</span>
        </button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="monitor-content">
      <!-- 当前值显示 -->
      <div class="current-value-section">
        <div class="value-display">
          <div class="value-container">
            <span class="value">{{ currentHumidity }}</span>
            <span class="unit">%</span>
          </div>
          <div class="value-label">当前湿度</div>
        </div>
        
        <div class="status-section">
          <div class="status-indicator" :class="statusClass">
            <div class="status-dot"></div>
            <span class="status-text">{{ statusText }}</span>
          </div>
          <div class="threshold-info">
            <span class="threshold-label">阈值:</span>
            <span class="threshold-value">低 {{ threshold.low }}% / 高 {{ threshold.high }}%</span>
          </div>
        </div>
      </div>

      <!-- 进度条区域 -->
      <div class="progress-section">
        <div class="progress-header">
          <h4 class="progress-title">湿度水平</h4>
          <div class="progress-legend">
            <span class="legend-item">
              <span class="legend-dot low"></span>
              <span>过低</span>
            </span>
            <span class="legend-item">
              <span class="legend-dot normal"></span>
              <span>正常</span>
            </span>
            <span class="legend-item">
              <span class="legend-dot high"></span>
              <span>过高</span>
            </span>
          </div>
        </div>
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${humidityPercentage}%` }"
              :class="progressClass"
            ></div>
            <div class="progress-marker" :style="{ left: `${humidityPercentage}%` }">
              <span class="marker-value">{{ currentHumidity }}%</span>
            </div>
          </div>
          <div class="progress-labels">
            <span>0%</span>
            <span>25%</span>
            <span>50%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="chart-section">
        <div class="chart-header">
          <h4 class="chart-title">24小时湿度趋势</h4>
          <div class="chart-stats">
            <div class="stat-item">
              <span class="stat-label">最高</span>
              <span class="stat-value">{{ maxHumidity }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最低</span>
              <span class="stat-value">{{ minHumidity }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均</span>
              <span class="stat-value">{{ avgHumidity }}%</span>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <v-chart 
            class="chart" 
            :option="chartOption" 
            :autoresize="true"
            :loading="isLoading"
          />
        </div>
      </div>

      <!-- 告警列表 -->
      <div class="alerts-section" v-if="alerts.length > 0">
        <div class="alerts-header">
          <h4 class="alerts-title">告警记录</h4>
          <span class="alerts-count">{{ alerts.length }}条</span>
        </div>
        <div class="alerts-list">
          <div 
            v-for="alert in alerts.slice(0, 3)" 
            :key="alert.id" 
            class="alert-item"
            :class="`alert-${alert.level}`"
          >
            <div class="alert-icon">
              <Droplets v-if="alert.level === 'warning'" :size="16" />
              <AlertTriangle v-else-if="alert.level === 'critical'" :size="16" />
              <Info v-else :size="16" />
            </div>
            <div class="alert-content">
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { RefreshCw, Droplets, AlertTriangle, Info } from 'lucide-vue-next';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
} from 'echarts/components';

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
]);

interface HumidityAlert {
  id: string;
  level: 'warning' | 'critical' | 'info';
  message: string;
  timestamp: Date;
  icon: string;
}

interface Props {
  deviceId?: string;
  threshold?: {
    low: number;
    high: number;
  };
}

const props = withDefaults(defineProps<Props>(), {
  deviceId: 'HUM-001',
  threshold: () => ({
    low: 30,
    high: 80
  })
});

const emit = defineEmits<{
  alert: [alert: HumidityAlert];
  dataUpdate: [humidity: number];
}>();

// 响应式数据
const currentHumidity = ref(45);
const isLoading = ref(false);
const alerts = ref<HumidityAlert[]>([]);
const lastUpdateTime = ref('刚刚更新');
const humidityHistory = ref<number[]>([]);
const timeLabels = ref<string[]>([]);

// 计算属性
const humidityPercentage = computed(() => {
  return Math.min(Math.max(currentHumidity.value, 0), 100);
});

const statusClass = computed(() => {
  const humidity = currentHumidity.value;
  if (humidity < props.threshold.low) return 'status-low';
  if (humidity > props.threshold.high) return 'status-high';
  return 'status-normal';
});

const statusText = computed(() => {
  const humidity = currentHumidity.value;
  if (humidity < props.threshold.low) return '湿度过低';
  if (humidity > props.threshold.high) return '湿度过高';
  return '湿度正常';
});

const progressClass = computed(() => {
  const humidity = currentHumidity.value;
  if (humidity < props.threshold.low) return 'progress-low';
  if (humidity > props.threshold.high) return 'progress-high';
  return 'progress-normal';
});

// 计算统计数据
const maxHumidity = computed(() => {
  if (humidityHistory.value.length === 0) return 0;
  return Math.max(...humidityHistory.value);
});

const minHumidity = computed(() => {
  if (humidityHistory.value.length === 0) return 0;
  return Math.min(...humidityHistory.value);
});

const avgHumidity = computed(() => {
  if (humidityHistory.value.length === 0) return 0;
  const sum = humidityHistory.value.reduce((acc, val) => acc + val, 0);
  return Math.round(sum / humidityHistory.value.length);
});

// ECharts 配置
const chartOption = computed(() => {
  const data = humidityHistory.value;
  const times = timeLabels.value;
  
  return {
    title: {
      text: '24小时湿度趋势',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.1)',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      formatter: function(params: any) {
        const data = params[0];
        return `${data.name}<br/>湿度: ${data.value}%`;
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '20%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontSize: 11,
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.06)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '湿度',
        type: 'line',
        data: data,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#4facfe',
          width: 3
        },
        itemStyle: {
          color: '#4facfe',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(79, 172, 254, 0.3)' },
              { offset: 1, color: 'rgba(79, 172, 254, 0.05)' }
            ]
          }
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: {
            color: '#faad14',
            type: 'dashed',
            width: 2
          },
          data: [
            {
              yAxis: props.threshold.low,
              label: {
                show: true,
                position: 'end',
                formatter: '低湿度阈值',
                color: '#faad14',
                fontSize: 11,
                fontWeight: 'bold'
              }
            },
            {
              yAxis: props.threshold.high,
              lineStyle: {
                color: '#ff4d4f'
              },
              label: {
                show: true,
                position: 'end',
                formatter: '高湿度阈值',
                color: '#ff4d4f',
                fontSize: 11,
                fontWeight: 'bold'
              }
            }
          ]
        }
      }
    ]
  };
});

// 方法
const generateRandomHumidity = () => {
  const baseHumidity = 45;
  const variation = Math.random() * 20 - 10;
  return Math.round(Math.max(0, Math.min(100, baseHumidity + variation)));
};

const updateHumidityHistory = (newHumidity: number) => {
  humidityHistory.value.push(newHumidity);
  // 保持24小时的数据点（每5分钟一个数据点，共288个点）
  if (humidityHistory.value.length > 288) {
    humidityHistory.value.shift();
  }
  
  // 更新时间标签
  updateTimeLabels();
};

const updateTimeLabels = () => {
  const labels = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    labels.push(time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }));
  }
  timeLabels.value = labels;
};

const fetchHumidityData = async () => {
  try {
    isLoading.value = true;
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // 生成新的湿度数据
    const newHumidity = generateRandomHumidity();
    
    currentHumidity.value = newHumidity;
    updateHumidityHistory(newHumidity);
    emit('dataUpdate', newHumidity);
    
    // 更新最后更新时间
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
    
    // 检查是否需要生成警报
    checkAlerts(newHumidity);
    
  } catch (error) {
    console.error('获取湿度数据失败:', error);
  } finally {
    isLoading.value = false;
  }
};

const checkAlerts = (humidity: number) => {
  if (humidity < props.threshold.low) {
    const alert: HumidityAlert = {
      id: Date.now().toString(),
      level: 'warning',
      message: `湿度过低: ${humidity}%，建议增加湿度`,
      timestamp: new Date(),
      icon: '💧'
    };
    alerts.value.unshift(alert);
    emit('alert', alert);
  } else if (humidity > props.threshold.high) {
    const alert: HumidityAlert = {
      id: Date.now().toString(),
      level: 'warning',
      message: `湿度过高: ${humidity}%，建议降低湿度`,
      timestamp: new Date(),
      icon: '🌧️'
    };
    alerts.value.unshift(alert);
    emit('alert', alert);
  }
};

const refreshData = () => {
  fetchHumidityData();
};

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 生命周期
onMounted(() => {
  // 初始化历史数据
  for (let i = 0; i < 24; i++) {
    humidityHistory.value.push(generateRandomHumidity());
  }
  updateTimeLabels();
  
  fetchHumidityData();
  
  // 每1秒自动刷新一次
  const interval = setInterval(fetchHumidityData, 1000);
  
  // 清理定时器
  onUnmounted(() => {
    clearInterval(interval);
  });
});

// 监听湿度变化
watch(currentHumidity, (newHumidity) => {
  console.log('湿度更新:', newHumidity);
});
</script>

<style scoped>
.humidity-monitor {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
  overflow: hidden;
}

.humidity-monitor:hover {
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 255, 255, 0.3);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.05) 0%, rgba(82, 196, 26, 0.05) 100%);
}

.header-content {
  flex: 1;
}

.title-section {
  margin-bottom: var(--spacing-sm);
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  letter-spacing: -0.5px;
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

.device-info {
  display: flex;
  gap: var(--spacing-lg);
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.device-id {
  font-weight: 500;
}

.update-time {
  font-weight: 400;
}

.header-actions {
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

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.action-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 主要内容 */
.monitor-content {
  padding: var(--spacing-2xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

/* 当前值显示 */
.current-value-section {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--spacing-2xl);
  align-items: center;
  padding: var(--spacing-2xl);
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: var(--radius-lg);
  color: var(--text-white);
  min-height: 120px;
}

.value-display {
  text-align: center;
}

.value-container {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.value {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -2px;
}

.unit {
  font-size: 1.5rem;
  font-weight: 500;
  opacity: 0.9;
}

.value-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  align-items: flex-end;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-2xl);
  font-size: var(--font-size-sm);
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.threshold-info {
  text-align: right;
  font-size: var(--font-size-xs);
  opacity: 0.8;
}

.threshold-label {
  font-weight: 500;
  margin-right: var(--spacing-xs);
}

.threshold-value {
  font-weight: 400;
}

/* 进度条区域 */
.progress-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.progress-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.progress-legend {
  display: flex;
  gap: var(--spacing-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.low {
  background: var(--warning-color);
}

.legend-dot.normal {
  background: var(--success-color);
}

.legend-dot.high {
  background: var(--error-color);
}

.progress-container {
  position: relative;
}

.progress-bar {
  position: relative;
  height: 12px;
  background: var(--bg-main);
  border-radius: var(--radius-2xl);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-2xl);
  transition: width 0.5s ease;
  position: relative;
}

.progress-fill.progress-low {
  background: linear-gradient(90deg, var(--warning-color) 0%, #ffd591 100%);
}

.progress-fill.progress-normal {
  background: linear-gradient(90deg, var(--success-color) 0%, #95de64 100%);
}

.progress-fill.progress-high {
  background: linear-gradient(90deg, var(--error-color) 0%, #ff7875 100%);
}

.progress-marker {
  position: absolute;
  top: -8px;
  transform: translateX(-50%);
  background: var(--text-white);
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-sm);
  padding: 2px 6px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  transition: left 0.5s ease;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-sm);
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* 图表区域 */
.chart-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.chart-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 500;
}

.stat-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  height: 200px;
  background: var(--bg-main);
  border-radius: var(--radius-md);
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 告警区域 */
.alerts-section {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.alerts-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.alerts-count {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  background: rgba(0, 0, 0, 0.05);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  transition: var(--transition-fast);
}

.alert-item:hover {
  transform: translateX(2px);
}

.alert-warning {
  background: var(--warning-bg);
  border: 1px solid rgba(250, 173, 20, 0.2);
  color: var(--warning-color);
}

.alert-critical {
  background: var(--error-bg);
  border: 1px solid rgba(255, 77, 79, 0.2);
  color: var(--error-color);
}

.alert-info {
  background: var(--info-bg);
  border: 1px solid rgba(24, 144, 255, 0.2);
  color: var(--info-color);
}

.alert-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  line-height: 1.4;
}

.alert-time {
  font-size: var(--font-size-xs);
  opacity: 0.7;
  font-weight: 400;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }
  
  .current-value-section {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
    text-align: center;
  }
  
  .status-section {
    align-items: center;
  }
  
  .progress-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .progress-legend {
    justify-content: center;
  }
  
  .chart-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .chart-stats {
    justify-content: center;
  }
  
  .device-info {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .monitor-content {
    padding: var(--spacing-lg);
    gap: var(--spacing-lg);
  }
  
  .value {
    font-size: 2.5rem;
  }
  
  .unit {
    font-size: 1.2rem;
  }
  
  .chart-stats {
    gap: var(--spacing-md);
  }
  
  .chart-container {
    height: 150px;
  }
}
</style>