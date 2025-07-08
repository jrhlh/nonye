<template>
  <div class="chart-container">
    <!-- 设备选择下拉框 -->
    <el-select
        v-model="selectedDevice"
        placeholder="选择设备"
        class="device-select"
        @change="handleDeviceChange"
    >
      <el-option
          v-for="item in deviceOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
          class="select-option"
      ></el-option>
    </el-select>

    <div ref="chartDom" style="width: 630px; height: 390px" class="wjk"></div>
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
import { ElSelect, ElOption } from 'element-plus'

// 添加设备选项数组
const deviceOptions = [
  { label: "设备A", value: "deviceA" },
  { label: "设备B", value: "deviceB" },
  { label: "设备C", value: "deviceC" },
  { label: "设备D", value: "deviceD" },
  { label: "设备E", value: "deviceE" },
  { label: "中心设备", value: "centerDevice" },
  { label: "设备F", value: "deviceF" }
]

// 其余代码保持不变...
const chartDom = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null
let currentStartDate = 1
let intervalId: number | null = null
const showAlert = ref(false)
const hasShownWarning = ref(false)
const selectedDevice = ref('deviceA')
const deviceData = ref<Record<string, number[]>>({})

// 生成随机湿度数据(40-90%之间)
const generateRandomMoisture = () => Math.floor(Math.random() * 50) + 40

// 初始化设备数据
const initDeviceData = () => {
  const devices = ['deviceA', 'deviceB', 'deviceC', 'deviceD', 'deviceE', 'centerDevice', 'deviceF']
  devices.forEach(device => {
    deviceData.value[device] = Array(5).fill(0).map(() => generateRandomMoisture())
    deviceData.value[device][10 % 5] = device === 'centerDevice' ? 95 : 90 + Math.floor(Math.random() * 5)
  })
}

// 初始配置选项
const option: echarts.EChartsOption = {
  title: {
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

const showWarningNotification = () => {
  if (!hasShownWarning.value) {
    showAlert.value = true
    hasShownWarning.value = true
  }
}

const emit = defineEmits()

const updateChartData = () => {
  const dates = []
  const moistureData = []

  for (let i = 0; i < 5; i++) {
    const currentDate = currentStartDate + i
    dates.push(currentDate.toString())

    if (selectedDevice.value && deviceData.value[selectedDevice.value]) {
      moistureData.push(deviceData.value[selectedDevice.value][i])
      if (currentDate === 11 && deviceData.value[selectedDevice.value][i] >= 90) {
        emit('handleWarning')
        showWarningNotification()
      }
    } else {
      if (currentDate === 11) {
        emit('handleWarning')
        moistureData.push(95)
        showWarningNotification()
      } else {
        moistureData.push(generateRandomMoisture())
      }
    }
  }

  if (myChart) {
    option.xAxis!.data = dates
    option.series![0].data = moistureData
    myChart.setOption(option, true)
  }

  currentStartDate++
}

const handleDeviceChange = () => {
  currentStartDate = 1
  hasShownWarning.value = false
  if (myChart) {
    updateChartData()
  }
}

const initChart = () => {
  initDeviceData()
  if (chartDom.value) {
    myChart = echarts.init(chartDom.value)
    updateChartData()
    intervalId = window.setInterval(updateChartData, 4000)
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

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

/* 设备选择下拉框样式 */
.device-select {
  position: absolute;
  top: -20px;
  right: 35px;
  width: 105px;
  z-index: 10;
}

/* 修改下拉框高度和文字颜色 */
:deep(.el-select) {
  height: 60px;
}

:deep(.el-input__inner) {
  height: 40px;
  line-height: 40px;
  color: #000000; /* 黑色文字 */
}

/* 下拉选项样式 */
:deep(.el-select-dropdown__item) {
  height: 40px;
  line-height: 40px;
  color: #000000; /* 黑色文字 */
  padding: 0 20px;
}

.wjk {
  padding-left: 20px;
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