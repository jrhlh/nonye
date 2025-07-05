<template>
  <div ref="chartRef" style="width: 350px; height: 400px;"></div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue';
import * as echarts from 'echarts';

const chartRef = ref(null);
let chartInstance = null;

const option = {
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: {
      fontSize: 14,
      color: '#333'
    }
  },
  series: [
    {
      name: '状态统计',
      type: 'pie',
      radius: ['40%', '60%'], // 调整半径以缩小饼图
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 5,
        borderColor: '#fff',
        borderWidth: 2
      },
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
      data: [
        {
          value: 58,
          name: '正常',
          itemStyle: {color: '#4bb118'}
        },
        {
          value: 14,
          name: '警告',
          itemStyle: {color: '#faad14'}
        },
        {
          value: 14,
          name: '故障',
          itemStyle: {color: '#f5222d'}
        },
        {
          value: 14,
          name: '离线',
          itemStyle: {color: '#bfbfbf'}
        }
      ]
    }
  ]
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    chartInstance.setOption(option);
    window.addEventListener('resize', handleResize);
  }
});

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    window.removeEventListener('resize', handleResize);
  }
});

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};
</script>

<style scoped>
/* You can add custom styles here */
</style>