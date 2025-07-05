<template>
  <div class="device-container">
    <svg 
      t="1748246060883" 
      class="icon" 
      style="width: 20px" 
      viewBox="0 0 1024 1024" 
      version="1.1" 
      xmlns="http://www.w3.org/2000/svg" 
      p-id="14446" 
      width="20" 
      height="20"
    >
      <path d="M815.43 40H200.06C91.48 40 3.16 128.33 3.16 236.9v396.37c0 108.57 88.32 196.9 196.9 196.9h268.49v76.27H269.77v78.41h475.96v-78.41H546.96v-76.27h268.47c108.58 0 196.9-88.33 196.9-196.9V236.9c0-108.57-88.32-196.9-196.9-196.9z m118.49 593.27c0 65.33-53.14 118.49-118.49 118.49H200.06c-65.34 0-118.49-53.15-118.49-118.49V236.9c0-65.33 53.14-118.49 118.49-118.49h615.37c65.34 0 118.49 53.15 118.49 118.49v396.37z" fill="#333333" p-id="14447" />
      <path d="M247.69 286.38h520.12v78.41H247.69zM247.69 505.38h355.86v78.41H247.69z" fill="#C6C6C6" p-id="14448" />
    </svg>
    <span class="device-count">{{ count }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  count: number;
}

defineProps<Props>();
</script>

<style scoped>
.device-container {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.device-count {
  font-weight: 500;
}

.icon {
  opacity: 0.7;
}
</style> 