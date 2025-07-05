<template>
  <div class="stat-cards-container">
    <div class="stat-cards">
      <StatCardItem
        icon="user"
        :iconComp="User"
        :value="userCount"
        trend="up"
        trendValue="+8.2%"
        label="总注册员工数"
        desc="今日新增 12 人"
        :progress="82"
        iconColor="#667eea"
        progressColor="#667eea"
      />
      <StatCardItem
        icon="device"
        :iconComp="Server"
        :value="deviceCount"
        trend="up"
        trendValue="+2.1%"
        label="在线设备数"
        desc="同比增长"
        :progress="65"
        iconColor="#764ba2"
        progressColor="#764ba2"
      />
      <StatCardItem
        icon="temp"
        :iconComp="Thermometer"
        :value="temperature"
        trend="down"
        trendValue="-1.3%"
        label="当前温度值"
        desc="较昨日下降"
        :progress="48"
        iconColor="#f093fb"
        progressColor="#f093fb"
      />
      <StatCardItem
        icon="fault"
        :iconComp="AlertTriangle"
        :value="faultCount"
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
import { User, Server, Thermometer, AlertTriangle } from 'lucide-vue-next';
import StatCardItem from './StatCardItem.vue';

defineProps<{
  userCount: number,
  deviceCount: number,
  temperature: number,
  faultCount: number,
  stats?: any[],
  loading?: boolean
}>()
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