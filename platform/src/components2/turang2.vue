<template>
  <div class="chart-container">
    <div class="chart-header">
      <h2 class="title">土壤营养分布图</h2>
      <div class="legend">
        <div class="legend-item">
          <div class="color-dot" :style="{ backgroundColor: '#FBEF89' }"></div>
          <span>氮</span>
        </div>
        <div class="legend-item">
          <div class="color-dot" :style="{ backgroundColor: '#C5E1EF' }"></div>
          <span>磷</span>
        </div>
        <div class="legend-item">
          <div class="color-dot" :style="{ backgroundColor: '#ADDEA6' }"></div>
          <span>钾</span>
        </div>
      </div>
    </div>
    <div class="chart" :style="chartStyle"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SoilNutrientChart',
  setup() {
    const chartStyle = ref({
      background: 'linear-gradient(to bottom right, #A9CCE3, #F9E79F, #ABEBC6)',
      height: '200px',
      borderRadius: '8px',
    });

    return {
      chartStyle,
    };
  },
});
</script>

<style scoped>
.chart-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-size: 24px;
  margin: 0;
}

.legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 16px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
}

.chart {
  width: 100%;
}
</style>