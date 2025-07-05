<template>
  <div class="chart-container">
    <div ref="chartDom" style="width: 600px; height: 390px"></div>
    <div v-if="showAlert" class="alert-overlay">
      <div class="alert-box">
        <h3>湿度异常警告</h3>
        <p>检测到6月11日土壤湿度过高(95%)，请检查设备！</p>
        <button @click="showAlert = false">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const chartDom = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null
let currentStartDate = 1
let intervalId: number | null = null
const showAlert = ref(false)
const hasShownWarning = ref(false)

// 生成随机湿度数据(40-90%之间)
const generateRandomMoisture = () => Math.floor(Math.random() * 50) + 40

// 初始配置选项
const option: echarts.EChartsOption = {
  title: {
    text: '土壤湿度监测',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: [],
    boundaryGap: false,
    axisLabel: {
      formatter: (value: string) => `6.${value}日`
    }
  },
  yAxis: {
    type: 'value',
    max: 100,
    min: 0,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [{
    name: '土壤湿度',
    data: [],
    type: 'line',
    smooth: true,
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        {
          offset: 0,
          color: 'rgba(118,193,118,0.7)'
        },
        {
          offset: 1,
          color: 'rgba(144, 238, 144, 0.1)'
        }
      ])
    },
    itemStyle: {
      color: 'rgb(98,165,98)'
    },
    markLine: {
      data: [
        { type: 'average', name: '平均值' },
        {
          yAxis: 90,
          name: '警戒线',
          lineStyle: {
            color: 'red'
          },
          label: {
            formatter: '警戒线: {c}%',
            position: 'start'
          }
        }
      ]
    }
  }]
}

// 显示警告弹窗
const showWarningNotification = () => {
  if (!hasShownWarning.value) {
    showAlert.value = true
    hasShownWarning.value = true
  }
}

// 更新图表数据
const updateChartData = () => {
  const dates = []
  const moistureData = []

  // 生成5天的数据
  for (let i = 0; i < 5; i++) {
    const currentDate = currentStartDate + i
    dates.push(currentDate.toString())

    // 6月14日显示异常湿度95%
    if (currentDate === 11) {
      moistureData.push(95)
      showWarningNotification()
    } else {
      moistureData.push(generateRandomMoisture())
    }
  }

  if (myChart) {
    option.xAxis!.data = dates
    option.series![0].data = moistureData
    myChart.setOption(option, true)
  }

  // 每4秒增加一天
  currentStartDate++
}

// 初始化图表
const initChart = () => {
  if (chartDom.value) {
    myChart = echarts.init(chartDom.value)
    updateChartData()
    // 启动定时器，每4秒更新一次数据
    intervalId = window.setInterval(updateChartData, 4000)
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

// 窗口大小变化时调整图表
const resizeChart = () => {
  if (myChart) {
    myChart.resize()
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  if (intervalId) {
    clearInterval(intervalId)
  }
  if (myChart) {
    myChart.dispose()
    myChart = null
  }
  // 重置警告状态
  hasShownWarning.value = false
})
</script>

<style scoped>
.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  top: -40px;
}

.alert-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.alert-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.alert-box h3 {
  color: #d32f2f;
  margin-top: 0;
}

.alert-box p {
  margin: 10px 0;
}

.alert-box button {
  background: #d32f2f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}
</style>