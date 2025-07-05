<template>
  <div class="humidity-boxplot">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div ref="chartRef" class="chart-container" v-show="!loading && !error"></div>

    <!-- 独立的下拉框组件 -->
    <div class="time-range-selector">
      <select v-model="timeRange" @change="handleTimeRangeChange" class="range-select">
        <option value="current">当前时间</option>
        <option value="20min">预测后20分钟</option>
        <option value="1hour">预测后1小时</option>
      </select>
    </div>

    <div v-if="error" class="error-message">
      <i class="error-icon">⚠️</i>
      <span>{{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import * as echarts from 'echarts';

const chartRef = ref(null);
let chartInstance = null;
const loading = ref(true);
const error = ref('');
const humidityData = ref([]);
const locations = ref(['设备1', '设备2', '设备3', '设备4', '设备5', '设备6', '设备7']);
const timeRange = ref('current');

const API_URL = 'http://localhost:5000/api/device-sd';

const handleTimeRangeChange = () => {
  fetchData(timeRange.value);
};

const fetchData = async (range = 'current') => {
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(`${API_URL}?range=${range}`);
    if (!response.ok) throw new Error(`HTTP错误：${response.status}`);

    const data = await response.json();
    console.log('获取到的数据:', data);

    humidityData.value = locations.value.map(loc => data[loc] || []);
    await waitForChartContainer();
    initChart();

  } catch (err) {
    error.value = `数据获取失败：${err.message}`;
    console.error('数据获取错误:', err);
  } finally {
    loading.value = false;
  }
};

const waitForChartContainer = async () => {
  for (let i = 0; i < 3; i++) {
    await nextTick();
    if (chartRef.value) return true;
  }
  await new Promise(resolve => setTimeout(resolve, 300));
  if (!chartRef.value) throw new Error('图表容器加载失败');
  return true;
};

const initChart = () => {
  if (!chartRef.value) {
    error.value = '图表容器不存在';
    return;
  }

  try {
    if (chartInstance) chartInstance.dispose();
    chartInstance = echarts.init(chartRef.value);

    const option = {
      title: {
        text: '设备湿度分布箱线图',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          if (params.seriesName === 'outlier') {
            return `异常值: ${params.value[1]}%RH`;
          }
          const data = params.data;
          return [
            `设备: ${params.name}`,
            `最大值: ${data[4]}%RH`,
            `上四分位: ${data[3]}%RH`,
            `中位数: ${data[2]}%RH`,
            `下四分位: ${data[1]}%RH`,
            `最小值: ${data[0]}%RH`
          ].join('<br/>');
        }
      },
      legend: {
        data: ['湿度分布', '异常值'],
        bottom: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: locations.value,
        axisLabel: {
          interval: 0,
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '湿度 (%)',
        min: 20,
        max: 100
      },
      series: [
        {
          name: '湿度分布',
          type: 'boxplot',
          data: calculateBoxplotData(humidityData.value),
          itemStyle: {
            color: '#5470C6',
            borderColor: '#314D99'
          }
        },
        {
          name: '异常值',
          type: 'scatter',
          data: calculateOutliers(humidityData.value),
          itemStyle: { color: '#EE6666' }
        }
      ]
    };

    chartInstance.setOption(option);
    window.addEventListener('resize', handleResize);

  } catch (err) {
    error.value = `图表渲染失败：${err.message}`;
    console.error('图表初始化错误:', err);
  }
};

// 其他工具函数保持不变...
const calculateBoxplotData = (data) => {
  return data.map((values) => {
    if (!values || values.length === 0) return [];
    const sortedValues = [...values].sort((a, b) => a - b);
    const q1 = calculatePercentile(sortedValues, 25);
    const median = calculatePercentile(sortedValues, 50);
    const q3 = calculatePercentile(sortedValues, 75);
    const iqr = q3 - q1;
    const min = Math.max(sortedValues[0], q1 - 1.5 * iqr);
    const max = Math.min(sortedValues[sortedValues.length - 1], q3 + 1.5 * iqr);
    return [min, q1, median, q3, max];
  });
};

const calculatePercentile = (array, percentile) => {
  const index = (percentile / 100) * (array.length - 1);
  const floor = Math.floor(index);
  const ceil = Math.ceil(index);
  return floor === ceil ? array[floor] : array[floor] + (index - floor) * (array[ceil] - array[floor]);
};

const calculateOutliers = (data) => {
  let allOutliers = [];

  // 收集所有设备的异常值
  data.forEach((values, index) => {
    if (!values || values.length === 0) return;

    const sortedValues = [...values].sort((a, b) => a - b);
    const q1 = calculatePercentile(sortedValues, 25);
    const q3 = calculatePercentile(sortedValues, 75);
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;

    const deviceOutliers = sortedValues
        .filter(val => val < lowerBound || val > upperBound)
        .map(outlier => [index, outlier]);

    allOutliers = allOutliers.concat(deviceOutliers);
  });

  // 最多只返回一个异常值（随机选择一个）
  return allOutliers.length > 0 ? [allOutliers[0]] : [];
};
const handleResize = () => {
  chartInstance?.resize();
};

onMounted(() => {
  fetchData();
  const interval = setInterval(() => fetchData(timeRange.value), 5000);
  onBeforeUnmount(() => clearInterval(interval));
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) chartInstance.dispose();
});
</script>

<style scoped>
.humidity-boxplot {
  width: 600px;
  height: 400px;
  position: relative;
  padding-top: 10px;

}

.chart-container {
  width: 600px;
  height: 400px;
}

.loading, .error-message {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.time-range-selector {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
}

.range-select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  font-size: 12px;
  cursor: pointer;
}

.range-select:focus {
  outline: none;
  border-color: #5470C6;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #007BFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-message {
  color: #f56c6c;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>