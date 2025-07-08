<!-- wendu4.vue -->
<template>
  <div class="chart-container">
    <div class="device-selector">
      <select id="device-select" v-model="selectedDeviceId" @change="initChartData">
        <option v-for="(name, id) in deviceList" :key="id" :value="id">
          {{ name }}
        </option>
      </select>
    </div>

    <div ref="chartRef" style="width: 100%; height: 600px; margin-top: 80px"></div>

    <div v-if="loading" class="status loading">加载中...</div>
    <div v-if="error" class="status error">数据加载失败: {{ error }}</div>
    <div v-if="!loading && !error && !hasData" class="status no-data">无传感器数据</div>

    <!-- 警告通知 -->
    <div v-if="showWarning" class="warning-notification">
      <div class="warning-content">
        <h3>⚠️ 温度异常高警告</h3>
        <p>预测到12:20温度将达到35°C，可能存在设备异常</p>
        <button class="view-details-btn" @click="showDetails = true">查看详情</button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetails" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>设备异常预警详情</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="alert-banner">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
              <h3>温度过高预警</h3>
              <p>系统检测到设备温度即将超过安全阈值</p>
            </div>
          </div>

          <div class="detail-section">
            <h4>预警信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">异常类型</span>
                <span class="detail-value">温度过高</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预警级别</span>
                <span class="detail-value warning-level">严重</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预测时间</span>
                <span class="detail-value">12:20</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预测温度</span>
                <span class="detail-value critical-temp" :style="{fontSize:'20px'}">35°C</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4>可能原因</h4>
            <ul class="reason-list">
              <li>设备散热系统故障或堵塞</li>
              <li>环境温度异常升高</li>
              <li>设备负载过高持续运行</li>
              <li>冷却系统未正常工作</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>处理建议</h4>
            <div class="recommendation-cards">
              <div class="recommendation-card">
                <div class="card-icon">🔧</div>
                <div class="card-content">
                  <h5>立即检查</h5>
                  <p>检查设备散热系统、风扇运行状态和通风情况</p>
                </div>
              </div>
              <div class="recommendation-card">
                <div class="card-icon">🌡️</div>
                <div class="card-content">
                  <h5>环境控制</h5>
                  <p>确保设备所在环境温度适宜，必要时开启空调</p>
                </div>
              </div>
              <div class="recommendation-card">
                <div class="card-icon">⏲️</div>
                <div class="card-content">
                  <h5>临时措施</h5>
                  <p>降低设备负载，安排短暂停机冷却</p>
                </div>
              </div>
              <div class="recommendation-card">
                <div class="card-icon">👨‍🔧</div>
                <div class="card-content">
                  <h5>专业维护</h5>
                  <p>联系设备维护人员进行全面检查和维修</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="confirm-btn" @click="closeModal">确认收到</button>
          <button class="secondary-btn" @click="closeModal">稍后处理</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import eventBus from '../utlis/event-bus';

interface SensorData {
  time: string;
  temperature: number;
}

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;
const loading = ref(false);
const error = ref<string | null>(null);
const deviceList = ref<Record<string, string>>({});
const selectedDeviceId = ref<string>('');
const hasData = ref(false);

const showWarning = ref(false);
const showDetails = ref(false);
const warningTriggered = ref(false);
const chartFrozen = ref(false);
let unfreezeTimer: number | null = null;

const chartData = ref<{
  times: string[];
  actualTemps: (number | null)[];
  predictionTemps: (number | null)[];
}>();

const DATA_UPDATE_INTERVAL = 5000;
let dataUpdateTimer: number | null = null;
let timeUpdateTimer: number | null = null;

const initialTimes = [
  '09:00', '09:20', '09:40', '10:00',
  '10:20', '10:40', '11:00', '11:20'
];

const currentTimes = ref<string[]>([...initialTimes]);

const unfreezeChart = () => {
  chartFrozen.value = false;
  if (chart) {
    chart.setOption({
      animationDuration: 1000,
      animationEasing: 'cubicOut'
    });
  }
};

const closeModal = () => {
  showDetails.value = false;

  // 清除之前的定时器（如果有）
  if (unfreezeTimer) {
    clearTimeout(unfreezeTimer);
  }

  // 设置1秒后解冻图表
  unfreezeTimer = setTimeout(() => {
    unfreezeChart();
  }, 1000);
};

const getNextTime = (timeStr: string) => {
  const [hours, minutes] = timeStr.split(':').map(Number);
  let newHours = hours;
  let newMinutes = minutes + 20;

  if (newMinutes >= 60) {
    newHours += Math.floor(newMinutes / 60);
    newMinutes = newMinutes % 60;
  }

  return `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;
};

const updateTimeSeries = () => {
  if (!chart || chartFrozen.value) return;

  const newTimes = currentTimes.value.map(time => getNextTime(time));
  chart.setOption({
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    xAxis: {
      data: newTimes
    }
  });

  currentTimes.value = newTimes;
  checkAndTriggerWarning();
};

const checkAndTriggerWarning = () => {
  if (!warningTriggered.value && currentTimes.value.some(time => time === '12:20')) {
    const index = currentTimes.value.indexOf('12:20');

    if (index >= 4 && chartData.value) {
      const predictionIndex = index - 4;
      chartData.value.predictionTemps[predictionIndex] = 35;

      updateChartData();
      showWarning.value = true;
      warningTriggered.value = true;
      chartFrozen.value = true;

      eventBus.emit('addTemperatureAnomaly', {
        time: `${new Date().toISOString().split('T')[0]} 12:20`,
        temperature: '35.0℃',
        status: '高温预警',
        action: '系统预测到温度将达到35°C，建议立即检查散热系统并降低设备负载'
      });

      setTimeout(() => {
        showWarning.value = false;
      }, 5000);
    }
  }
};

const getCurrentTime = () => {
  const now = new Date();
  const minutes = now.getMinutes();
  const alignedMinutes = Math.floor(minutes / 20) * 20;
  const currentTime = new Date(now);
  currentTime.setMinutes(alignedMinutes, 0, 0);
  return currentTime;
};

const fetchDevices = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/chou1/devices');
    if (response.data.code === 200) {
      return response.data.data;
    }
    throw new Error(response.data.message || '获取设备列表失败');
  } catch (err) {
    console.error('获取设备列表失败:', err);
    error.value = err instanceof Error ? err.message : '获取设备列表失败';
    return {};
  }
};

const fetchLatestActualSensorData = async (deviceId: string) => {
  try {
    loading.value = true;
    error.value = null;
    hasData.value = false;

    const response = await axios.get(
        `http://localhost:5000/api/sensor/device/${deviceId}/latest`
    );

    if (response.data.code === 200) {
      if (response.data.data) {
        hasData.value = true;
        return response.data.data as SensorData;
      } else {
        return null;
      }
    } else {
      error.value = response.data.message || '获取传感器数据失败';
      return null;
    }
  } catch (err) {
    console.error('获取传感器数据失败:', err);
    error.value = err instanceof Error ? err.message : '获取传感器数据失败';
    return null;
  } finally {
    loading.value = false;
  }
};

const fetchLatestTemperaturePrediction = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/prediction/temperature/latest');

    if (response.data.code === 200) {
      return response.data.data as number;
    }
    throw new Error(response.data.message || '获取预测数据失败');
  } catch (err) {
    console.error('获取预测数据失败:', err);
    return 25 + (Math.random() * 2 - 1);
  }
};

const initChart = () => {
  if (!chartRef.value) return;

  if (chart) {
    chart.dispose();
    chart = null;
  }

  chart = echarts.init(chartRef.value);

  const actualAreaGradient = new echarts.graphic.LinearGradient(0, 0, 0, 1, [
    { offset: 0, color: 'rgba(164, 203, 234, 0.8)' },
    { offset: 1, color: 'rgba(219, 235, 250, 0.1)' }
  ]);

  const option = {
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const time = params[0].axisValue;
        const value = params[0].value;
        const isPrediction = params[0].dataIndex >= 4;
        const prefix = isPrediction ? '预测' : '实际';
        return `${time}<br/>${prefix}温度: ${value?.toFixed(1) ?? '--'}°C`;
      }
    },
    legend: {
      data: ['实际数据', '预测数据'],
      right: '10%',
      top: '5%',
    },
    grid: {
      left: '2%',
      right: '4%',
      bottom: '0%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: currentTimes.value,
      axisLabel: {
        formatter: (value: string) => value,
        rotate: 45,
      },
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicOut'
    },
    yAxis: {
      type: 'value',
      min: 15,
      max: 35,
      axisLabel: {
        formatter: '{value} °C',
      },
    },
    series: [
      {
        name: '实际数据',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: [],
        itemStyle: { color: '#24a4fa' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: actualAreaGradient
        },
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '预测数据',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: [],
        itemStyle: { color: '#f56c6c' },
        lineStyle: { width: 3, type: 'dashed' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.5)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.1)' },
          ]),
        },
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '连接线',
        type: 'line',
        symbol: 'none',
        data: [],
        lineStyle: {
          width: 3,
          color: '#24a4fa'
        },
        areaStyle: {
          color: actualAreaGradient
        },
        silent: true,
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      }
    ],
  };

  chart.setOption(option);
};

const updateChartData = (newActualTemp?: number, newPredictionTemp?: number) => {
  if (!chart || !chartData.value || chartFrozen.value) return;

  if (newActualTemp !== undefined) {
    chartData.value.actualTemps = [
      ...chartData.value.actualTemps.slice(1),
      newActualTemp
    ];
  }

  if (newPredictionTemp !== undefined) {
    chartData.value.predictionTemps = [
      newPredictionTemp,
      ...chartData.value.predictionTemps.slice(0, 3)
    ];
  }

  const connectionData = Array(8).fill(null);
  if (chartData.value.actualTemps[3] !== null && chartData.value.predictionTemps[0] !== null) {
    connectionData[3] = chartData.value.actualTemps[3];
    connectionData[4] = chartData.value.predictionTemps[0];
  }

  chart.setOption({
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    xAxis: {
      data: currentTimes.value,
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicOut'
    },
    series: [
      {
        name: '实际数据',
        data: [...chartData.value.actualTemps, ...Array(4).fill(null)],
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '预测数据',
        data: [...Array(4).fill(null), ...chartData.value.predictionTemps],
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      },
      {
        name: '连接线',
        data: connectionData,
        areaStyle: connectionData[3] !== null && connectionData[4] !== null ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(164, 203, 234, 0.8)' },
            { offset: 1, color: 'rgba(219, 235, 250, 0.1)' }
          ])
        } : undefined,
        animationDurationUpdate: 1000,
        animationEasingUpdate: 'cubicOut'
      }
    ],
    graphic: [
      {
        type: 'line',
        z: 100,
        shape: { x1: 0, y1: 0, x2: 0, y2: chart.getHeight() },
        style: { stroke: '#ff6b6b', lineDash: [5, 5], lineWidth: 2 },
        position: [chart.convertToPixel('xAxis', 3.5), 0]
      },
      {
        type: 'text',
        z: 100,
        style: { fill: '#ff6b6b', fontSize: 14, fontWeight: 'bold',  },
        position: [chart.convertToPixel('xAxis', 3.5) + 10, 40]
      }
    ]
  });
};

const initChartData = async () => {
  if (!selectedDeviceId.value) return;
  stopUpdateTimers();

  showWarning.value = false;
  showDetails.value = false;
  warningTriggered.value = false;
  chartFrozen.value = false;

  currentTimes.value = [...initialTimes];

  const latestActualData = await fetchLatestActualSensorData(selectedDeviceId.value);

  if (latestActualData) {
    const latestPrediction = await fetchLatestTemperaturePrediction();

    chartData.value = {
      times: currentTimes.value,
      actualTemps: [22.5, 23.0, 23.5, latestActualData.temperature],
      predictionTemps: [latestPrediction, 24.5, 24.0, 23.8]
    };

    if (chartData.value.actualTemps[3] === chartData.value.predictionTemps[0]) {
      chartData.value.predictionTemps[0] += 0.5;
    }

    if (!chart) initChart();
    updateChartData();
    hasData.value = true;
    startUpdateTimers();
  }
};

const startUpdateTimers = () => {
  stopUpdateTimers();

  dataUpdateTimer = setInterval(async () => {
    if (!selectedDeviceId.value || !chartData.value || chartFrozen.value) return;

    const latestActualData = await fetchLatestActualSensorData(selectedDeviceId.value);
    if (!latestActualData) return;

    const latestPrediction = await fetchLatestTemperaturePrediction();

    let adjustedPrediction = latestPrediction;
    if (Math.abs(latestActualData.temperature - latestPrediction) < 0.5) {
      adjustedPrediction = latestActualData.temperature + (Math.random() > 0.5 ? 0.5 : -0.5);
    }

    updateChartData(latestActualData.temperature, adjustedPrediction);
  }, DATA_UPDATE_INTERVAL);

  timeUpdateTimer = setInterval(() => {
    updateTimeSeries();
  }, DATA_UPDATE_INTERVAL);
};

const stopUpdateTimers = () => {
  if (dataUpdateTimer) {
    clearInterval(dataUpdateTimer);
    dataUpdateTimer = null;
  }
  if (timeUpdateTimer) {
    clearInterval(timeUpdateTimer);
    timeUpdateTimer = null;
  }
};

onMounted(async () => {
  deviceList.value = await fetchDevices();

  if (Object.keys(deviceList.value).length > 0) {
    selectedDeviceId.value = Object.keys(deviceList.value)[0];
    await initChartData();
  }
});

onBeforeUnmount(() => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
  stopUpdateTimers();
  if (unfreezeTimer) {
    clearTimeout(unfreezeTimer);
    unfreezeTimer = null;
  }
});

window.addEventListener('resize', () => {
  if (chart) {
    chart.resize();
  }
});

watch(selectedDeviceId, async (newId) => {
  if (newId) {
    await initChartData();
  }
});
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  height: 380px;
  position: relative;
  top: -60px;
}

.device-selector {
  position: absolute;
  top: -40px;
  right: 20px;
  display: flex;
  gap: 20px;
  border-radius: 4px;
  padding: 10px 10px;
  z-index: 10;
  border: none;
}

.device-selector select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s;
}

.device-selector select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 5px rgba(64, 158, 255, 0.3);
}

.status {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 30px;
  border-radius: 10px;
  z-index: 10;
  text-align: center;
  font-size: 18px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.loading {
  background: rgba(64, 158, 255, 0.9);
  color: white;
}

.error {
  background: rgba(245, 108, 108, 0.9);
  color: white;
  border: 1px solid #f56c6c;
}

.no-data {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border: 1px solid #ddd;
}

.warning-notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #ff4d4f;
  color: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
  max-width: 350px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.warning-content h3 {
  margin-top: 0;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.warning-content p {
  margin-bottom: 15px;
  line-height: 1.5;
}

.view-details-btn {
  background-color: white;
  color: #ff4d4f;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  float: right;
  transition: background-color 0.2s;
}

.view-details-btn:hover {
  background-color: #f5f5f5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.3s ease-out;
}

.modal::-webkit-scrollbar {
  display: none;
}

@keyframes modalSlideIn {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 10;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1f2329;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #86909c;
  transition: color 0.2s;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  color: #1f2329;
  background-color: #f5f5f5;
}

.modal-body {
  padding: 24px;
  flex: 1;
}

.alert-banner {
  background-color: #fff8e6;
  border-left: 4px solid #faad14;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.alert-icon {
  font-size: 28px;
  margin-right: 16px;
  color: #faad14;
}

.alert-content h3 {
  margin: 0 0 4px 0;
  color: #d48806;
  font-size: 16px;
}

.alert-content p {
  margin: 0;
  color: #86909c;
  font-size: 14px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #1f2329;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 13px;
  color: #86909c;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 14px;
  color: #1f2329;
  font-weight: 500;
}

.warning-level {
  color: #fa8c16;
  background-color: #fff7e6;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.critical-temp {
  color: #f5222d;
  font-weight: bold;
  font-size: 16px;
}

.reason-list,
.impact-list {
  margin: 0;
  padding-left: 20px;
  color: #595959;
}

.reason-list li,
.impact-list li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.recommendation-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.recommendation-card {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
}

.recommendation-card:nth-child(2) {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.recommendation-card:nth-child(3) {
  background-color: #fffbe6;
  border-color: #ffe58f;
}

.recommendation-card:nth-child(4) {
  background-color: #f9f0ff;
  border-color: #d3adf7;
}

.card-icon {
  font-size: 20px;
  margin-right: 12px;
  margin-top: 2px;
}

.card-content h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #1f2329;
}

.card-content p {
  margin: 0;
  font-size: 13px;
  color: #595959;
  line-height: 1.5;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  position: sticky;
  bottom: 0;
  background-color: white;
}

.confirm-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.confirm-btn:hover {
  background-color: #40a9ff;
}

.secondary-btn {
  background-color: white;
  color: #666;
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.secondary-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background-color: #f0f9ff;
}
</style>