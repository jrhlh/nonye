<template>
  <div class="echarts-container">
    <div ref="chartRef" style="width: 550px; height: 454px;"></div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount, watch} from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartRef = ref(null);
let chartInstance = null;
const faultData = ref([]);

const colorMap = {
  '其他故障': '#0EA5E9',
  '离线故障': '#F87171',  // 粉调红
  '传感器故障': '#FBBF24',  // 奶油橙

};
// 初始化图表
const initChart = () => {
  if (!chartRef.value || !faultData.value.length) return;

  chartInstance = echarts.init(chartRef.value);

  // 为数据添加颜色配置
  const coloredData = faultData.value.map(item => ({
    ...item,
    itemStyle: {
      color: colorMap[item.name] || '#999' // 默认灰色
    }
  }));

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
      left: 'center',
      data: coloredData.map(item => item.name)
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
        data: coloredData
      }
    ]
  };

  chartInstance.setOption(option);
  window.addEventListener('resize', handleResize);
};

const handleResize = () => {
  chartInstance?.resize();
};

// 获取故障类型数据
const fetchFaultData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/fault-types');
    if (response.data.success) {
      faultData.value = response.data.data;
    }
  } catch (error) {
    console.error('获取故障类型数据失败:', error);
  }
};

onMounted(() => {
  fetchFaultData();
  watch(faultData, () => {
    if (chartInstance) {
      chartInstance.dispose();
    }
    initChart();
  }, {deep: true});
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
  padding: 20px;

  width: fit-content;
  margin: 0 auto;
  position: relative;
  right: 5px;
  background-color: #FFFFFF;
}
</style>