<template>
  <div class="device-management-page">

    <div class="device-content">
      <p>设备管理功能正在开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseButton from '../components/ui/BaseButton.vue';

const showAddDeviceModal = ref(false);
</script>

<style scoped>
.device-management-page {
  padding: 24px;
  background: #f5f7fa;
}

.device-content {
  background: white;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  color: #666;
  font-size: 16px;
}

@media (max-width: 768px) {
  .device-management-page {
    padding: 16px;
  }
}
</style> 