<template>
  <div class="stat-cards-container">
    <div class="stat-cards">
      <StatCardItem
          icon="user"
          :iconComp="User"
          :value="totalUsers"
          trend="up"
          trendValue="+10%"
          label="总注册员工数"
          desc="今日新增 1 人"
          :progress="82"
          iconColor="#667eea"
          progressColor="#667eea"
      />
      <StatCardItem
          icon="device"
          :iconComp="Server"
          :value="totalDevicesCount"
          trend="up"
          trendValue="+2.1%"
          label="总设备数"
          desc="同比增长"
          :progress="65"
          iconColor="#764ba2"
          progressColor="#764ba2"
      />
      <StatCardItem
          icon="temp"
          :iconComp="Thermometer"
          :value="29"
          trend="up"
          trendValue="+1.3%"
          label="当前温度值"
          desc="较昨日上升"
          :progress="48"
          iconColor="#f093fb"
          progressColor="#f093fb"
      />
      <StatCardItem
          icon="fault"
          :iconComp="AlertTriangle"
          :value="repairDevicesCount"
          trend="up"
          trendValue="+0.7%"
          label="故障设备总数"
          desc="需重点关注"
          :progress="22"
          iconColor="#ff4d4f"
          progressColor="#ff4d4f"
          danger
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { User, Server, Thermometer, AlertTriangle } from 'lucide-vue-next';
import StatCardItem from './StatCardItem.vue';

// 总用户数
const totalUsers = ref(0);

// 设备相关
const devices = ref([]);
const totalDevicesCount = computed(() => devices.value?.length || 0); // 计算设备总数

// 温度相关
const currentTemperature = ref('27.5'); // 默认值
const isTemperatureLoading = ref(true);

// 故障设备数
const repairDevicesCount = ref(0); // 初始化为0

// 获取用户总数
const fetchTotalUsers = async () => {
  try {
    const response = await axios.get('http://localhost:5000/personnel/users');
    totalUsers.value = response.data.data.length;
  } catch (error) {
    console.error('获取用户总数失败:', error);
    totalUsers.value = 0;
  }
};

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

// 获取温度数据
const fetchDeviceATemperature = async () => {
  try {
    isTemperatureLoading.value = true;
    const response = await axios.get('http://localhost:5000/temperature/daily/average', {
      params: { deviceId: 1, date: '2025-05-27' }
    });

    if (response.data.code === 200) {
      const avgTemp = response.data.data.temperatures?.[0];
      currentTemperature.value = avgTemp ? `${avgTemp.toFixed(1)}°C` : '无数据';
    } else {
      currentTemperature.value = '数据获取失败';
    }
  } catch (error) {
    console.error('获取温度数据失败:', error);
    currentTemperature.value = '网络错误';
  } finally {
    isTemperatureLoading.value = false;
  }
};

// 获取故障设备数
const fetchRepairDevicesCount = async () => {
  try {
    const response = await axios.get('http://localhost:5000/dashboard');
    repairDevicesCount.value = response.data.todayFaults || 0;
  } catch (error) {
    console.error('获取维修设备数失败:', error);
    repairDevicesCount.value = 0;
  }
};

// 初始化数据
onMounted(async () => {
  await Promise.all([
    fetchTotalUsers(),
    fetchDevices(),
    fetchDeviceATemperature(),
    fetchRepairDevicesCount()
  ]);
});
</script>

<style scoped>
.stat-cards-container {
  width: 100%;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .stat-cards {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .stat-cards {
    gap: 12px;
  }
}
</style>