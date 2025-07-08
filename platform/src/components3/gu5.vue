<template>
  <div class="echarts-container">
    <div ref="chartRef" style="width: 670px; height: 440px;"></div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue';
import * as echarts from 'echarts';

const chartRef = ref(null);
let chartInstance = null;

// 手动设置故障时段数据 (6点1个，18点1个，22点1个)
const faultTimeData = ref([
  {name: '00:00-02:00', value: 0},
  {name: '02:00-04:00', value: 0},
  {name: '04:00-06:00', value: 1}, // 6点一个故障
  {name: '06:00-08:00', value: 0},
  {name: '08:00-10:00', value: 0},
  {name: '10:00-12:00', value: 0},
  {name: '12:00-14:00', value: 0},
  {name: '14:00-16:00', value: 0},
  {name: '16:00-18:00', value: 0},
  {name: '18:00-20:00', value: 0},
  {name: '20:00-22:00', value: 1}, // 22点一个故障
  {name: '22:00-24:00', value: 0}
]);

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;

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
      bottom: '8%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: faultTimeData.value.map(item => item.name),
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12,
        margin: 15
      },
      axisLine: {lineStyle: {color: '#666'}},
      axisTick: {alignWithLabel: true, length: 5}
    },
    yAxis: {
      type: 'value',
      name: '故障次数',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {fontSize: 14, padding: [0, 0, 10, 0]},
      axisLabel: {
        fontSize: 12,
        formatter: function (value) {
          return value; // 确保Y轴只显示整数
        }
      },
      min: 0, // 最小值设为0
      max: 5, // 最大值设为5
      interval: 1, // 间隔设为1
      splitLine: {lineStyle: {type: 'dashed'}}
    },
    series: [{
      name: '故障次数',
      type: 'bar',
      barWidth: '50%',
      data: faultTimeData.value.map(item => item.value),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {offset: 0, color: '#ff9e9e'},
          {offset: 0.5, color: '#ff6b6b'},
          {offset: 1, color: '#ff3d3d'}
        ]),
        borderRadius: [6, 6, 0, 0]
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: '#ff6b6b'},
            {offset: 0.7, color: '#ff3d3d'},
            {offset: 1, color: '#cc2a2a'}
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

onMounted(() => {
  initChart();
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
  padding-top: 47px;
  width: fit-content;
  margin: 0 auto;
  position: relative;
}
</style>