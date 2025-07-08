<template>
  <!--  抽屉中的ph图表-->
  <div class="ph-chart-container">
    <div ref="chartRef" class="chart-wrapper"></div>
    <div v-if="isLoading" class="loading">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartRef = ref(null);
let chartInstance = null;
const isLoading = ref(true);
const error = ref('');
let updateInterval = null;
let currentTime = new Date(); // 当前基准时间
let chartData = ref([]); // 存储当前图表数据

// 生成时间点 (每20分钟)
const generateTimePoints = () => {
  const timePoints = [];
  for (let i = 0; i < 8; i++) {
    const delta = i * 20; // 20分钟间隔
    const time = new Date(currentTime.getTime() + delta * 60000);
    timePoints.push(time.toTimeString().substring(0, 5)); // 格式化为HH:MM
  }
  return timePoints;
};

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;

  chartInstance = echarts.init(chartRef.value);

  // 响应式调整大小
  const resizeChart = () => {
    if (chartInstance) {
      chartInstance.resize();
    }
  };

  window.addEventListener('resize', resizeChart);

  // 组件卸载时清理
  onBeforeUnmount(() => {
    if (chartInstance) {
      chartInstance.dispose();
      chartInstance = null;
    }
    window.removeEventListener('resize', resizeChart);
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  return chartInstance;
};

// 更新数据 - 只更新最后一个实际值和最后一个预测值
const updateData = () => {
  if (chartData.value.length === 0) return;

  // 移动数据点 - 相当于时间向前推移
  const newData = [...chartData.value];

  // 移动实际值
  for (let i = 0; i < 3; i++) {
    newData[i].ph = newData[i + 1].ph;
  }

  // 移动预测值
  for (let i = 4; i < 7; i++) {
    newData[i].ph = newData[i + 1].ph;
  }

  // 生成新的最后一个实际值 (6.1-6.6)
  newData[3].ph = parseFloat((6.1 + Math.random() * 0.5).toFixed(2));

  // 生成新的最后一个预测值 (6.1-7.0)
  newData[7].ph = parseFloat((6.1 + Math.random() * 0.9).toFixed(2));

  chartData.value = newData;
  renderChart(chartData.value);
};

// 渲染pH值趋势图
const renderChart = (data) => {
  if (!data || data.length === 0) {
    error.value = '没有可用的数据';
    isLoading.value = false;
    return;
  }

  // 分离实际值和预测值
  const actualData = data.filter(item => item.type === 'actual');
  const predictionData = data.filter(item => item.type === 'prediction');

  const chart = initChart();
  if (!chart) return;

  // 提取pH值数据
  const actualPhValues = actualData.map(item => item.ph);
  const predictionPhValues = predictionData.map(item => item.ph);

  // 计算pH值范围
  const allPhValues = [...actualPhValues, ...predictionPhValues];
  const minPh = Math.min(...allPhValues);
  const maxPh = Math.max(...allPhValues);
  const phRange = maxPh - minPh;
  const yMin = Math.max(6, Math.floor(minPh - phRange * 0.1));
  const yMax = Math.min(8, Math.ceil(maxPh + phRange * 0.1));

  const option = {
    title: {
      text: 'pH值动态监测 (20分钟间隔)',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      backgroundColor: 'rgba(255,255,255,0.9)',
      borderColor: '#ddd',
      borderWidth: 1,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      formatter: (params) => {
        const param = params[0];
        const type = param.seriesName === '实际值' ? '实际测量' :
            param.seriesName === '连接线' ? '实际→预测' : '模型预测';
        return `时间: ${param.name}<br>pH值: ${param.value.toFixed(2)} pH<br>类型: ${type}`;
      }
    },
    toolbox: {
      show: true,
      feature: {
        saveAsImage: {
          title: '保存为图片',
          pixelRatio: 2
        }
      },
      right: 20,
      top: 1
    },
    legend: {
      data: ['实际值', '连接线', '预测值'],
      right: 20,
      top: 50
    },
    xAxis: {
      type: 'category',
      data: generateTimePoints(), // 使用动态生成的时间点
      boundaryGap: false,
      name: '时间',
      axisLabel: {
        color: '#666',
        interval: 0
      },
      axisLine: {
        lineStyle: {
          color: '#e5e5e5'
        }
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#f8f8f8',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'value',
      min: yMin,
      max: yMax,
      name: 'pH值',
      axisLabel: {
        formatter: '{value} pH',
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#e5e5e5'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f8f8f8',
          type: 'dashed'
        }
      },
      markLine: {
        data: [
          {
            yAxis: 7.4,
            lineStyle: {
              color: 'red',
              type: 'dashed'
            },
            label: {
              show: true,
              position: 'start',
              formatter: '理想值7.4'
            }
          },
          {
            yAxis: 7,
            lineStyle: {
              color: 'gray',
              type: 'dashed'
            },
            label: {
              show: true,
              position: 'start',
              formatter: '中性7.0'
            }
          }
        ]
      }
    },
    series: [
      {
        name: '实际值',
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 8,
        showSymbol: true,
        data: actualPhValues,
        lineStyle: {
          width: 3,
          color: '#1890ff'
        },
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {offset: 0, color: 'rgba(24, 144, 255, 0.2)'},
              {offset: 1, color: 'rgba(24, 144, 255, 0)'}
            ]
          }
        }
      },
      {
        name: '连接线',
        type: 'line',
        smooth: false,
        symbol: 'none',
        showSymbol: false,
        data: [
          ...Array(3).fill(null), // 前三个点不显示
          actualPhValues[actualPhValues.length - 1], // 最后一个实际值
          predictionPhValues[0], // 第一个预测值
          ...Array(3).fill(null)  // 后三个点不显示
        ],
        lineStyle: {
          width: 3,
          color: '#1890ff'
        },
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {offset: 0, color: 'rgba(24, 144, 255, 0.2)'},
              {offset: 1, color: 'rgba(24, 144, 255, 0)'}
            ]
          }
        }
      },
      {
        name: '预测值',
        type: 'line',
        smooth: false,
        symbol: 'diamond',
        symbolSize: 8,
        showSymbol: true,
        data: [null, null, null, null, ...predictionPhValues], // 前4个点为null，不显示
        lineStyle: {
          width: 3,
          color: '#ff4d4f'
        },
        itemStyle: {
          color: '#ff4d4f'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {offset: 0, color: 'rgba(255, 77, 79, 0.2)'},
              {offset: 1, color: 'rgba(255, 77, 79, 0)'}
            ]
          }
        }
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        bottom: 10,
        style: {
          text: `pH值在7.35-7.45之间为正常范围 | 当前基准时间: ${currentTime.toLocaleTimeString()}`,
          fontSize: 12,
          fill: '#999'
        }
      }
    ]
  };

  chart.setOption(option);
};

// 获取初始数据
const fetchPhData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/ph_data/get_ph_today');
    chartData.value = response.data.data;

    if (chartData.value.length === 0) {
      error.value = '没有可用的数据';
    } else {
      renderChart(chartData.value);
    }
  } catch (err) {
    console.error('获取数据失败:', err);
    error.value = '获取数据失败，请检查网络连接';
  } finally {
    isLoading.value = false;
  }
};

// 每5秒更新数据
const startAutoUpdate = () => {
  updateInterval = setInterval(() => {
    // 更新基准时间
    currentTime = new Date(currentTime.getTime() + 20 * 60000);
    updateData();
  }, 5000);
};

onMounted(() => {
  fetchPhData();
  startAutoUpdate();
});
</script>

<style scoped>
.ph-chart-container {
  width: 100%;
  max-width: 800px;
  margin: 20px auto;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
  background-color: #fff;
  padding-top: 25px;

}

.loading {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 16px;
  position: relative;
}

.loading::before {
  content: '';
  display: inline-block;
  width: 24px;
  height: 24px;
  margin-right: 8px;
  border: 3px solid #ccc;
  border-top-color: #52c41a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  vertical-align: middle;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  text-align: center;
  padding: 20px;
  color: #f5222d;
  font-size: 16px;
  background-color: #fff2f0;
  border-radius: 4px;
  border: 1px solid #ffccc7;
}
</style>