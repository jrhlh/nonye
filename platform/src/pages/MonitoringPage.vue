<template>
  <div class="monitoring-page">
  
      <div class="monitoring-grid">
        <TemperatureMonitor 
          :device-id="'temp-001'"
          :threshold="{ warning: 30, critical: 35 }"
          @alert="handleAlert"
          @data-update="handleDataUpdate"
        />
        <HumidityMonitor 
          :device-id="'humidity-001'"
          :threshold="{ low: 30, high: 80 }"
          @alert="handleAlert"
          @data-update="handleDataUpdate"
        />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
    import BaseButton from '../components/ui/BaseButton.vue';
import TemperatureMonitor from '../components/features/monitoring/TemperatureMonitor.vue';
import HumidityMonitor from '../components/features/monitoring/HumidityMonitor.vue';
  
  const isRefreshing = ref(false);
  
  const refreshData = async () => {
    isRefreshing.value = true;
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('数据刷新完成');
    } finally {
      isRefreshing.value = false;
    }
  };
  
  const handleAlert = (alert: any) => {
    console.log('收到告警:', alert);
  };
  
  const handleDataUpdate = (data: any) => {
    console.log('数据更新:', data);
  };
  </script>
  
  <style scoped>
  .monitoring-page {
  padding: 24px;
  background: #f5f7fa;
}
  
  .monitoring-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
  }
  
  @media (max-width: 768px) {
  .monitoring-page {
    padding: 16px;
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
}
  </style>