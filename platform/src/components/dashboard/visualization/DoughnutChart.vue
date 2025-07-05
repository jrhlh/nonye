<template>
  <div ref="chartRef" class="doughnut-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  data: Array<{ name: string; value: number }>
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const statusColorMap: Record<string, string> = {
  '正常': '#52c41a',
  '警告': '#faad14',
  '故障': '#ff4d4f',
  '离线': '#d9d9d9',
};

const total = props.data.reduce((sum, item) => sum + item.value, 0);

const renderChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  const option = {
    // title: props.title ? { text: props.title, left: 'center', top: 10, textStyle: { fontSize: 16, fontWeight: 700 } } : undefined,
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: '#e0e0e0',
      borderWidth: 1,
      textStyle: { color: '#222', fontSize: 13 },
      padding: 8,
      extraCssText: '',
      formatter: params => `${params.name}: ${params.percent}% (${params.value})`
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 40,
      itemWidth: 14,
      itemHeight: 8,
      itemGap: 12,
      textStyle: {
        fontSize: 13,
        color: '#888',
        fontWeight: 400
      },
      data: props.data.map((d: { name: string; value: number }) => d.name)
    },
    series: [
      {
        name: '全局状态',
        type: 'pie',
        radius: ['62%', '80%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 14,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'center',
          fontSize: 16,
          fontWeight: 600,
          color: '#222',
          formatter: () => `${total}`
        },
        emphasis: {
          scale: false,
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 700,
            color: '#1890ff',
            formatter: () => `${total}`
          }
        },
        color: [
          '#52c41a',
          '#faad14',
          '#ff4d4f',
          '#d9d9d9'
        ],
        data: props.data
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
.doughnut-chart {
  width: 100%;
  height: 240px;
  min-width: 160px;
  min-height: 160px;
  background: #f8fbff;
  border-radius: 14px;
  box-shadow: 0 2px 8px 0 rgba(24,144,255,0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 10px;
  transition: none;
}
</style> 