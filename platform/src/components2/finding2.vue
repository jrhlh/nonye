<template>
  <div class="key-findings-container">
    <h2 class="title">关键发现</h2>
    <ul class="findings-list">
      <li v-for="item in findingsData" :key="item.title" class="finding-item">
        <span :class="['finding-icon', item.type]">{{ item.icon }}</span>
        <div class="finding-content">
          <span class="finding-title">{{ item.title }}</span>
          <span class="finding-description">{{ item.description }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  setup() {
    const findingsData = ref([]);

    // 默认数据
    const defaultData = [
      {
        icon: '!',
        type: 'alert',
        title: '高温预警',
        description: '当前温度28°C接近作物生长上限，建议密切关注温度变化。'
      },
      {
        icon: '✓',
        type: 'success',
        title: '湿度适宜',
        description: '空气湿度65%RH处于理想范围，有利于作物生长。'
      },
      {
        icon: '!',
        type: 'warning',
        title: 'pH值偏高',
        description: '土壤pH7.8略高于最佳范围，建议适当调整。'
      }
    ];

    // 更新关键发现数据的方法
    const updateFindings = (newFindings) => {
      findingsData.value = newFindings;
    };

    // 监听自定义事件
    const handleUpdateEvent = (event) => {
      if (event.detail) {
        updateFindings(event.detail);
      }
    };

    onMounted(() => {
      // 初始加载默认数据
      findingsData.value = defaultData;

      // 添加事件监听
      window.addEventListener('updateKeyFindings', handleUpdateEvent);
    });

    onUnmounted(() => {
      // 移除事件监听
      window.removeEventListener('updateKeyFindings', handleUpdateEvent);
    });

    return {
      findingsData
    };
  }
};
</script>

<style scoped>
/* 保持原有样式不变 */
.key-findings-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 395px;
  margin: 0;
  padding-left: 10px;
}

.title {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 25px;
  padding-bottom: 6px;
  width: 390px;
  border-bottom: 1px solid #eee;
  position: relative;
  right: 11px;
}

.findings-list {
  list-style: none;
  padding-left: 7px;
  margin: 0;
}

.finding-item {
  margin-bottom: 18px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.finding-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.finding-icon.alert {
  background-color: #f44336;
}

.finding-icon.success {
  background-color: #4CAF50;
}

.finding-icon.warning {
  background-color: #FFC107;
}

.finding-content {
  display: flex;
  flex-direction: column;
}

.finding-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  font-size: 17.5px;
}

.finding-description {
  font-size: 16px;
  color: #666;
  line-height: 1.4;
}
</style>