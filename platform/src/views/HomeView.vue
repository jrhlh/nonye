<template>
  <div class="dashboard-root">
    <StatCards
      :user-count="userCount"
      :device-count="deviceCount"
      :temperature="temperature"
      :fault-count="faultCount"
    />
    <ChartSection :current-time="currentTime" />
    <MapSection />
    <AISection />
    <AIAssistantSection />
  </div>
</template>

<script setup lang="ts">
import StatCards from '../components/dashboard/StatCards.vue';
import ChartSection from '../components/dashboard/ChartSection.vue';
import MapSection from '../components/dashboard/MapSection.vue';
import AISection from '../components/dashboard/AISection.vue';
import AIAssistantSection from '../components/dashboard/AIAssistantSection.vue';
const userCount = 0;
const deviceCount = 0;
const temperature = 0;
const faultCount = 0;
const currentTime = '';
</script>

<style scoped>
:root {
  --dashboard-main-bg: #f5f7fa;
  --dashboard-card-bg: #fff;
  --dashboard-radius: 12px;
  --dashboard-shadow: 0 2px 8px rgba(24,144,255,0.04);
  --dashboard-primary: #1890ff;
}
.dashboard-root {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 32px 40px;
  background: var(--dashboard-main-bg);
  box-sizing: border-box;
  min-height: 0;
}
@media (max-width: 900px) {
  .dashboard-root {
    padding: 16px 8px;
    gap: 16px;
  }
}
</style> 