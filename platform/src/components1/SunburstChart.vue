<template>
  <div ref="chartRef" class="sunburst-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: ''
  }
});

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const renderChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  const option = {
    title: props.title ? { text: props.title, left: 'center', top: 10, textStyle: { fontSize: 16, fontWeight: 700 } } : undefined,
    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
    series: [
      {
        type: 'sunburst',
        data: props.data,
        radius: [0, '90%'],
        label: {
          rotate: 'radial',
          fontSize: 12
        },
        itemStyle: {
          borderRadius: 6,
          borderWidth: 1,
          borderColor: '#fff'
        },
        emphasis: {
          focus: 'ancestor'
        }
      }
    ]
  };
  chartInstance.setOption(option);
};

onMounted(() => {
  renderChart();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', resizeChart);
});

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

watch(() => props.data, () => {
  renderChart();
});
</script>

<style scoped>
.sunburst-chart {
  width: 100%;
  height: 320px;
  min-height: 220px;
}
</style> 