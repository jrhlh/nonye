<template>
  <div class="echarts-container">
    <div ref="chartRef" style="width: 550px; height: 454px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios'; // 引入axios用于数据请求

const chartRef = ref(null);
let chartInstance = null;
const faultData = ref([]); // 存储故障类型数据

// 初始化图表
const initChart = () => {
  if (!chartRef.value || !faultData.value.length) return; // 确保容器和数据存在

  chartInstance = echarts.init(chartRef.value);

  const option = {
    title: {
      text: '故障类型分布',
      left: 'left',
      top: 10,
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '故障类型分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 40,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: faultData.value // 动态绑定故障类型数据
      }
    ]
  };

  chartInstance.setOption(option);
  window.addEventListener('resize', handleResize);
};

const handleResize = () => {
  chartInstance?.resize();
};

// 获取故障类型数据的异步函数
const fetchFaultData = async () => {
  try {
    // 假设后端接口路径为 /device/fault-types（需与实际后端一致）
    const response = await axios.get('http://localhost:5000/fault-types');
    if (response.data.success) {
      faultData.value = response.data.data; // 更新故障类型数据
    }
  } catch (error) {
    console.error('获取故障类型数据失败:', error);
  }
};

onMounted(() => {
  fetchFaultData(); // 组件挂载后获取数据
  watch(faultData, () => { // 监听数据变化，重新渲染图表
    chartInstance?.dispose();
    initChart();
  }, {deep: true});
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose(); // 组件卸载时销毁图表实例
});
</script>

<style scoped>
.echarts-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 5px 0 rgba(0, 0, 0, 0.12);
  width: fit-content;
  margin: 0 auto;
  position: relative;
  right: 5px;
  background-color: #FFFFFF;
}
</style>