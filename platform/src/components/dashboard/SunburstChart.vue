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

// 状态颜色映射
const statusColorMap: Record<string, string> = {
  '正常': '#52c41a',
  '警告': '#faad14',
  '故障': '#ff4d4f',
  '离线': '#d9d9d9',
};

// 递归为每个节点分配颜色
function assignColors(nodes: any[]) {
  if (!Array.isArray(nodes)) return;
  nodes.forEach(node => {
    if (node.status && statusColorMap[node.status]) {
      node.itemStyle = { color: statusColorMap[node.status] };
    }
    if (node.children) assignColors(node.children);
  });
}

const renderChart = () => {
  if (!chartRef.value) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  // 深拷贝数据，避免污染原数据
  const chartData = JSON.parse(JSON.stringify(props.data));
  assignColors(chartData);
  const option = {
    title: props.title ? { text: props.title, left: 'center', top: 10, textStyle: { fontSize: 16, fontWeight: 700 } } : undefined,
    tooltip: {
      trigger: 'item',
      formatter: info => {
        const status = info.data.status ? `<br/>状态: <b>${info.data.status}</b>` : '';
        return `<b>${info.name}</b><br/>数值: ${info.value}${status}<br/>层级: ${info.treePathInfo.map(x => x.name).join(' / ')}`;
      }
    },
    series: [
      {
        type: 'sunburst',
        data: chartData,
        radius: [0, '90%'],
        label: {
          rotate: 'radial',
          fontSize: 12,
          color: '#333',
          formatter: params => {
            // label 显示状态简写
            if (params.data.status) {
              const map = { '正常': '✓', '警告': '!', '故障': '×', '离线': '-' };
              return `${params.name} ${map[params.data.status] || ''}`;
            }
            return params.name;
          }
        },
        itemStyle: {
          borderRadius: 6,
          borderWidth: 1,
          borderColor: '#fff'
        },
        emphasis: {
          focus: 'ancestor',
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(24,144,255,0.18)'
          }
        },
        levels: [
          {},
          {
            r0: '0%', r: '33%',
            label: { rotate: 0, fontSize: 13, color: '#1890ff' },
            itemStyle: { color: '#e6f7ff' }
          },
          {
            r0: '33%', r: '66%',
            label: { fontSize: 12 },
            itemStyle: { color: '#91d5ff' }
          },
          {
            r0: '66%', r: '90%',
            label: { fontSize: 11 },
            itemStyle: { color: '#bae7ff' }
          }
        ]
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
  height: 260px;
  min-width: 180px;
  min-height: 180px;
}
</style> 