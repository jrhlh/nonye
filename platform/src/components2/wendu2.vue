<template>
  <div class="chart-container">
    <div class="header">
      <select
          class="device-select"
          @change="handleDeviceChange"
          v-model="selectedDeviceId"
          :disabled="loading"
      >
        <option v-for="(device, key) in deviceList" :key="key" :value="key">
          {{ device.device_name }}
        </option>
      </select>
    </div>
    <div ref="chartDom" style="width: 600px; height: 390px"></div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">数据加载失败: {{ error }}</div>
    <div v-if="showAlert" class="alert-overlay">
      <div class="alert-box">
        <h3>温度异常警告</h3>
        <p>检测到设备温度过高 (38°C)，请立即检查设备！</p>
        <button @click="showAlert = false">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import eventBus from '../utlis/event-bus';

const chartDom = ref<HTMLDivElement | null>(null);
let myChart: echarts.ECharts | null = null;
const loading = ref(false);
const error = ref<string | null>(null);
const deviceList = ref<Record<string, { device_name: string }>>({});
const selectedDeviceId = ref<string>('');
const currentThreshold = ref(eventBus.getThreshold() || 28);
const showAlert = ref(false);
const dateInterval = ref<NodeJS.Timeout | null>(null);
const hasShownJune8Alert = ref(false); // 新增：标记是否已经显示过6月8日的警告

// 初始日期设置为6月1日
const currentDate = ref(new Date('2025-06-01'));
const displayedDates = ref<string[]>([]);
const displayedTemperatures = ref<number[]>([]);

// 生成5天的日期数组
const generateDates = (startDate: Date) => {
  const dates = [];
  for (let i = 0; i < 5; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    dates.push(date.toISOString().split('T')[0]);
  }
  return dates;
};

// 生成随机温度数据 (25-34度之间，6月8日设为38度)
const generateTemperatures = (dates: string[]) => {
  return dates.map(date => {
    if (date === '2025-06-08') {
      return 38; // 异常温度
    }
    return Math.floor(Math.random() * 10) + 25; // 25-34度
  });
};

const option = ref<echarts.EChartsOption>({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow',
      shadowStyle: { opacity: 0.2 }
    },
    formatter: '{b}<br/>温度: {c}°C'
  },
  xAxis: {
    type: 'category',
    data: [],
    axisLabel: {
      formatter: (value: string) => value.split('-').slice(1).join('-'),
      rotate: 0,
      interval: 0
    }
  },
  yAxis: {
    type: 'value',
    min: 15,
    max: 40,
    axisLabel: { formatter: '{value} °C' }
  },
  series: [
    {
      name: '温度',
      data: [],
      type: 'bar',
      itemStyle: {
        color: '#02BBB5'
      },
      label: { show: true, position: 'top', formatter: '{c}°C' },
      markLine: {
        data: [
          {
            yAxis: 22.0,
            name: '正常温度下限',
            lineStyle: { color: '#4CAF50', width: 3, type: 'dashed' },
            label: { position: 'end', formatter: '下限22°C' }
          },
          {
            yAxis: currentThreshold.value,
            name: '正常温度上限',
            lineStyle: { color: '#FF9800', width: 3, type: 'dashed' },
            label: { position: 'end', formatter: `上限${currentThreshold.value}°C` }
          }
        ]
      }
    }
  ]
});

// 获取设备列表
const fetchDevices = async () => {
  try {
    loading.value = true;
    const response = await axios.get('http://localhost:5000/api/devices');
    if (response.data.code === 200) {
      deviceList.value = response.data.data;
      if (Object.keys(response.data.data).length > 0) {
        selectedDeviceId.value = Object.keys(response.data.data)[0];
      }
    } else {
      error.value = response.data.message || '获取设备列表失败';
    }
  } catch (err) {
    console.error('获取设备列表错误:', err);
    error.value = '获取设备列表失败';
  } finally {
    loading.value = false;
  }
};
const emit = defineEmits()
// 更新图表数据
const updateChartData = () => {
  displayedDates.value = generateDates(currentDate.value);
  displayedTemperatures.value = generateTemperatures(displayedDates.value);

  // 检查是否是6月8日且温度异常(38度)并显示警告
  const june8Index = displayedDates.value.indexOf('2025-06-08');
  if (june8Index !== -1 && displayedTemperatures.value[june8Index] === 38 && !hasShownJune8Alert.value) {
    emit('handleWarning')

    showAlert.value = true;
    hasShownJune8Alert.value = true; // 标记已显示警告
  }

  // 处理柱形颜色
  const processedData = displayedTemperatures.value.map((temp, index) => {
    let color = '#02BBB5'; // 默认蓝色
    if (temp > currentThreshold.value) {
      color = 'red'; // 超过上限值变红
    } else if (temp < 22) {
      color = 'red'; // 低于下限值变红
    }
    return {
      value: temp,
      itemStyle: { color }
    };
  });

  option.value = {
    ...option.value,
    xAxis: {
      ...option.value.xAxis,
      data: displayedDates.value
    },
    series: [
      {
        ...option.value.series[0],
        data: processedData
      }
    ]
  };

  if (myChart) {
    myChart.setOption(option.value);
  }
};

// 自动更新日期
const startDateAutoUpdate = () => {
  if (dateInterval.value) clearInterval(dateInterval.value);
  dateInterval.value = setInterval(() => {
    currentDate.value.setDate(currentDate.value.getDate() + 1);
    updateChartData();
  }, 4000); // 每4秒更新一次
};

// 使用新阈值更新图表
const updateChartWithNewThreshold = (threshold: number) => {
  currentThreshold.value = threshold;
  option.value.series[0].markLine.data[1].yAxis = threshold;
  option.value.series[0].markLine.data[1].label.formatter = `上限${threshold}°C`;
  updateChartData();
};

const initChart = () => {
  if (chartDom.value) {
    myChart = echarts.init(chartDom.value);
    updateChartData();
  }
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => myChart?.resize());
  fetchDevices();
  startDateAutoUpdate();

  // 监听全局阈值更新
  eventBus.on('thresholdUpdated', (threshold: number) => {
    updateChartWithNewThreshold(threshold);
  });
});

onBeforeUnmount(() => {
  if (dateInterval.value) clearInterval(dateInterval.value);
  window.removeEventListener('resize', () => myChart?.resize());
  eventBus.off('thresholdUpdated');
  myChart?.dispose();
});

const handleDeviceChange = () => {
  updateChartData();
};
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
  position: relative;
  margin-top: -115px;
}

.header {
  display: flex;
  align-items: center;
  margin-left: 495px;
  margin-top: 10px;
  position: relative;
  top: 20px;
  padding: 8px 0;
}

.device-select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  height: auto;
  min-width: 120px;
  font-size: 17px;
  cursor: pointer;
  position: relative;
  top: 13px;
  right: 10px;
}

.loading, .error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
}

.alert-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.alert-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.alert-box h3 {
  color: #d32f2f;
  margin-top: 0;
}

.alert-box button {
  background: #d32f2f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}
</style>