<template>
  <div class="growth-trend-card">
    <div class="card-header">
      <div class="header-content">
        <div class="title-section">
          <h3 class="card-title">生长趋势分析</h3>
          <p class="card-subtitle">实时监测作物生长状态和趋势预测</p>
        </div>
        <div class="crop-info">
          <div class="crop-icon">
            <Sprout :size="24" />
          </div>
          <div class="crop-details">
            <h4>水稻</h4>
            <span class="crop-variety">早籼稻</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-refresh" @click="refreshData" :disabled="loading">
          <RefreshCw :size="16" :class="{ 'spinning': loading }" />
        </button>
        <button class="btn-expand" @click="showDetails = !showDetails">
          <ChevronDown :size="16" :class="{ 'rotated': showDetails }" />
        </button>
      </div>
    </div>

    <div class="card-body">
      <!-- 生长状态概览 -->
      <div class="growth-overview">
        <div class="overview-item">
          <div class="overview-icon">
            <TrendingUp :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">生长阶段</span>
            <span class="overview-value">分蘖期</span>
          </div>
        </div>
        <div class="overview-item">
          <div class="overview-icon">
            <Calendar :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">生长天数</span>
            <span class="overview-value">{{ growthDays }}天</span>
          </div>
        </div>
        <div class="overview-item">
          <div class="overview-icon">
            <Target :size="20" />
          </div>
          <div class="overview-content">
            <span class="overview-label">健康指数</span>
            <span class="overview-value">{{ healthIndex }}%</span>
          </div>
        </div>
      </div>

      <!-- 趋势图表 -->
      <div class="chart-container">
        <div class="chart-header">
          <h4>30天生长趋势</h4>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color height"></span>
              <span>株高 (cm)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color leaf"></span>
              <span>叶片数</span>
            </div>
            <div class="legend-item">
              <span class="legend-color tiller"></span>
              <span>分蘖数</span>
            </div>
          </div>
        </div>
        <div class="chart-wrapper">
          <v-chart 
            class="growth-chart" 
            :option="chartOption" 
            :autoresize="true"
            :loading="loading"
          />
        </div>
      </div>

      <!-- 可展开的详细信息 -->
      <Transition name="slide-down">
        <div v-if="showDetails" class="details-section">
          <div class="details-grid">
            <div class="detail-card">
              <div class="detail-header">
                <Sun :size="18" />
                <h5>气候适应性</h5>
              </div>
              <div class="detail-content">
                <p>当前气温：15-25℃，适合水稻生长</p>
                <p>降水量充足，土壤湿度适中</p>
              </div>
            </div>
            
            <div class="detail-card">
              <div class="detail-header">
                <DollarSign :size="18" />
                <h5>经济效益</h5>
              </div>
              <div class="detail-content">
                <p>市场需求旺盛</p>
                <p>预计亩产量：<strong>450-500公斤</strong></p>
              </div>
            </div>
            
            <div class="detail-card">
              <div class="detail-header">
                <Droplets :size="18" />
                <h5>土壤建议</h5>
              </div>
              <div class="detail-content">
                <p>PH值6.5-7.5，肥沃的壤土</p>
                <p>保持适当水分</p>
              </div>
            </div>
            
            <div class="detail-card">
              <div class="detail-header">
                <Shield :size="18" />
                <h5>病虫害防治</h5>
              </div>
              <div class="detail-content">
                <p>注意防治稻瘟病和稻飞虱</p>
                <p>定期检查叶片状态</p>
              </div>
            </div>
            
            <div class="detail-card">
              <div class="detail-header">
                <Sprout :size="18" />
                <h5>施肥建议</h5>
              </div>
              <div class="detail-content">
                <p>基肥充足，分蘖肥和穗肥结合</p>
                <p>氮磷钾比例：2:1:1</p>
              </div>
            </div>
            
            <div class="detail-card">
              <div class="detail-header">
                <AlertTriangle :size="18" />
                <h5>注意事项</h5>
              </div>
              <div class="detail-content">
                <p>避免过度灌溉</p>
                <p>及时除草和病虫害防治</p>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { 
  RefreshCw, 
  ChevronDown, 
  TrendingUp, 
  Calendar, 
  Target,
  Sun,
  DollarSign,
  Droplets,
  Shield,
  Sprout,
  AlertTriangle
} from 'lucide-vue-next';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components';
import VChart from 'vue-echarts';

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
]);

// 响应式数据
const loading = ref(false);
const showDetails = ref(false);
const growthDays = ref(45);
const healthIndex = ref(92);

// 生成模拟数据
const generateGrowthData = () => {
  const days = 30;
  const heightData: string[] = [];
  const leafData: number[] = [];
  const tillerData: number[] = [];
  
  for (let i = 0; i < days; i++) {
    // 株高：从20cm开始，每天增长1-3cm
    const height = 20 + i * 2.5 + Math.random() * 2;
    heightData.push(height.toFixed(1));
    
    // 叶片数：从3片开始，每5天增加1片
    const leaves = 3 + Math.floor(i / 5) + (Math.random() > 0.7 ? 1 : 0);
    leafData.push(leaves);
    
    // 分蘖数：从1个开始，每3天增加1-2个
    const tillers = 1 + Math.floor(i / 3) * 1.5 + Math.random() * 2;
    tillerData.push(Math.floor(tillers));
  }
  
  return { heightData, leafData, tillerData };
};

const { heightData, leafData, tillerData } = generateGrowthData();

// 图表配置
const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: 'rgba(0, 0, 0, 0.1)',
    borderWidth: 1,
    textStyle: {
      color: '#333'
    },
    formatter: function(params: any) {
      let result = `<div style="font-weight: 600; margin-bottom: 8px;">第${params[0].dataIndex + 1}天</div>`;
      params.forEach((param: any) => {
        const color = param.color;
        const value = param.value;
        const name = param.seriesName;
        result += `
          <div style="display: flex; align-items: center; margin: 4px 0;">
            <span style="display: inline-block; width: 12px; height: 12px; background: ${color}; border-radius: 2px; margin-right: 8px;"></span>
            <span style="flex: 1;">${name}:</span>
            <span style="font-weight: 600;">${value}</span>
          </div>
        `;
      });
      return result;
    }
  },
  legend: {
    show: false
  },
  xAxis: {
    type: 'category',
    data: Array.from({ length: 30 }, (_, i) => i + 1),
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    },
    axisTick: {
      show: false
    },
    axisLabel: {
      color: '#666',
      fontSize: 12
    }
  },
  yAxis: [
    {
      type: 'value',
      name: '株高 (cm)',
      nameTextStyle: {
        color: '#666',
        fontSize: 12
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.05)',
          type: 'dashed'
        }
      }
    },
    {
      type: 'value',
      name: '数量',
      nameTextStyle: {
        color: '#666',
        fontSize: 12
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontSize: 12
      },
      splitLine: {
        show: false
      }
    }
  ],
  series: [
    {
      name: '株高',
      type: 'line',
      yAxisIndex: 0,
      data: heightData,
      smooth: true,
      lineStyle: {
        color: '#10b981',
        width: 3
      },
      itemStyle: {
        color: '#10b981'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16, 185, 129, 0.2)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
          ]
        }
      },
      symbol: 'circle',
      symbolSize: 6
    },
    {
      name: '叶片数',
      type: 'line',
      yAxisIndex: 1,
      data: leafData,
      smooth: true,
      lineStyle: {
        color: '#3b82f6',
        width: 3
      },
      itemStyle: {
        color: '#3b82f6'
      },
      symbol: 'circle',
      symbolSize: 6
    },
    {
      name: '分蘖数',
      type: 'line',
      yAxisIndex: 1,
      data: tillerData,
      smooth: true,
      lineStyle: {
        color: '#f59e0b',
        width: 3
      },
      itemStyle: {
        color: '#f59e0b'
      },
      symbol: 'circle',
      symbolSize: 6
    }
  ]
}));

// 刷新数据
const refreshData = async () => {
  loading.value = true;
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    growthDays.value = Math.floor(Math.random() * 20) + 40;
    healthIndex.value = Math.floor(Math.random() * 10) + 85;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // 组件挂载后的初始化
});
</script>

<style scoped>
.growth-trend-card {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
}

.growth-trend-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 255, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  flex: 1;
}

.title-section {
  flex: 1;
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

.crop-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.crop-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--gradient-primary);
  border-radius: var(--radius-lg);
  color: white;
}

.crop-details h4 {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.crop-variety {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-refresh,
.btn-expand {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.8);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-refresh:hover,
.btn-expand:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

.rotated {
  transform: rotate(180deg);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.card-body {
  padding: var(--spacing-2xl);
}

.growth-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
}

.overview-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
}

.overview-item:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.overview-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--gradient-primary);
  border-radius: var(--radius-lg);
  color: white;
}

.overview-content {
  display: flex;
  flex-direction: column;
}

.overview-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
}

.overview-value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  background: rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.chart-header h4 {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: var(--spacing-lg);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.height {
  background: #10b981;
}

.legend-color.leaf {
  background: #3b82f6;
}

.legend-color.tiller {
  background: #f59e0b;
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

.growth-chart {
  width: 100%;
  height: 100%;
}

.details-section {
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-2xl);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
}

.detail-card {
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
}

.detail-card:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.detail-header h5 {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin: 0;
}

.detail-content p {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: var(--spacing-xs) 0;
  line-height: 1.6;
}

.detail-content strong {
  color: var(--text-primary);
  font-weight: 600;
}

/* 过渡动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .growth-overview {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .chart-legend {
    flex-wrap: wrap;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style> 