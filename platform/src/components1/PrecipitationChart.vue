<template>
  <div class="chart-wrapper">
    <div class="header">
      <h2 class="chart-title">温湿度趋势图</h2>
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
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

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
const isLoading = ref(true);
const error = ref('');
const errorDetails = ref('');
const hasData = ref(true);
let chart = null;

// 格式化日期
const formatDate = (date) => {
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

    const deviceData = response.data.data.filter(item => {
      if (item.device_id === 5) {
        return item.temperature !== -999;
      }
      return item.device_id === selectedDevice.value;
    });

    if (deviceData.length === 0) {
      throw new Error(selectedDevice.value === 5 ? '设备离线，无有效数据' : '无有效数据');
    }

    const temperatureData = [];
    const humidityData = [];

    deviceData.forEach(item => {
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

  } catch (err) {
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
      formatter: (params) => {
        // 用 Map 对数据分组，key: 时间 + 系列名，确保同一时间、同一系列只显示一条
        const uniqueParamsMap = new Map();
        params.forEach(item => {
          const date = new Date(item.value[0]);
          const timeKey = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}_${item.seriesName}`;
          if (!uniqueParamsMap.has(timeKey)) {
            uniqueParamsMap.set(timeKey, item);
          }
        });
        // 将 Map 转成数组，按时间排序（可选，保持原顺序也可）
        const uniqueParams = Array.from(uniqueParamsMap.values()).sort((a, b) => {
          return new Date(a.value[0]).getTime() - new Date(b.value[0]).getTime();
        });
        // 渲染去重后的数据
        return uniqueParams.map(item => {
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
          formatter: function (params) {
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
        formatter: function (value) {
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
  window.addEventListener('resize', () => chart.resize());
};

onMounted(() => {
  fetchData();
});

onBeforeUnmount(() => {
  if (chart) {
    chart.dispose();
    window.removeEventListener('resize', () => chart.resize());
  }
});

watch([selectedRange, selectedDevice], () => {
  if (chart) chart.dispose();
  fetchData();
});

const handleRangeChange = () => {
  if (chart) chart.dispose();
  fetchData();
};
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  height: 100%;
  border-radius: 8px;
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
  color: #333;
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
  background-color: #fff;
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
</style>