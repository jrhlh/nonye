<template>
  <div class="echarts-container">
    <div ref="chartRef" style="width: 670px; height: 440px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios'; // 引入axios获取后端数据

const chartRef = ref(null);
let chartInstance = null;
const faultTimeData = ref([]); // 存储故障时段数据

// 初始化图表
const initChart = () => {
  if (!chartRef.value || !faultTimeData.value.length) return; // 确保容器和数据存在

  chartInstance = echarts.init(chartRef.value);

  const option = {
    title: {
      text: '系统故障时段分布统计',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333'
      },
      subtext: '24小时故障发生情况',
      subtextStyle: {
        fontSize: 14,
        color: '#666'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '时段: {b}<br/>故障次数: {c}次',
      backgroundColor: 'rgba(50,50,50,0.9)',
      borderColor: '#333',
      textStyle: {
        color: '#fff'
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '8%', // 调整底部留白适应标签
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: faultTimeData.value.map(item => item.name), // 动态获取时段名称
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12,
        margin: 15
      },
      axisLine: { lineStyle: { color: '#666' } },
      axisTick: { alignWithLabel: true, length: 5 }
    },
    yAxis: {
      type: 'value',
      name: '故障次数',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: { fontSize: 14, padding: [0, 0, 10, 0] },
      axisLabel: { fontSize: 12 },
      splitLine: { lineStyle: { type: 'dashed' } }
    },
    series: [{
      name: '故障次数',
      type: 'bar',
      barWidth: '50%',
      data: faultTimeData.value.map(item => item.value), // 动态获取故障次数
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ff9e9e' },
          { offset: 0.5, color: '#ff6b6b' },
          { offset: 1, color: '#ff3d3d' }
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ff6b6b' },
            { offset: 0.7, color: '#ff3d3d' },
            { offset: 1, color: '#cc2a2a' }
          ]),
          shadowColor: 'rgba(255, 100, 100, 0.5)',
          shadowBlur: 10,
          shadowOffsetY: 3
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}',
        fontSize: 12,
        fontWeight: 'bold',
        color: '#ff3d3d'
      }
    }]
  };

  chartInstance.setOption(option);
  window.addEventListener('resize', handleResize);
};

const handleResize = () => {
  chartInstance?.resize();
};

// 从后端获取故障时段数据
const fetchFaultTimeData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/fault-time-distribution');
    if (response.data.success) {
      faultTimeData.value = response.data.data;
    }
  } catch (error) {
    console.error('获取故障时段数据失败:', error);
  }
};

onMounted(() => {
  fetchFaultTimeData(); // 组件挂载后获取数据
  watch(faultTimeData, () => { // 数据更新后重新渲染图表
    chartInstance?.dispose();
    initChart();
  }, { deep: true });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});
</script>

<style scoped>
.echarts-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 25px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 5px 0 rgba(0, 0, 0, 0.12);
  width: fit-content;
  margin: 0 auto;
  border: 1px solid #eee;
  position: relative;
  right: -10px;
}
</style>