<template>
  <div>
    <div ref="chartRef" style="width: 610px; height: 400px;position: relative;top: 20px;left: 5px"></div>
    <div v-if="error" class="error-message">
      Error loading/updating chart: {{ error }}
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)
const myChart = ref(null)
const error = ref(null)

// 模拟温州晴天的真实光照强度（单位：lux）
const generateLightIntensityData = (hour) => {
  let intensity = 0

  if (hour >= 5 && hour < 20) {
    // 日出到日落之间有光照
    const normalizedHour = (hour - 5) / 15 // 映射到 [0, 1]
    const peakTime = 0.5 // 正午12:30左右达到顶峰
    const curve = Math.exp(-Math.pow((normalizedHour - peakTime) * 3, 2)) // 高斯曲线
    intensity = 100000 * curve
  }

  // 添加±5%随机波动
  return Math.max(0, Math.min(100000, intensity * (1 + 0.05 * (Math.random() * 2 - 1))))
}

// 红蓝光比例模拟（清晨/傍晚偏红，正午偏蓝）
const generateRedBlueRatio = (hour) => {
  let ratio = 3

  if (hour >= 5 && hour < 20) {
    const normalizedHour = (hour - 5) / 15
    const peakTime = 0.5
    const curve = Math.sin(Math.PI * normalizedHour) // 正弦曲线模拟日光色温变化
    ratio = 4 - curve // 曲线范围：2.5 ~ 4.5
  }

  return Math.max(2.0, Math.min(4.0, ratio + 0.1 * (Math.random() * 2 - 1))).toFixed(1)
}

// 生成初始数据
const generateInitialData = () => {
  const now = new Date()
  const categories = []
  const lightData = []
  const ratioData = []

  for (let i = 9; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 2000)
    const hour = time.getHours() + time.getMinutes() / 60

    categories.push(time.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'}))
    lightData.push(generateLightIntensityData(hour))
    ratioData.push(generateRedBlueRatio(hour))
  }

  return {categories, lightData, ratioData}
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  if (myChart.value) myChart.value.dispose()

  const {categories, lightData, ratioData} = generateInitialData()
  myChart.value = echarts.init(chartRef.value)

  const option = {
    title: {text: '光照强度与红蓝光比例'},
    tooltip: {
      trigger: 'axis',
      axisPointer: {type: 'cross', label: {backgroundColor: '#283b56'}},
      formatter: (params) => {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color}"></span>`
          result += `${param.seriesName}: ${param.value} ${param.seriesIndex === 0 ? 'lux' : ' (红光:蓝光)'}`
          result += '<br/>'
        })
        return result
      }
    },
    legend: {data: ['光照强度', '红蓝光比例']},
    toolbox: {
      show: true,
      feature: {
        restore: {title: '重置'},
        saveAsImage: {title: '保存为图片'}
      }
    },
    xAxis: [{type: 'category', boundaryGap: true, data: categories}],
    yAxis: [
      {
        type: 'value',
        scale: true,
        name: '光照强度',
        max: 110000,
        min: 0,
        boundaryGap: [0.2, 0.2]
      },
      {
        type: 'value',
        scale: true,
        name: '红蓝光比例',
        min: 1,
        max: 4,
        interval: 1,
        boundaryGap: [0.2, 0.2]
      }
    ],
    series: [
      {
        name: '光照强度',
        type: 'bar',
        yAxisIndex: 0,
        data: lightData,
        itemStyle: {color: '#5470C6'}
      },
      {
        name: '红蓝光比例',
        type: 'line',
        yAxisIndex: 1,
        data: ratioData,
        lineStyle: {color: '#91CC75'},
        symbolSize: 6,
        symbol: 'circle',
        itemStyle: {color: '#fff', borderColor: '#91CC75', borderWidth: 2}
      }
    ]
  }

  myChart.value.setOption(option)
  startDynamicUpdate()
}

// 动态更新数据
let updateInterval = null
const startDynamicUpdate = () => {
  if (updateInterval) clearInterval(updateInterval)
  updateInterval = setInterval(() => {
    const {categories, lightData, ratioData} = generateInitialData()
    myChart.value.setOption({
      xAxis: [{data: categories}],
      series: [
        {data: lightData},
        {data: ratioData}
      ]
    })
  }, 2100)
}

onMounted(() => {
  try {
    initChart()
  } catch (err) {
    error.value = err.message
    console.error('Error initializing chart:', err)
  }
})

onBeforeUnmount(() => {
  if (updateInterval) clearInterval(updateInterval)
  if (myChart.value) myChart.value.dispose()
})
</script>

<style scoped>
.error-message {
  color: #f56c6c;
  margin-top: 16px;
  padding: 12px;
  border-radius: 4px;
  background-color: #fef0f0;
  position: relative;

}
</style>