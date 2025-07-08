<script setup lang="ts">
import Wendu2 from "../components2/wendu2.vue";
import wendu3 from "../components2/wendu3.vue";
import Turang2 from "../components2/turang2.vue";
import Shidu2 from "../components2/shidu2.vue";
import Shidu3 from "../components2/shidu3.vue";
import Ph from "../components2/ph.vue";
import Ph3 from "../components2/ph3.vue";
import Guang2 from "../components2/guang2.vue";
import finding2 from "../components2/finding2.vue";
import Askai from "../components1/askai.vue";
import { ref, onMounted, nextTick } from 'vue';
import { ElMessageBox, ElNotification, ElDialog, ElMessage } from 'element-plus';
import axios from 'axios';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const drawerVisible = ref(false);
const drawerVisibleHumidity = ref(false);
const drawerVisiblePh = ref(false);
const progressValue = ref(85);
const isExporting = ref(false);

// PDF preview related
const pdfModalVisible = ref(false);
const pdfModalContent = ref<HTMLElement | null>(null);

// Report export related
const exportReportDialogVisible = ref(false);
const isReportLoading = ref(false);
const reportErrorMessage = ref('');
const isDownloadReady = ref(false);

// Data related
const currentTemperature = ref('27.5');
const isTemperatureLoading = ref(true);
const currentPh = ref('6.5');
const currentHumidity = ref('34%');
const currentLightIntensity = ref('0');
const maintenanceSuggestions = ref<{
  deviceName: string;
  warningType: string;
  warningValue?: number;
  urgent: boolean;
  faultDescription?: string;
  timestamp?: string;
}[]>([]);
const isMaintenanceLoading = ref(false);

// 添加标志跟踪关键温度警告是否已显示
const hasCriticalTemperatureWarning = ref(false);

// Simulated abnormal status
const isTemperatureAbnormal = ref(false);
const isHumidityAbnormal = ref(false);
const hasCriticalHumidityWarning = ref(false);

// Enhanced maintenance suggestions with faster response
const fetchMaintenanceSuggestions = () => {
  // 检查是否已经显示关键温度警告，如果是则跳过更新
  if (hasCriticalTemperatureWarning.value) {
    return;
  }

  isMaintenanceLoading.value = true;

  // Simulate faster response (500ms instead of 800ms)
  setTimeout(() => {
    const suggestions = [];

    // Default normal status
    if (!isTemperatureAbnormal.value && !isHumidityAbnormal.value) {
      suggestions.push({
        deviceName: '所有设备',
        warningType: 'normal',
        urgent: false,
        faultDescription: '设备运行正常',
        timestamp: new Date().toLocaleString()
      });
    }

    // Temperature alerts - 保持不变
    if (isTemperatureAbnormal.value) {
    }
    //
    maintenanceSuggestions.value = suggestions;
    isMaintenanceLoading.value = false;
  }, 500); // Reduced from 800ms to 500ms for faster response
};

const handleWarning = (value) => {
  if(maintenanceSuggestions.value.length >= 2) return
  if(value === 1) {
    maintenanceSuggestions.value = []
    maintenanceSuggestions.value.push({
      deviceName: '温度传感器',
      warningType: 'temperature_high',
      warningValue: 32,
      urgent: true,
      faultDescription: '6月8日检测到温度异常高(38°C)',
      timestamp: new Date().toLocaleString()
    });
  }
  if(value === 2) {
    maintenanceSuggestions.value.push({
      deviceName: '湿度传感器',
      warningType: 'temperature_high',
      warningValue: 38,
      urgent: true,
      faultDescription: '6月11日检测到湿度异常高(95°C)',
      timestamp: '2025-06-08 14:30'
    });
  }
  hasCriticalTemperatureWarning.value = true;
}

// 计算温州地区当前时间的光照强度（模拟）
const calculateWenzhouLightIntensity = () => {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const month = now.getMonth();

  // 简单模拟温州地区不同季节的日照时长和强度
  // 假设夏季日照时间长，强度高；冬季日照时间短，强度低
  let maxIntensity = 0;
  let sunrise = 0;
  let sunset = 0;

  // 夏季（6-8月）
  if (month >= 5 && month <= 7) {
    sunrise = 5; // 5:00
    sunset = 19; // 19:00
    maxIntensity = 120000; // 夏季最大光照强度
  }
  // 春季和秋季
  else if ((month >= 2 && month <= 4) || (month >= 8 && month <= 10)) {
    sunrise = 6; // 6:00
    sunset = 18; // 18:00
    maxIntensity = 80000; // 春秋季最大光照强度
  }
  // 冬季
  else {
    sunrise = 7; // 7:00
    sunset = 17; // 17:00
    maxIntensity = 50000; // 冬季最大光照强度
  }

  // 计算当前时间在日照时间中的位置（0-1）
  const dayProgress = (hours + minutes / 60 - sunrise) / (sunset - sunrise);

  // 如果在日照时间内
  if (dayProgress >= 0 && dayProgress <= 1) {
    // 使用正弦曲线模拟光照强度变化（中午最强，早晚较弱）
    const intensity = Math.round(Math.sin(dayProgress * Math.PI) * maxIntensity);
    return Math.max(0, intensity); // 确保不低于0
  }

  // 非日照时间
  return 0;
};

// Simulate getting temperature data
const fetchDeviceATemperature = async () => {
  try {
    isTemperatureLoading.value = true;
    currentTemperature.value = isTemperatureAbnormal.value ? '32.5°C' : '27.5°C';
  } catch (error) {
    console.error('获取温度数据失败:', error);
    currentTemperature.value = '获取失败';
  } finally {
    isTemperatureLoading.value = false;
  }
};

// Simulate getting humidity data - 修改为66%-75%随机
const fetchHumidityData = async () => {
  try {
    // 生成66到75之间的随机湿度值
    const randomHumidity = Math.floor(66 + Math.random() * 9); // 66 + (0-8.999...) => 66-74.999... => 66-74
    currentHumidity.value = `${randomHumidity}%`;
  } catch (error) {
    console.error('获取湿度数据失败:', error);
    currentHumidity.value = '获取失败';
  }
};

// Simulate getting pH data - 修改为6.6-7.3随机
const fetchPhData = async () => {
  try {
    // 生成6.6到7.3之间的随机PH值
    const randomPh = (6.6 + Math.random() * 0.7).toFixed(1); // 6.6 + (0-0.699...) => 6.6-7.299... => 6.6-7.3
    currentPh.value = randomPh;
  } catch (error) {
    console.error('获取pH数据失败', error);
    currentPh.value = '获取失败';
  }
};

const handleClose = (done: () => void) => {
  ElMessageBox.confirm('确定要关闭此分析页面吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
      .then(() => done())
      .catch(() => {});
};

const exportToPDF = async () => {
  try {
    isExporting.value = true;
    ElNotification({
      title: '正在准备报表',
      message: '正在生成报表预览...',
      type: 'info',
      duration: 2000
    });

    await Promise.all([
      fetchDeviceATemperature(),
      fetchPhData(),
      fetchHumidityData()
    ]);

    pdfModalVisible.value = true;
    await nextTick();
  } catch (error) {
    console.error('生成预览失败:', error);
    ElNotification({
      title: '错误',
      message: '生成预览时出错: ' + (error as Error).message,
      type: 'error',
      duration: 5000
    });
  } finally {
    isExporting.value = false;
  }
};

const downloadPDF = async () => {
  try {
    isReportLoading.value = true;
    isDownloadReady.value = false;

    const element = pdfModalContent.value;
    if (!element) throw new Error('找不到要导出的内容');

    ElMessage({
      message: '正在生成PDF...',
      type: 'loading',
      duration: 0,
      center: true
    });

    const canvas = await html2canvas(element, {
      scale: 3,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      logging: false
    });

    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm'
    });

    const imgData = canvas.toDataURL('image/jpeg', 0.95);
    const imgWidth = pdf.internal.pageSize.getWidth() - 20;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    pdf.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);

    const fileName = `农业环境分析报告_${new Date().toLocaleDateString().replace(/\//g, '-')}.pdf`;
    pdf.save(fileName);

    isReportLoading.value = false;
    isDownloadReady.value = true;

    ElMessage.closeAll();
    ElNotification({
      title: '导出成功',
      message: `报表已成功导出为 ${fileName}`,
      type: 'success',
      duration: 5000
    });

    pdfModalVisible.value = false;
  } catch (error) {
    isReportLoading.value = false;
    isDownloadReady.value = false;

    ElMessage.closeAll();
    console.error('导出PDF失败:', error);
    ElNotification({
      title: '导出失败',
      message: '生成PDF时出错: ' + (error as Error).message,
      type: 'error',
      duration: 5000
    });
  }
};

const suggestionText = (suggestion: {
  deviceName: string;
  warningType: string;
  urgent: boolean;
  faultDescription?: string;
}) => {
  if (suggestion.faultDescription) {
    const timeInfo = suggestion.timestamp ? `` : '';
    return `${suggestion.deviceName}检测到${suggestion.faultDescription}`;
  }

  switch (suggestion.warningType) {
    case 'temperature_high':
      return `${suggestion.deviceName}温度持续异常，请立即检查散热系统`;
    case 'humidity_high':
      return `${suggestion.deviceName}湿度持续异常，请检查灌溉系统`;
    case 'ph_abnormal':
      return `${suggestion.deviceName}pH值持续异常，请检查液体成分`;
    default:
      return `${suggestion.deviceName}运行正常`;
  }
};

const handleExportReport = async () => {
  try {
    isReportLoading.value = true;
    isDownloadReady.value = false;
    reportErrorMessage.value = '';

    await exportToPDF();
  } catch (error: any) {
    console.error('导出报表失败:', error);
    reportErrorMessage.value = error.message || '生成报表时出错';

    ElNotification({
      title: '导出失败',
      message: reportErrorMessage.value,
      type: 'error',
      duration: 5000
    });
  }
};

const handleDownloadReport = () => {
  exportToPDF();
};

const closeExportDialog = () => {
  exportReportDialogVisible.value = false;
};

const handlePdfClose = (done: () => void) => {
  ElMessageBox.confirm('确定要关闭报表预览吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
      .then(() => {
        done();
      })
      .catch(() => {});
};

// Simulate environment changes
const simulateEnvironmentChange = () => {
  isTemperatureAbnormal.value = Math.random() > 0.7;
  isHumidityAbnormal.value = Math.random() > 0.7;

  // 计算温州地区当前光照强度
  currentLightIntensity.value = calculateWenzhouLightIntensity().toString();

  fetchDeviceATemperature();
  fetchHumidityData();
  fetchPhData();
  fetchMaintenanceSuggestions();
};

onMounted(() => {
  fetchDeviceATemperature();
  fetchPhData();
  fetchHumidityData();
  currentLightIntensity.value = calculateWenzhouLightIntensity().toString();

  // 每5秒更新一次环境数据（修改为5秒）
  setInterval(simulateEnvironmentChange, 5000);
});

</script>

<template>
  <!-- 模板部分保持不变 -->
  <div id="all">
    <!-- Fixed top data cards -->
    <div class="top-container">
      <div class="box">
        <div class="data-container">
          <div class="number">{{ currentTemperature }}</div>
          <svg t="1747892350883" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6895" width="200" height="200"><path d="M752.65536 220.16c-59.38176 0-107.52 48.13824-107.52 107.52s48.13824 107.52 107.52 107.52 107.52-48.13824 107.52-107.52-48.13824-107.52-107.52-107.52z m0 61.44a46.08 46.08 0 1 1 0 92.16 46.08 46.08 0 0 1 0-92.16zM396.83584 51.22048C313.17504 52.57728 245.77536 120.81664 245.77536 204.8v365.85472l-1.65888 1.50016c-67.5072 61.5168-92.68736 157.81888-62.59712 245.22752 32.01024 92.98944 119.51104 155.40736 217.856 155.40736 98.33984 0 185.84064-62.41792 217.856-155.40736l0.93696-2.7904c28.60544-86.66112 3.2512-181.57568-63.5392-242.43712l-1.65376-1.49504V204.8c0-84.83328-68.77184-153.6-153.6-153.6l-2.53952 0.02048zM399.37536 112.64c50.8928 0 92.16 41.26208 92.16 92.16v380.2624l0.01536 1.15712c0.36864 10.73664 5.77024 19.14368 13.312 24.2176l0.1536 0.09216 1.97632 1.60768A168.96 168.96 0 1 1 239.616 797.38368l-0.7424-2.2016a168.96 168.96 0 0 1 52.85888-183.02976l1.9968-1.62304 0.1536-0.09728c7.81312-5.25312 13.33248-14.08 13.33248-25.37472V204.8c0-50.89792 41.26208-92.16 92.16-92.16z" fill="#2ECC71" p-id="6896"></path><path d="M399.37536 634.88c-59.38176 0-107.52 48.13824-107.52 107.52s48.13824 107.52 107.52 107.52 107.52-48.13824 107.52-107.52-48.13824-107.52-107.52-107.52z m0 61.44a46.08 46.08 0 1 1 0 92.16 46.08 46.08 0 0 1 0-92.16z" fill="#2ECC71" p-id="6897"></path><path d="M399.37536 327.68a30.72 30.72 0 0 1 30.69952 29.568l0.02048 1.152v307.2a30.72 30.72 0 0 1-61.41952 1.152l-0.02048-1.152V358.4a30.72 30.72 0 0 1 30.72-30.72z" fill="#2ECC71" p-id="6898"></path></svg>
          <div class="label1">平均温度</div>
        </div>
      </div>
      <div class="box">
        <div class="data-container">
          <div class="number">{{ currentHumidity }}</div>
          <svg t="1747892908314" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="37543" width="200" height="200"><path d="M424.3456 0h-0.068267a43.690667 43.690667 0 0 0-33.109333 15.223467C354.645333 58.026667 34.133333 439.159467 34.133333 638.293333 34.133333 851.012267 209.851733 1024 425.847467 1024c215.995733 0 391.7824-172.987733 391.7824-385.6384 0-199.338667-323.3792-580.471467-360.2432-623.274667A43.690667 43.690667 0 0 0 424.3456 0z m1.501867 938.666667c-168.209067 0-305.015467-134.690133-305.015467-300.305067 0-127.931733 195.857067-395.6736 303.650133-528.452267 108.7488 132.7104 306.449067 400.452267 306.449067 528.452267 0 165.614933-136.874667 300.305067-305.083733 300.305067zM873.198933 0s-115.575467 135.441067-115.575466 198.587733c0 63.146667 51.950933 114.2784 116.053333 114.2784 64.170667 0 116.189867-51.2 116.189867-114.2784C989.866667 135.441067 873.198933 0 873.198933 0z" fill="#f7c244" p-id="37544"></path><path d="M243.370667 434.312533C205.141333 494.045867 170.666667 520.055467 170.666667 600.405333c0 158.5152 127.044267 283.101867 259.003733 283.101867S684.714667 783.701333 684.714667 625.117867c0-25.463467 0-37.341867-12.0832-71.953067-1.2288-3.549867-17.681067-35.976533-18.8416-39.3216-6.826667-20.2752-52.155733-40.072533-68.130134-29.627733-16.315733 10.6496-35.498667 21.162667-57.344 25.531733-75.434667 15.086933-97.211733 2.048-150.869333-30.242133-50.312533-30.242133-109.704533-83.217067-134.075733-45.192534z" fill="#f7d37e" p-id="37545"></path></svg>
          <div class="label1">平均湿度</div>
        </div>
      </div>
      <div class="box">
        <div class="data-container">
          <div class="number">{{ currentPh }}</div>
          <svg t="1747893022949" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="40565" width="200" height="200"><path d="M597.930667 364.987733l-0.802134-2.542933-0.853333-3.6352a34.133333 34.133333 0 0 1-0.392533-3.003733l-0.136534-3.0208V154.1632a34.133333 34.133333 0 0 1 68.181334-2.56l0.085333 2.56v188.893867l277.8624 425.130666 1.501867 2.525867c35.9936 66.986667-10.632533 148.4288-85.572267 151.074133l-3.754667 0.068267H169.949867c-75.861333 0-124.330667-80.3328-91.0848-147.780267l1.723733-3.362133 1.501867-2.5088L359.9872 343.04V153.0368a34.133333 34.133333 0 0 1 31.573333-34.048l2.56-0.085333a34.133333 34.133333 0 0 1 34.048 31.573333l0.085334 2.56v199.8336a34.133333 34.133333 0 0 1-0.6656 6.690133l-0.7168 3.003734a34.133333 34.133333 0 0 1-2.6624 6.690133l-1.655467 2.816L140.288 803.959467l-0.648533 1.365333c-9.728 21.6064 4.898133 46.4896 27.8528 48.1792l2.491733 0.085333h684.066133c24.3712 0 40.3968-25.873067 30.344534-48.247466l-0.682667-1.3824-282.2144-431.8208a34.133333 34.133333 0 0 1-3.549867-7.150934z" fill="#444444" p-id="40566"></path><path d="M716.8 102.4a34.133333 34.133333 0 0 1 2.56 68.164267L716.8 170.666667H307.2a34.133333 34.133333 0 0 1-2.56-68.181334L307.2 102.4h409.6z" fill="#444444" p-id="40567"></path><path d="M699.733333 699.733333v34.133334a34.133333 34.133333 0 0 1-34.133333 34.133333H358.4a34.133333 34.133333 0 0 1-34.133333-34.133333v-34.133334h375.466666z" fill="#00B386" p-id="40568"></path></svg>
          <div class="label">平均PH值</div>
        </div>
      </div>
      <div class="box">
        <div class="data-container">
          <div class="number">{{ currentLightIntensity }}</div>
          <svg t="1747893107823" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="41680" width="200" height="200"><path d="M512 256c141.385 0 256 114.615 256 256S653.385 768 512 768 256 653.385 256 512s114.615-256 256-256z m0 64c-106.039 0-192 85.961-192 192s85.961 192 192 192 192-85.961 192-192-85.961-192-192-192z" fill="#d81e06" p-id="41681"></path><path d="M480 64m32 0l0 0q32 0 32 32l0 64q0 32-32 32l0 0q-32 0-32-32l0-64q0-32 32-32Z" fill="#d81e06" p-id="41682"></path><path d="M883.979626 260.287187m16 27.712813l0 0q16 27.712813-11.712813 43.712813l-55.425626 32q-27.712813 16-43.712813-11.712813l0 0q-16-27.712813 11.712813-43.712813l55.425626-32q27.712813-16 43.712813 11.712813Z" fill="#d81e06" p-id="41683"></path><path d="M915.979626 708.287187m-16 27.712813l0 0q-16 27.712813-43.712813 11.712813l-55.425626-32q-27.712813-16-11.712813-43.712813l0 0q16-27.712813 43.712813-11.712813l55.425626 32q27.712813 16 11.712813 43.712813Z" fill="#d81e06" p-id="41684"></path><path d="M544 960m-32 0l0 0q-32 0-32-32l0-64q0-32 32-32l0 0q32 0 32 32l0 64q0 32-32 32Z" fill="#d81e06" p-id="41685"></path><path d="M140.020374 763.712813m-16-27.712813l0 0q-16-27.712813 11.712813-43.712813l55.425626-32q27.712813-16 43.712813 11.712813l0 0q16 27.712813-11.712813 43.712813l-55.425626 32q-27.712813 16-43.712813-11.712813Z" fill="#d81e06" p-id="41686"></path><path d="M108.020374 315.712813m16-27.712813l0 0q16-27.712813 43.712813-11.712813l55.425626 32q27.712813 16 11.712813 43.712813l0 0q-16 27.712813-43.712813 11.712813l-55.425626-32q-27.712813-16-11.712813-43.712813Z" fill="#d81e06" p-id="41687"></path></svg>
          <div class="label">光照强度</div>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="body">
      <div class="body-top-box">
        <!-- Temperature content -->
        <div class="body-top-temp">
          <h3 class="clickable-area" @click="drawerVisible = true">设备温度日志表柱形图</h3>
          <wendu2 @handleWarning="handleWarning(1)"/>
        </div>
        <!-- Humidity content -->
        <div class="body-top-shidu">
          <h3 class="clickable-area01" @click="drawerVisibleHumidity = true" >设备湿度日志图</h3>
          <shidu2 @handleWarning="handleWarning(2)" class="uu"/>
        </div>
      </div>
      <div class="body-middle-box">
        <!-- pH content -->
        <div class="body-mid-ph">
          <h3 class="clickable-area" @click="drawerVisiblePh = true">PH值的散点分布图</h3>
          <ph/>
        </div>
        <div class="body-mid-guang">
          <guang2 class="gg1"/>
        </div>
      </div>
      <div class="under-box">
        <div class="body-under">
          <turang2/>
        </div>
        <div class="body-under-right">
          <finding2/>
        </div>
      </div>

      <!-- Smart analysis section -->
      <div class="smart-analysis-container">
        <div class="analysis-header">
          <h2 class="analysis-title">智能分析</h2>
          <button class="baobiao-button" @click="handleExportReport">
            导出报表
          </button>
        </div>
        <div class="confidence-section">
          <h3 class="section-title">故障预测置信度</h3>
          <div class="custom-progress-bar">
            <div class="progress-background"></div>
            <div class="progress-fill" :style="{ width: progressValue + '%' }"></div>
          </div>
          <div class="confidence-value">85%</div>
        </div>
        <div class="maintenance-section">
          <h3 class="section-title">异常检测</h3>
          <ul class="maintenance-list" v-if="!isMaintenanceLoading && maintenanceSuggestions.length > 0">
            <li
                v-for="(suggestion, index) in maintenanceSuggestions"
                :key="index"
                :class="['maintenance-item', { 'urgent': suggestion.urgent }]"
            >
              <span class="item-icon" :class="suggestion.urgent ? 'urgent-icon' : 'normal-icon'">
                {{ suggestion.urgent ? '!' : '✓' }}
              </span>
              <span class="item-text">{{ suggestionText(suggestion) }}</span>
            </li>
          </ul>
          <div v-else-if="isMaintenanceLoading" class="loading-container">
            <span class="item-icon">⌛</span>
            <span class="item-text">正在加载维护建议...</span>
          </div>
        </div>

        <div>
          <askai />
        </div>
      </div>
    </div>
    <!-- Drawer components -->
    <el-drawer
        v-model="drawerVisible"
        direction="rtl"
        size="750px"
        :before-close="handleClose"
        :with-header="false"
    >
      <div class="drawer-content">
        <wendu3/>
      </div>
    </el-drawer>

    <el-drawer
        v-model="drawerVisibleHumidity"
        direction="rtl"
        size="750px"
        :before-close="handleClose"
        :with-header="false"
    >
      <div class="drawer-content">
        <shidu3/>
      </div>
    </el-drawer>

    <el-drawer
        v-model="drawerVisiblePh"
        size="750px"
        direction="rtl"
        :before-close="handleClose"
        :with-header="false"
    >
      <ph3/>
    </el-drawer>

    <!-- PDF preview modal -->
    <el-dialog
        v-model="pdfModalVisible"
        width="85%"
        center
        :before-close="(done) => { pdfModalVisible.value = false; done(); }"
    >
      <div ref="pdfModalContent" class="pdf-preview-content">
        <!-- PDF preview content will be generated by html2canvas -->
        <div class="preview-header">
          <h3 style="padding-top: 10px; letter-spacing: 6px;">数据报表</h3>
          <p>生成时间: {{ new Date().toLocaleString() }}</p>
        </div>
        <div class="preview-body">
          <div class="preview-section">
            <div class="data-cards">
              <div class="data-card">
                <div class="card-title">平均温度</div>
                <div class="card-value">{{ currentTemperature }}</div>
              </div>
              <div class="data-card">
                <div class="card-title">平均湿度</div>
                <div class="card-value">{{ currentHumidity }}</div>
              </div>
              <div class="data-card">
                <div class="card-title">平均PH值</div>
                <div class="card-value">{{ currentPh }}</div>
              </div>
              <div class="data-card">
                <div class="card-title">光照强度</div>
                <div class="card-value">{{ currentLightIntensity }}</div>
              </div>
            </div>
            <div class="shuju">
              <div class="header">
                <div class="sj-top1">
                  <div class="wendu">
                    <h1>设备温度日志表柱形图</h1>
                    <wendu2></wendu2>
                  </div>
                </div>
                <div class="sj-top2">
                  <div class="shidu">
                    <div>
                      <h1>设备湿度日志图</h1>
                    </div>


                    <shidu2 style="width: 650px"></shidu2>
                  </div>
                </div>
              </div>

              <div class="foot">
                <div class="sj-foot1">
                  <div class="ph">
                    <h1>PH散点分布图</h1>
                    <ph style="width: 600px;.device-select{position: relative;
                    top: 10px}"></ph>
                  </div>
                </div>
                <div class="sj-foot2">
                  <div class="guang">
                    <guang2></guang2>
                  </div>
                </div>
              </div>
              <div class="under">
                <div class="sj-un1">
                  <div class="turang">
                    <turang2></turang2>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="pdfModalVisible = false">取消</el-button>
          <el-button type="primary" @click="downloadPDF">下载报表</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Export report dialog -->
    <el-dialog
        v-model="exportReportDialogVisible"
        width="300px"
        :modal="false"
        :close-on-click-modal="false"
        :show-close="false"
        custom-class="export-report-dialog"
    >
      <div class="blank-dialog-content">
        <div v-if="isReportLoading" class="loading-spinner">
          <i class="el-icon-loading"></i>
          <span>报表生成中...</span>
        </div>
        <div v-else-if="!isDownloadReady" class="error-content" v-if="reportErrorMessage">
          <i class="el-icon-error error-icon"></i>
          <span>{{ reportErrorMessage }}</span>
        </div>
        <div v-else class="success-content">
          <div class="success-icon">
            <i class="el-icon-success"></i>
          </div>
          <p>报表已生成</p>
          <button @click="handleDownloadReport" class="download-btn">下载报表</button>
          <button @click="closeExportDialog" class="close-btn">取消</button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 样式部分保持不变 */
.top-container {
  display: flex;
  padding-top: 10px;
  justify-content: center;
  gap: 40px;
  background: #F5F7FA;
  width: calc(100% - 80px);
  z-index: 1000;
  transition: all 0.3s ease;
  margin: 10px 0 -10px 40px;
}

/* 主内容区域调整 */
.body {
  padding: 20px 5px 20px 30px;
  overflow-y: auto;
  background: #f5f5f5;
  margin-top: 0;
  width: calc(100% - 0px);
  box-sizing: border-box;
}

.box {
  flex: 1;
  max-width: 310px;
  background-color: #FFFFFF;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 3px 0 rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  height: 120px;
}

.data-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.gg1{

}
.icon{
  position: relative;
  left: 118px;
  width: 50px;
  height: 200px;
}

.number {
  font-size: 30px;
  font-weight: bold;
  text-align: center;
}

.label {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  color: #626363;
  text-align: center;
  line-height: 25px;
}

.label1 {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  color: #626363;
  line-height: 25px;
  position: relative;
  right:5px;
}

/* 图表区域调整 */
.body-top-box{
  display: flex;
  width: calc(100% - 30px); /* 减去右边间距 */
  height: 420px;
  gap: 26px;
  margin-top: 20px;

}
.body-top-temp, .body-top-shidu,
.body-mid-ph, .body-mid-guang,
.body-under, .body-under-right {
  padding: 20px;
  border-radius: 8px;
  border: none;
  background: #FFFFFF;

  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  box-sizing: border-box; /* 确保padding不影响宽度 */
}

.body-top-temp, .body-top-shidu {
  flex: 1;
}

.body-top-temp h3{
  position: relative;
  top: -13px;
  right: 180px;
}
.body-top-shidu h3{
  position: relative;
  top: -13px;
  right: 190px;
}

.body-middle-box{
  display: flex;
  width: calc(100% - 30px); /* 减去右边间距 */
  height: 420px;
  gap: 26px;
  margin-top: 30px; /* 增加顶部间距使布局更规整 */
}

.body-mid-ph, .body-mid-guang {
  flex: 1;
}

.body-mid-ph h3 {
  margin-top: -13.2px;
  position: relative;
  z-index: 10;
  top: 20px;
  right:  202px;
}

.under-box {
  display: flex;
  width: calc(100% - 30px); /* 减去右边间距 */
  gap: 26px;
  margin-top: 30px; /* 增加顶部间距使布局更规整 */
}

/* 土壤营养分布图与关键发现的宽是4：2 */
.body-under {
  flex: 2; /* 4/(4+2) = 2/3 */
  height: 370px;
}

.body-under-right {
  flex: 1; /* 2/(4+2) = 1/3 */
  height: 370px;
}

/* Smart analysis */
.smart-analysis-container {
  font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
  width: calc(100% - 30px); /* 减去右边间距 */
  padding: 20px;
  background-color: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 30px; /* 增加顶部间距使布局更规整 */
  margin-bottom: 30px;
  box-sizing: border-box;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eaeaea;
  width: 100%;
  margin-bottom: 20px;
  padding-bottom: 10px;
}

.analysis-title {
  color: #333;
  font-size: 25px;

}
.uu{
  margin-top: 20px;

}
.section-title {
  color: #555;
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.custom-progress-bar {
  flex-grow: 1;
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-right: 20px;
}

.progress-fill {
  width: 85%;
  height: 100%;
  background-color: #4285f4;
  transition: width 0.3s ease;
}

.confidence-section {
  margin-top: -6px;
  margin-bottom: 10px;
}

.confidence-value {
  color: #5e99fa;
  font-size: 18px;
  font-weight: 800;
  min-width: 40px;
  text-align: right;
  position: relative;
  top: -35px;
  right: 15px;
}

/* 建议维护措施的样式保持不变 */
.maintenance-list {
  list-style: none;
  padding: 0;
  margin: 0;
  margin-right: 16px;
}

.maintenance-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.maintenance-item.urgent {
  border-left: 4px solid #ff6b6b;
}

.item-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 12px;
  font-weight: bold;
}

.normal-icon {
  background-color: #4CAF50;
  color: white;
}

.urgent-icon {
  background-color: #ff6b6b;
  color: white;
}

.item-text {
  flex: 1;
  color: #333;
}

.loading-container {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.error-container {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #f56c6c;
}

.clickable-area {
  border-radius: 4px;
  cursor: pointer;
  margin: 20px;
  margin-left: -40px;
  text-align: center;
  transition: background-color 0.3s;
  z-index: 100;
}

.clickable-area:hover {
  color: #838282;
}

.clickable-area01 {
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  margin-top: 20px;
  transition: background-color 0.3s;
  position: relative;
  left: 17px;
}

.clickable-area01:hover {
  color: #838282;
}

.drawer-content {
  padding: 20px;
  position: relative;
  top: -20px;
}

.baobiao-button {
  background-color: #3498db;
  border-color: #3498db;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  top: -7px;
  border: none;
  color: white;
  letter-spacing: 2px;
}

.baobiao-button:hover {
  background-color: #2980b9;
  border-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 2px rgba(0, 0, 0, 0.1);
}

/* PDF preview styles */
.pdf-preview-content {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;

}

.preview-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
  margin-top: 30px;
}

.preview-header h3 {
  font-size: 40px;
  margin-bottom: -20px;
  color: #333;
  position: relative;
  top: -30px;
}

.preview-header p {
  font-size: 15px;
  color: #666;
}

.preview-section {
  margin-bottom: 30px;
  background-color: #FFFFFF;
  border-radius: 6px;
}

.preview-section h4 {
  font-size: 18px;
  color: #555;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.data-cards {
  display: flex;              /* Enable flex layout */
  justify-content: space-evenly; /* Evenly distribute cards */
  align-items: stretch;       /* Stretch card heights */
  margin-bottom: 20px;
  gap: 15px;                  /* Card spacing */
  overflow-x: auto;           /* Show scrollbar when needed */
  padding-bottom: 5px;        /* Space for scrollbar */
}

.data-card {
  flex: 1;                    /* Equal space distribution */
  min-width: 0;               /* Allow shrinking */
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

/* Small screen optimization */
@media (max-width: 1200px) {
  .data-cards {
    gap: 10px;
  }
}

.card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.preview-suggestions {
  list-style: none;
  padding: 0;
}

.preview-suggestion {
  padding: 10px 0;
  border-bottom: 1px dashed #eee;
}

.preview-suggestion:last-child {
  border-bottom: none;
}

.urgent-tag, .normal-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 10px;
  font-weight: bold;
}

.urgent-tag {
  background-color: #ff6b6b;
  color: white;
}

.normal-tag {
  background-color: #4CAF50;
  color: white;
}

.suggestion-text {
  font-size: 14px;
  color: #333;
}

.no-suggestions {
  padding: 15px 0;
  color: #666;
  font-size: 14px;
}

/* Export report dialog styles */
.export-report-dialog .blank-dialog-content {
  padding: 30px 20px;
  text-align: center;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading-spinner i {
  font-size: 24px;
  color: #409EFF;
  margin-bottom: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(360deg); }
  to { transform: rotate(360deg); }
}

.loading-spinner span {
  color: #666;
  font-size: 14px;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-icon {
  font-size: 24px;
  color: #f56c6c;
  margin-bottom: 10px;
}

.success-content {
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success-content p {
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
}

.download-btn, .close-btn {
  display: block;
  width: 100%;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.download-btn {
  background-color: #409EFF;
  color: white;
}

.download-btn:hover {
  background-color: #3a8ee6;
}

.close-btn {
  background-color: #909399;
  color: white;
}

.close-btn:hover {
  background-color: #606266;
}

/* Dialog footer styles */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.header {
  display: flex;              /* Enable flex layout */
  gap: 20px;                  /* Element spacing */
  width: 100%;                /* Full parent width */
  height: 400px;
}

.sj-top1, .sj-top2 {
  flex: 1;                    /* Equal parent width */
  background-color: #fff;     /* Child background */
  padding: 15px;              /* Padding */
  border-radius: 6px;         /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  min-width: 0;               /* Allow shrinking */
  box-sizing: border-box;     /* Include padding in width */
}

.sj-top1 h1 {
  position: relative;
  top: -20px;
  left: 10px;
  font-size:  19px;
}

.sj-top2 h1{
  position: relative;
  top: -10px;
  left: 10px;
  font-size:  19px;
}

/* Remove positioning that might affect layout */
.wendu, .shidu {
  position: static;           /* Remove absolute positioning */
  top: 0;                     /* Remove top offset */
  right: 0;                   /* Remove right offset */
}

/* Ensure chart containers fit parent */
.wendu > div, .shidu > div {
  width: 100%;                /* Full parent width */
  height: auto;               /* Maintain proper height */
}

.wendu{
  position: relative;
  top: 20px;
}

.shidu{
  position: relative;
  top: 10px;
}

.foot {
  display: flex; /* Enable flex layout */
  justify-content: space-between; /* Space between elements */
  gap: 20px; /* Element spacing */
  margin-top: 20px;
  height: 420px;
}
.shuju{

}
.sj-foot1, .sj-foot2 {
  flex: 1; /* Equal parent width */
  background-color: #fff; /* Child background */
  padding: 15px; /* Padding */
  border-radius: 6px; /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.sj-foot1 h1{
  position: relative;
  top: 10px;
  left: 10px;
  font-size:  19px;
}

.ph{
  position: relative;
  top: -15px;
}

.guang{
  position: relative;
  top: 10px;
}
.under {
  display: flex; /* Enable flex layout */
  gap: 20px; /* Element spacing */
  margin-top: 20px;
  height: 320px;
}

.sj-un1 {
  width: 925px;
  background-color: #fff; /* Child background */
  padding: 15px; /* Padding */
  border-radius: 6px; /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  height: 345px;

}
.sj-un2 {
  width:500px;
  background-color: #fff; /* Child background */
  padding: 15px; /* Padding */
  border-radius: 6px; /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.turang{
  position: relative;
  top: -10px;
  right:  5px;

}
.finding{
  position: relative;
  top: -10px;
  right: 10px;
}
.preview-section-under{
  padding-left: 30px;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.preview-section-under h4{
  font-size:  26px;
  padding-top:  20px;
}
::v-deep .el-dialog__header {
  display: none;
}
.smart-analysis-container1{

  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>