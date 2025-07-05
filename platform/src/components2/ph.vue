<template>
  <div class="chart-container">
    <!-- 筛选容器：对应原 filter-container，替换 class 并调整位置逻辑 -->
    <div class="header">
      <select
          class="device-select"
          v-model="selectedTimeRange"
          @change="fetchData"
      >
        <option
            v-for="range in timeRanges"
            :key="range.value"
            :value="range.value"
        >
          {{ range.label }}
        </option>
      </select>
    </div>

    <!-- 图表容器：替换 ref 和 class，功能不变 -->
    <div ref="chartRef" class="chart" style="width: 100%; height: 400px;"></div>

    <!-- 状态提示：保留逻辑，调整 class -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="data.value && data.value.length === 0" class="no-data">暂无数据</div>
  </div>
</template>

<script setup>
// 以下 JS 逻辑完全保留，确保功能不变
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartRef = ref(null);
let chartInstance = null;
const selectedTimeRange = ref('today');
const timeRanges = ref([]);
const data = ref([]);
const loading = ref(false);
const error = ref('');

// 获取时间范围选项
const fetchMetadata = async () => {
  try {
    const response = await axios.get('http://localhost:5000/ph_data/get_time_ranges');
    timeRanges.value = response.data.time_ranges;
  } catch (err) {
    console.error('获取时间范围失败:', err);
    error.value = '获取数据失败，请重试';
  }
};

// 获取 PH 值数据
const fetchData = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await axios.get('http://localhost:5000/ph_data/get_ph_data', {
      params: {
        time_range: selectedTimeRange.value
      }
    });

    console.log('API响应数据:', response.data);
    processData(response.data);
  } catch (err) {
    console.error('获取 PH 数据失败:', err);
    error.value = '获取数据失败，请重试';
  } finally {
    loading.value = false;
  }
};

// 处理数据并渲染图表
const processData = (dataResponse) => {
  if (!dataResponse || !Array.isArray(dataResponse.data)) {
    console.error('数据格式错误:', dataResponse);
    error.value = '数据格式错误，请刷新页面重试';
    return;
  }

  data.value = dataResponse.data;

  if (!chartInstance) {
    initChart();
  } else {
    updateChart();
  }
};

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    updateChart();
  }
};

// 更新图表数据
const updateChart = () => {
  if (!chartInstance || !Array.isArray(data.value) || data.value.length === 0) {
    return;
  }

  // 统一处理数据格式，确保 timestamp 是正确的日期时间格式
  const formattedData = data.value.map(item => {
    if (item.timestamp) {
      // 处理带 timestamp 的数据
      return {
        timestamp: item.timestamp,
        value: item.ph !== undefined ? item.ph : item.avg_ph
      };
    } else if (item.date) {
      // 处理带 date 的数据（通常来自 get_ph_data_by_date_range）
      return {
        timestamp: `${item.date} 12:00:00`, // 为纯日期添加默认时间
        value: item.avg_ph
      };
    }
    return null;
  }).filter(item => item !== null).sort((a, b) =>
      new Date(a.timestamp) - new Date(b.timestamp)
  );

  if (formattedData.length === 0) {
    return;
  }

  // 准备图表数据
  const scatterData = formattedData.map(item => [
    // 确保转换为正确的时间戳格式
    new Date(item.timestamp).getTime(),
    item.value
  ]);

  // 根据时间范围设置不同的 x 轴标签格式
  let xAxisLabelFormatter;
  if (selectedTimeRange.value === 'today') {
    // 今日：只显示时分
    xAxisLabelFormatter = (value) => {
      const date = new Date(value);
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    };
  } else if (selectedTimeRange.value === 'last_three_days' || selectedTimeRange.value === 'next_two_days') {
    // 前三天/后两天：显示月日时
    xAxisLabelFormatter = (value) => {
      const date = new Date(value);
      return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit' });
    };
  } else {
    // 其他：只显示年月日
    xAxisLabelFormatter = (value) => {
      const date = new Date(value);
      return date.toLocaleDateString('zh-CN');
    };
  }

  // 设置图表配置
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const date = new Date(params.data[0]);
        const timeStr = date.toLocaleString('zh-CN');
        return `时间: ${timeStr} <br/>PH值: ${params.data[1].toFixed(2)}`;
      }
    },
    xAxis: {
      name: '日期/时间',
      type: 'time',
      axisLabel: {
        formatter: xAxisLabelFormatter,
        rotate: 45,
        interval: 'auto' // 自动调整标签间隔
      }
    },
    yAxis: {
      name: 'PH值',
      min: 2,
      max: 9,
      splitNumber: 7,
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed'
        }
      },
      axisTick: {
        interval: 1
      },
      axisLabel: {
        formatter: (value) => value.toFixed(0)
      }
    },
    series: [
      {
        name: 'PH值',
        type: 'scatter',
        data: scatterData,
        symbolSize: 10,
        itemStyle: {
          color: '#1890ff'
        },
        emphasis: {
          itemStyle: {
            color: '#f5222d',
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          }
        }
      }
    ],
    markLine: {
      data: [
        { yAxis: 7 }  // 中性线
      ],
      lineStyle: {
        type: 'dashed',
        color: '#f5222d'
      },
      label: {
        position: 'end',
        formatter: '中性(PH=7)'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    }
  };

  chartInstance.setOption(option);
};

onMounted(() => {
  fetchMetadata();
  fetchData();

  // 窗口大小变化时重新渲染图表
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize();
    }
  });
});

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', () => {
  });
});

watch(selectedTimeRange, fetchData);
</script>

<style scoped>
/* 新模板样式体系，适配原功能的 DOM 结构 */
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;

}

/* 筛选器容器：对应原 filter-container，调整为新 class 和定位 */
.header {
  position: absolute;
  top: -30px;
  right: 20px;
  display: flex;
  gap: 20px;
  border-radius: 4px;
  padding: 10px 20px;
  z-index: 10;
}

/* 下拉选择器样式：对应原 select，替换 class */
.device-select {
  width: 110px;
  padding: 10px 10px;
  font-size: 15px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s;
  border: 1px solid #ccc;
  border-radius: 4px;
  position: absolute;
  top: 3px;
  right: 0;
}

/* 图表容器：替换 class，样式不变 */
.chart {
  border: none;
  width: 100%;
  height: 400px;
}

/* 状态提示：替换 class，样式逻辑不变 */
.loading, .error, .no-data {
  text-align: center;
  margin-top: 80px;
  font-size: 16px;
  border: none;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
}

.error {
  color: #e53935;
}
</style>