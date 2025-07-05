<template>
  <div class="chart-container">
    <div class="device-selector">
      <select id="device-select" v-model="selectedDeviceId" @change="initChartData">
        <option v-for="(name, id) in deviceList" :key="id" :value="id">
          {{ name }}
        </option>
      </select>
    </div>

    <div ref="chartRef" style="width: 100%; height: 600px; margin-top: 80px"></div>

    <div v-if="loading" class="status loading">加载中...</div>
    <div v-if="error" class="status error">数据加载失败: {{ error }}</div>
    <div v-if="!loading && !error && !hasData" class="status no-data">无传感器数据</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

interface SensorData {
  time: string;
  temperature: number;
}

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;
const loading = ref(false);
const error = ref<string | null>(null);
const deviceList = ref<Record<string, string>>({});
const selectedDeviceId = ref<string>('');
const hasData = ref(false);

const chartData = ref<{
  times: string[];
  actualTemps: (number | null)[];
  predictionTemps: (number | null)[];
}>();

// 更新间隔
const DATA_UPDATE_INTERVAL = 5000; // 5秒更新一次数据
let dataUpdateTimer: number | null = null;
let timeUpdateTimer: number | null = null;

// 初始时间序列（从9:00开始，每20分钟一个间隔）
const initialTimes = [
  '09:00', '09:20', '09:40', '10:00',
  '10:20', '10:40', '11:00', '11:20'
];

// 当前显示的时间序列
const currentTimes = ref<string[]>([...initialTimes]);

// 获取下一个时间点（增加20分钟）
const getNextTime = (timeStr: string) => {
  const [hours, minutes] = timeStr.split(':').map(Number);
  let newHours = hours;
  let newMinutes = minutes + 20;

  if (newMinutes >= 60) {
    newHours += Math.floor(newMinutes / 60);
    newMinutes = newMinutes % 60;
  }

  return `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
};

// 更新时间序列（平滑过渡）
const updateTimeSeries = () => {
  if (!chart) return;

  // 使用动画更新x轴数据
  chart.setOption({
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    xAxis: {
      data: currentTimes.value.map(time => getNextTime(time))
    }
  });

  // 更新当前时间序列
  currentTimes.value = currentTimes.value.map(time => getNextTime(time));
};

// 获取当前时间（对齐到最近的20分钟）
const getCurrentTime = () => {
  const now = new Date();
  const minutes = now.getMinutes();
  const alignedMinutes = Math.floor(minutes / 20) * 20;
  const currentTime = new Date(now);
  currentTime.setMinutes(alignedMinutes, 0, 0);
  return currentTime;
};

// 从后端获取设备列表
const fetchDevices = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/chou1/devices');
    if (response.data.code === 200) {
      return response.data.data;
    }
    throw new Error(response.data.message || '获取设备列表失败');
  } catch (err) {
    console.error('获取设备列表失败:', err);
    error.value = err instanceof Error ? err.message : '获取设备列表失败';
    return {};
  }
};

// 从后端获取最新的实际传感器数据（只获取最后一个点）
const fetchLatestActualSensorData = async (deviceId: string) => {
  try {
    loading.value = true;
    error.value = null;
    hasData.value = false;

    const response = await axios.get(
        `http://localhost:5000/api/sensor/device/${deviceId}/latest`
    );

    if (response.data.code === 200) {
      if (response.data.data) {
        hasData.value = true;
        return response.data.data as SensorData;
      } else {
        return null;
      }
    } else {
      error.value = response.data.message || '获取传感器数据失败';
      return null;
    }
  } catch (err) {
    console.error('获取传感器数据失败:', err);
    error.value = err instanceof Error ? err.message : '获取传感器数据失败';
    return null;
  } finally {
    loading.value = false;
  }
};

// 从后端获取最新的温度预测数据（只获取最后一个点）
const fetchLatestTemperaturePrediction = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/prediction/temperature/latest');

    if (response.data.code === 200) {
      return response.data.data as number;
    }
    throw new Error(response.data.message || '获取预测数据失败');
  } catch (err) {
    console.error('获取预测数据失败:', err);
    // 生成模拟预测数据
    return 25 + (Math.random() * 2 - 1); // 24-26之间的随机值
  }
};

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;

  if (chart) {
    chart.dispose();
    chart = null;
  }

  chart = echarts.init(chartRef.value);

  // 定义共享的渐变配置
  const actualAreaGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: 'rgba(164, 203, 234, 0.8)' },
    { offset: 1, color: 'rgba(219, 235, 250, 0.1)' }
  ]);

  const option = {
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const time = params[0].axisValue;
        const value = params[0].value;
        const isPrediction = params[0].dataIndex >= 4; // 前4个是实际数据，后4个是预测数据
        const prefix = isPrediction ? '预测' : '实际';
        return `${time}<br/>${prefix}温度: ${value?.toFixed(1) ?? '--'}°C`;
      }
    },
    legend: {
      data: ['实际数据', '预测数据'],
      right: '10%',
      top: '5%',
    },
    grid: {
      left: '2%',
      right: '4%',
      bottom: '0%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: currentTimes.value,
      axisLabel: {
        formatter: (value: string) => value,
        rotate: 45,
      },
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicOut'
    },
    yAxis: {
      type: 'value',
      min: 15,
      max: 35,
      axisLabel: {
        formatter: '{value} °C',
      },
    },
    series: [
      {
        name: '实际数据',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: [],
        itemStyle: { color: '#24a4fa' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: actualAreaGradient
        },
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '预测数据',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: [],
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 3, type: 'dashed' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.5)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.1)' },
          ]),
        },
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        // 连接线系列
        name: '连接线',
        type: 'line',
        symbol: 'none',
        data: [],
        lineStyle: {
          width: 3,
          color: '#24a4fa'
        },
        areaStyle: {
          color: actualAreaGradient
        },
        silent: true,
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      }
    ],
  };

  chart.setOption(option);
};

// 更新图表数据
const updateChartData = (newActualTemp?: number, newPredictionTemp?: number) => {
  if (!chart || !chartData.value) return;

  if (newActualTemp !== undefined) {
    // 更新实际数据（保留前3个历史数据点）
    chartData.value.actualTemps = [
      ...chartData.value.actualTemps.slice(1), // 移除第一个历史点
      newActualTemp // 添加新的实际数据点
    ];
  }

  if (newPredictionTemp !== undefined) {
    // 更新预测数据（保留后3个历史预测点）
    chartData.value.predictionTemps = [
      newPredictionTemp, // 新的预测点
      ...chartData.value.predictionTemps.slice(0, 3) // 保留前3个预测点
    ];
  }

  // 准备连接线数据（连接最后一个实际点和第一个预测点）
  const connectionData = Array(8).fill(null);
  if (chartData.value.actualTemps[3] !== null && chartData.value.predictionTemps[0] !== null) {
    connectionData[3] = chartData.value.actualTemps[3];
    connectionData[4] = chartData.value.predictionTemps[0];
  }

  chart.setOption({
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    xAxis: {
      data: currentTimes.value,
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicOut'
    },
    series: [
      {
        name: '实际数据',
        data: [...chartData.value.actualTemps, ...Array(4).fill(null)],
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '预测数据',
        data: [...Array(4).fill(null), ...chartData.value.predictionTemps],
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '连接线',
        data: connectionData,
        areaStyle: connectionData[3] !== null && connectionData[4] !== null ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(164, 203, 234, 0.8)' },
            { offset: 1, color: 'rgba(219, 235, 250, 0.1)' }
          ])
        } : undefined,
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      }
    ],
    graphic: [
      {
        type: 'line',
        z: 100,
        shape: { x1: 0, y1: 0, x2: 0, y2: chart.getHeight() },
        style: { stroke: '#ff6b6b', lineDash: [5, 5], lineWidth: 2 },
        position: [chart.convertToPixel('xAxis', 3.5), 0]
      },
      {
        type: 'text',
        z: 100,
        style: { fill: '#ff6b6b', fontSize: 14, fontWeight: 'bold',  },
        position: [chart.convertToPixel('xAxis', 3.5) + 10, 40] // 将 y 坐标从 20 改为 40
      }
    ]
  });
};

// 初始化图表数据
const initChartData = async () => {
  if (!selectedDeviceId.value) return;
  stopUpdateTimers();

  // 重置时间序列
  currentTimes.value = [...initialTimes];

  // 获取最新的实际数据
  const latestActualData = await fetchLatestActualSensorData(selectedDeviceId.value);

  if (latestActualData) {
    // 获取最新的预测数据
    const latestPrediction = await fetchLatestTemperaturePrediction();

    // 初始化图表数据
    chartData.value = {
      times: currentTimes.value,
      actualTemps: [22.5, 23.0, 23.5, latestActualData.temperature], // 初始历史数据+最新点
      predictionTemps: [latestPrediction, 24.5, 24.0, 23.8] // 最新预测+历史预测
    };

    // 确保最后一个实际值和第一个预测值不同
    if (chartData.value.actualTemps[3] === chartData.value.predictionTemps[0]) {
      chartData.value.predictionTemps[0] += 0.5;
    }

    // 初始化图表
    if (!chart) initChart();
    updateChartData();
    hasData.value = true;
    startUpdateTimers();
  }
};

// 启动定时更新
const startUpdateTimers = () => {
  stopUpdateTimers();

  // 数据更新定时器（5秒更新一次）
  dataUpdateTimer = setInterval(async () => {
    if (!selectedDeviceId.value || !chartData.value) return;

    // 获取最新的实际数据
    const latestActualData = await fetchLatestActualSensorData(selectedDeviceId.value);
    if (!latestActualData) return;

    // 获取最新的预测数据
    const latestPrediction = await fetchLatestTemperaturePrediction();

    // 确保最后一个实际值和第一个预测值不同
    let adjustedPrediction = latestPrediction;
    if (Math.abs(latestActualData.temperature - latestPrediction) < 0.5) {
      adjustedPrediction = latestActualData.temperature + (Math.random() > 0.5 ? 0.5 : -0.5);
    }

    // 更新图表（只更新最后一个实际数据点和第一个预测数据点）
    updateChartData(latestActualData.temperature, adjustedPrediction);
  }, DATA_UPDATE_INTERVAL);

  // 时间更新定时器（5秒更新一次）
  timeUpdateTimer = setInterval(() => {
    // 平滑更新时间序列
    updateTimeSeries();
  }, DATA_UPDATE_INTERVAL);
};

// 停止定时更新
const stopUpdateTimers = () => {
  if (dataUpdateTimer) {
    clearInterval(dataUpdateTimer);
    dataUpdateTimer = null;
  }
  if (timeUpdateTimer) {
    clearInterval(timeUpdateTimer);
    timeUpdateTimer = null;
  }
};

// 组件挂载
onMounted(async () => {
  deviceList.value = await fetchDevices();

  if (Object.keys(deviceList.value).length > 0) {
    selectedDeviceId.value = Object.keys(deviceList.value)[0];
    await initChartData();
  }
});

// 组件卸载
onBeforeUnmount(() => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
  stopUpdateTimers();
});

// 响应窗口大小变化
window.addEventListener('resize', () => {
  if (chart) {
    chart.resize();
  }
});

// 监听设备选择变化
watch(selectedDeviceId, async (newId) => {
  if (newId) {
    await initChartData();
  }
});
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  height: 380px;
  position: relative;
  top: -60px;
}

.device-selector {
  position: absolute;
  top: -40px;
  right: 20px;
  display: flex;
  gap: 20px;
  border-radius: 4px;
  padding: 10px 10px;
  z-index: 10;
  border: none;
}

.device-selector select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s;
}

.device-selector select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.3);
}

.status {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 30px;
  border-radius: 10px;
  z-index: 10;
  text-align: center;
  font-size: 18px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.loading {
  background: rgba(64, 158, 255, 0.9);
  color: white;
}

.error {
  background: rgba(245, 108, 108, 0.9);
  color: white;
  border: 1px solid #f56c6c;
}

.no-data {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: 1px solid #ddd;
}
</style>