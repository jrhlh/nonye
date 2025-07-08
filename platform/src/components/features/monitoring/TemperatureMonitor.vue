<template>
  <div class="temperature-monitor">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="header-content">
        <div class="title-section">
          <h3 class="card-title">温度监控</h3>
          <p class="card-subtitle">实时监测环境温度变化</p>
        </div>
      </div>
    </div>

    <!-- 主要内容 - 替换为温湿度趋势图 -->
    <div class="monitor-content">
      <div class="chart-wrapper">
        <div class="header">
          <h2 class="chart-title"></h2>
          <div class="select-group">
            <select v-model="selectedRange" @change="handleRangeChange" class="data-selector">
              <option value="today">今日</option>
              <option value="yesterday">昨日</option>
            </select>
            <select v-model="selectedDevice" @change="handleRangeChange" class="data-selector">
              <option v-for="device in devices" :key="device.id" :value="device.id">
                {{ device.name }}
              </option>
            </select>
          </div>
        </div>
        <div v-if="isLoading" class="loading">
          <i class="fa fa-spinner fa-spin mr-2"></i> Loading...
        </div>
        <div v-else-if="error" class="error">
          <i class="fa fa-exclamation-triangle mr-2"></i> {{ error }}
          <div v-if="errorDetails" class="error-details">{{ errorDetails }}</div>
        </div>
        <div v-else-if="!hasData" class="no-data">
          <i class="fa fa-info-circle mr-2"></i> 所选时间范围或设备无数据
        </div>
        <div ref="chartContainer" v-else class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { RefreshCw } from 'lucide-vue-next';
import axios from 'axios';
import * as echarts from 'echarts';

// 设备信息
const deviceId = ref('TEMP-001');
const lastUpdateTime = ref('刚刚更新');
const isLoading = ref(false);

// 图表相关变量
const chartContainer = ref(null);
const selectedRange = ref('today');
const selectedDevice = ref(1);
const devices = ref([
  { id: 1, name: '设备A' },
  { id: 2, name: '设备B' },
  { id: 3, name: '设备C' },
  { id: 4, name: '设备D' },
  { id: 5, name: '设备E' },
  { id: 6, name: '中心设备' }
]);
const serverData = ref({ temperatureData: [], humidityData: [] });
const error = ref('');
const errorDetails = ref('');
const hasData = ref(true);
let chart: echarts.ECharts | null = null;

// 格式化日期
const formatDate = (date: Date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

// 获取时间范围
const getTimeRange = () => {
  const today = new Date('2025-05-27');
  const yesterday = new Date('2025-05-26');

  return selectedRange.value === 'today' ? [
    `${formatDate(today)} 00:00:00`,
    `${formatDate(today)} 23:59:59`
  ] : [
    `${formatDate(yesterday)} 00:00:00`,
    `${formatDate(yesterday)} 23:59:59`
  ];
};

// 获取数据
const fetchData = async () => {
  isLoading.value = true;
  error.value = '';
  errorDetails.value = '';
  hasData.value = true;

  try {
    const [startTime, endTime] = getTimeRange();
    const response = await axios.get('http://localhost:5000/api/weather/data', {
      params: { start_time: startTime, end_time: endTime }
    });

    if (!response.data.success) throw new Error(response.data.message);

    const deviceData = response.data.data.filter((item: any) => {
      if (item.device_id === 5) {
        return item.temperature !== -999;
      }
      return item.device_id === selectedDevice.value;
    });

    if (deviceData.length === 0) {
      throw new Error(selectedDevice.value === 5 ? '设备离线，无有效数据' : '无有效数据');
    }

    const temperatureData: [number, number | null][] = [];
    const humidityData: [number, number | null][] = [];

    deviceData.forEach((item: any) => {
      const timestamp = new Date(item.timestamp).getTime();

      let temp = parseFloat(item.temperature);
      if (isNaN(temp) || temp < -20 || temp > 50) temp = null;
      else temp = parseFloat(temp.toFixed(1));
      temperatureData.push([timestamp, temp]);

      let hum = parseFloat(item.humidity);
      if (isNaN(hum) || hum < 0 || hum > 100) hum = null;
      else hum = parseFloat(hum.toFixed(1));
      humidityData.push([timestamp, hum]);
    });

    serverData.value = {
      temperatureData,
      humidityData
    };
    await nextTick();
    initChart();

  } catch (err: any) {
    console.error('数据获取失败:', err);
    error.value = err.message || '获取数据失败，请检查网络或时间范围';
    errorDetails.value = err.stack || '';
    hasData.value = false;
    if (chart) chart.dispose();
  } finally {
    isLoading.value = false;
  }
};

// 初始化图表（优化样式）
const initChart = () => {
  if (!chartContainer.value ||
      serverData.value.temperatureData.length === 0 ||
      serverData.value.humidityData.length === 0) return;

  if (chart) chart.dispose();
  chart = echarts.init(chartContainer.value);

  const option = {
    legend: {
      top: 'bottom',
      data: ['温度', '湿度'],
      textStyle: {
        fontSize: 12
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e0e0e0',
      borderWidth: 1,
      padding: 10,
      formatter: (params: any) => {
        // 用 Map 对数据分组，key: 时间 + 系列名，确保同一时间、同一系列只显示一条
        const uniqueParamsMap = new Map();
        params.forEach((item: any) => {
          const date = new Date(item.value[0]);
          const timeKey = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}_${item.seriesName}`;
          if (!uniqueParamsMap.has(timeKey)) {
            uniqueParamsMap.set(timeKey, item);
          }
        });
        // 将 Map 转成数组，按时间排序（可选，保持原顺序也可）
        const uniqueParams = Array.from(uniqueParamsMap.values()).sort((a: any, b: any) => {
          return new Date(a.value[0]).getTime() - new Date(b.value[0]).getTime();
        });
        // 渲染去重后的数据
        return uniqueParams.map((item: any) => {
          const date = new Date(item.value[0]);
          const time = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
          return `
        <div style="margin: 5px 0;">
          <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${item.color}; margin-right: 5px;"></span>
          <span style="font-weight: 500;">${item.seriesName}</span>: ${item.value[1] !== null ? item.value[1] : '无数据'} ${item.seriesIndex === 0 ? '°C' : '%'}
          <div style="color: #999; margin-top: 2px;">${time}</div>
        </div>
      `;
        }).join('');
      }
    },
    dataZoom: [
      {
        type: 'inside',
        throttle: 50,
        xAxisIndex: 0
      }
    ],
    grid: {
      top: 60,
      left: 15,
      right: 15,
      height: 260
    },
    xAxis: {
      type: 'time',
      axisPointer: {
        snap: true,
        lineStyle: {
          color: '#7581BD',
          width: 2
        },
        label: {
          show: true,
          formatter: function (params: any) {
            const date = new Date(params.value);
            return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
          },
          backgroundColor: '#7581BD'
        },
        handle: {
          show: true,
          color: '#7581BD'
        }
      },
      splitLine: {
        show: false
      },
      axisLabel: {
        formatter: function (value: number) {
          const date = new Date(value);
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '温度 ',
        nameTextStyle: {
          color: '#0F73FE',
          fontSize: 12
        },
        axisTick: {
          inside: true
        },
        splitLine: {
          show: false
        },
        axisLabel: {
          inside: true,
          formatter: '{value}\n'
        },
        min: 10,
        max: 40
      },
      {
        type: 'value',
        name: '湿度 ',
        nameTextStyle: {
          color: '#F2597F',
          fontSize: 12
        },
        axisTick: {
          inside: true
        },
        splitLine: {
          show: false
        },
        axisLabel: {
          inside: true,
          formatter: '{value}\n'
        },
        min: 0,
        max: 100
      }
    ],
    series: [
      {
        name: '湿度',
        type: 'line',
        data: serverData.value.humidityData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        itemStyle: {
          color: '#F2597F'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(242, 89, 127, 0.8)' },
            { offset: 1, color: 'rgba(242, 89, 127, 0.1)' }
          ])
        },
        connectNulls: true,
        yAxisIndex: 1,
        // 添加 emphasis 配置，让点击等交互时样式不变
        emphasis: {
          itemStyle: {
            color: '#F2597F' // 和正常状态的 itemStyle.color 一致
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(242, 89, 127, 0.8)' },
              { offset: 1, color: 'rgba(242, 89, 127, 0.1)' }
            ])
          }
        }
      },
      {
        name: '温度',
        type: 'line',
        data: serverData.value.temperatureData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        itemStyle: {
          color: '#0F73FE'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(15, 115, 254, 0.8)' },
            { offset: 1, color: 'rgba(15, 115, 254, 0.1)' }
          ])
        },
        connectNulls: true,
        yAxisIndex: 0,
        // 添加 emphasis 配置，让点击等交互时样式不变
        emphasis: {
          itemStyle: {
            color: '#0F73FE' // 和正常状态的 itemStyle.color 一致
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(15, 115, 254, 0.8)' },
              { offset: 1, color: 'rgba(15, 115, 254, 0.1)' }
            ])
          }
        }
      }
    ]
  };

  chart.setOption(option);
  window.addEventListener('resize', () => chart?.resize());
};

// 刷新数据函数
const refreshData = () => {
  fetchData();
};

// 处理时间范围变化
const handleRangeChange = () => {
  if (chart) chart.dispose();
  fetchData();
};

onMounted(() => {
  fetchData();
});

onBeforeUnmount(() => {
  if (chart) {
    chart.dispose();
    window.removeEventListener('resize', () => chart?.resize());
  }
});

watch([selectedRange, selectedDevice], () => {
  if (chart) chart.dispose();
  fetchData();
});
</script>

<style scoped>
.temperature-monitor {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
  overflow: hidden;

}

.temperature-monitor:hover {
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
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.header-content {
  flex: 1;
}

.title-section {

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
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
  height: calc(100% - 100px);
}

/* 温湿度趋势图样式 */
.chart-wrapper {
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  border-radius: 8px;
  background: var(--bg-card);

}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  margin-bottom: 10px;
}

.chart-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.select-group {
  display: flex;
  gap: 10px;
}

.data-selector {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  width: 100px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.data-selector:hover {
  border-color: #c0c4cc;
}

.data-selector:focus {
  outline: none;
  border-color: #0F73FE;
  box-shadow: 0 0 0 2px rgba(15, 115, 254, 0.2);
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 10px;
  border-radius: 6px;
}

.loading, .error, .no-data {
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  color: #606266;
  background-color: var(--bg-main);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.error {
  color: #f56c6c;
  flex-direction: column;
}

.error-details {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }

  .header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }

  .select-group {
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

  .chart-container {
    height: 300px;
  }
}
</style>