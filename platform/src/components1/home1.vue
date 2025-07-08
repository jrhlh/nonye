<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import PrecipitationChart from "./PrecipitationChart.vue";
import Bingzhuang1 from "../components/features/devices/bingzhuang1.vue";
import AIyujing from "../pages/AIyujing.vue";
import Shengzhang from "../pages/shengzhang.vue";
import axios from 'axios';
import Askai from  "./askai.vue";
import StatCards from '../components/dashboard/StatCards.vue';

// Import avatar images
import c1 from '../assets/c1.jpg';
import c2 from '../assets/c2.jpg';
import c3 from '../assets/c3.jpg';
import c4 from '../assets/c4.jpg';
import c5 from '../assets/c5.jpg';
import c6 from '../assets/c6.jpg';

// Array of available avatar images
const avatarImages = [c1, c2, c3, c4, c5, c6];

// Function to get a random avatar
const getRandomAvatar = () => {
  const randomIndex = Math.floor(Math.random() * avatarImages.length);
  return avatarImages[randomIndex];
};

// 声明响应式用户信息
const user = ref({
  username: '未登录用户',
  isAdmin: false,
  avatar: 'https://avatars.dicebear.com/api/identicon/guest.svg' // 默认头像
});

// 模拟维修设备数（实际需从接口获取）
const repairDevicesCount = ref(0);

// 声明响应式当前时间
const currentTime = ref('');
// 定时器引用
let timeUpdateTimer: ReturnType<typeof setInterval> | null = null;

onMounted(async () => {
  try {
    // 调用后端接口获取维修设备数（假设接口为/get-repair-count）
    const response = await axios.get('http://localhost:5000/dashboard'); // 示例接口
    const { todayFaults } = response.data;

    // 更新响应式变量
    repairDevicesCount.value = todayFaults;
  } catch (error) {
    console.error('获取维修设备数失败:', error);
    // 可选：设置默认值
    repairDevicesCount.value = 0;
  }
  await fetchDeviceATemperature();

  // 初始化时间显示
  updateCurrentTime();
  startTimeUpdateTimer();
});

// 组件挂载后处理用户信息和头像
onMounted(() => {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const parsedUser = JSON.parse(storedUser);
      user.value = {
        ...parsedUser,
        // 使用 DiceBear 生成头像（用户名或默认值）
        avatar: getRandomAvatar()
      };
    } catch (error) {
      console.error('解析用户信息失败:', error);
      // 解析失败时使用默认头像
      user.value.avatar = 'https://avatars.dicebear.com/api/identicon/user123.svg';
    }
  }
});

// 添加总用户数响应式变量
const totalUsers = ref(0);

// 在组件挂载时获取用户总数
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5000/personnel/users');
    totalUsers.value = response.data.data.length; // 假设返回的数据结构中有data数组
  } catch (error) {
    console.error('获取用户总数失败:', error);
    totalUsers.value = 0;
  }
});

const devices = ref([]); // 确保已有这个声明

// 获取设备列表
const fetchDevices = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/device/list');
    if (response.data.success) {
      devices.value = response.data.data;
    }
  } catch (error) {
    console.error('获取设备列表失败:', error);
  }
};

onMounted(() => {
  fetchDevices();
});
// 计算设备总数
const totalDevicesCount = computed(() => {
  return devices.value?.length || 0;
});

// 设备A温度相关响应式数据
const currentTemperature = ref('27.5');
const isTemperatureLoading = ref(true);
const temperatureError = ref('');
// 获取设备A在5月27日的平均温度
const fetchDeviceATemperature = async () => {
  try {
    isTemperatureLoading.value = true;
    temperatureError.value = '';

    // 调用优化后的温度API
    const response = await axios.get('http://localhost:5000/temperature/daily/average', {
      params: {
        deviceId: 1,
        date: '2025-05-27'
      }
    });

    console.log('温度API响应:', response.data);

    const data = response.data;

    if (data.code === 200 && data.data && data.data.temperatures && data.data.dates) {
      const temperatures = data.data.temperatures;
      const dates = data.data.dates;

      // 验证数据有效性
      if (temperatures.length > 0 && dates.length > 0) {
        // 直接获取日均温度（因为后端已返回单日数据）
        if (temperatures.length > 0) {
          const avgTemp = temperatures[0];
          currentTemperature.value = `${avgTemp.toFixed(1)}°C`;
        } else {
          currentTemperature.value = '指定日期无数据';
        }
      } else {
        console.error('无法解析温度数据结构:', data.data);
        currentTemperature.value = '数据格式错误';
        temperatureError.value = '无法解析温度数据';
      }
    } else {
      currentTemperature.value = '数据获取失败';
      temperatureError.value = data.message || '未知错误';
    }
  } catch (error: any) {
    console.error('获取温度数据失败:', error);
    currentTemperature.value = '网络错误';
    temperatureError.value = error.message || '无法连接到服务器';
  } finally {
    isTemperatureLoading.value = false;
  }
};

// 更新当前时间
const updateCurrentTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 启动时间更新定时器（每分钟更新一次）
const startTimeUpdateTimer = () => {
  if (timeUpdateTimer) {
    stopTimeUpdateTimer();
  }
  timeUpdateTimer = setInterval(() => {
    updateCurrentTime();
  }, 60000); // 每分钟更新一次
};

// 停止时间更新定时器
const stopTimeUpdateTimer = () => {
  if (timeUpdateTimer) {
    clearInterval(timeUpdateTimer);
    timeUpdateTimer = null;
  }
};

// 组件卸载时停止定时器
onUnmounted(() => {
  stopTimeUpdateTimer();
});

// 优化变量命名
const userCount = totalUsers;
const deviceCount = totalDevicesCount;
const temperature = currentTemperature;
const faultCount = repairDevicesCount;
</script>

<template>
  <div></div>
</template>

<style scoped>
/* 基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard {
  width: 100%;
  min-height: 100vh;
  background-color: #f0f2f5;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #262626;
}

/* 顶部导航栏 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.alert-banner {
  margin-right: 24px;
  background-color: #1890ff;
  color: white;
  padding: 6px 16px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-icon {
  display: flex;
  align-items: center;
  animation: pulse 2s infinite;
}

.alert-text {
  font-size: 14px;
  font-weight: 500;
}

.alert-count {
  font-size: 20px;
  font-weight: 600;
  color: #ff4d4f;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 0 8px;
  min-width: 32px;
  text-align: center;
}

.alert-unit {
  font-size: 14px;
}

.time-display {
  margin-right: 16px;
  color: #8c8c8c;
  font-size: 14px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar-container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 24px;
  background-color: #f5f5f5;
  transition: all 0.3s;
}

.avatar-container:hover {
  background-color: #e6f7ff;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 内容区域 */
.dashboard-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 章节标题 */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  background-color: #1890ff;
  margin-right: 8px;
  border-radius: 2px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 4px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-action:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.btn-refresh {
  background: none;
  border: none;
  color: #8c8c8c;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-refresh:hover {
  background-color: #f5f5f5;
  color: #1890ff;
}

/* 数据卡片 */
.stat-section {
  margin-bottom: 8px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.stat-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 24px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  border-left: 4px solid transparent;
}

.stat-card:nth-child(1) {
  border-left-color: #FDBB38;
}

.stat-card:nth-child(2) {
  border-left-color: #449EEE;
}

.stat-card:nth-child(3) {
  border-left-color: #42BB88;
}

.stat-card:nth-child(4) {
  border-left-color: #F96C17;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-right: 16px;
  background-position: center;
  background-repeat: no-repeat;
  background-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-icon {
  background-color: rgba(253, 187, 56, 0.1);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FDBB38'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'%3E%3C/path%3E%3C/svg%3E");
}

.device-icon {
  background-color: rgba(68, 158, 238, 0.1);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23449EEE'%3E%3Cpath d='M17 16l-4-4V8.82C14.16 8.4 15 7.3 15 6c0-1.66-1.34-3-3-3S9 4.34 9 6c0 1.3.84 2.4 2 2.82V12l-4 4H3v5h5v-3.05l4-4.2 4 4.2V21h5v-5h-4z'%3E%3C/path%3E%3C/svg%3E");
}

.temp-icon {
  background-color: rgba(66, 187, 136, 0.1);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2342BB88'%3E%3Cpath d='M15 13V5c0-1.66-1.34-3-3-3S9 3.34 9 5v8c-1.21.91-2 2.37-2 4 0 2.76 2.24 5 5 5s5-2.24 5-5c0-1.63-.79-3.09-2-4zm-4-8c0-.55.45-1 1-1s1 .45 1 1h-2z'%3E%3C/path%3E%3C/svg%3E");
}

.fault-icon {
  background-color: rgba(249, 108, 23, 0.1);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F96C17'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'%3E%3C/path%3E%3C/svg%3E");
}

.stat-data {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
  color: #262626;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.highlight {
  color: #ff4d4f;
}

/* 图表区域 */
.chart-section {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 16px;
}

.chart-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.card-info {
  font-size: 14px;
  color: #8c8c8c;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.status-indicators {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.status-item {
  background-color: #fafafa;
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  transition: all 0.3s;
}

.status-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-bottom: 8px;
}

.status-label {
  font-size: 14px;
  color: #595959;
  margin-bottom: 4px;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.green { background-color: #52c41a; }
.orange { background-color: #faad14; }
.red { background-color: #f5222d; }
.gray { background-color: #bfbfbf; }

.pie-chart {
  height: 240px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 地图区域 */
.map-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  overflow: hidden;
}

.map-container {
  height: 500px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

/* AI预警和生长趋势 */
.data-section {
  margin-bottom: 16px;
}

.data-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
}

.ai-card, .growth-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  height: 400px;
  display: flex;
  flex-direction: column;
}

.card-content {
  flex: 1;
  overflow: hidden;
}

/* AI助手 */
.ai-section {
  margin-bottom: 24px;
}

.ai-assistant {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

/* 徽章 */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.4;
}

.badge.primary {
  background-color: #e6f7ff;
  color: #1890ff;
}

.badge.warning {
  background-color: #fff7e6;
  color: #fa8c16;
}

.badge.info {
  background-color: #e6fffb;
  color: #13c2c2;
}

/* 动画 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.dashboard {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-section,
  .data-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.large,
  .chart-card,
  .ai-card,
  .growth-card {
    height: auto;
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .status-indicators {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-header {
    flex-direction: column;
    height: auto;
    padding: 12px;
  }
  
  .header-left,
  .header-right {
    width: 100%;
    justify-content: center;
    margin: 8px 0;
  }
  
  .alert-banner {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .user-info {
    flex-direction: column;
    gap: 8px;
  }
}
</style>