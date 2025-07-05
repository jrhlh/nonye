<template>
  <section class="chart-section">
    <div class="card-grid">
      <div class="chart-card doughnut-card">
        <div class="card-header">
          <span class="card-title">设备全局状态</span>
        </div>
        <div class="chart-divider"></div>
        <DoughnutChart :data="doughnutData" />
        <div class="card-footer">
          <span v-for="item in doughnutData" :key="item.name" class="footer-item">
            <span :class="['dot', item.name]" />{{ item.name }}: {{ item.value }}
          </span>
          <span class="footer-total">总数: {{ doughnutData.reduce((sum, i) => sum + i.value, 0) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">

import DoughnutChart from './DoughnutChart.vue';


// 环形图数据
const doughnutData = [
  { name: '正常', value: 58 },
  { name: '警告', value: 14 },
  { name: '故障', value: 14 },
  { name: '离线', value: 14 }
];
</script>

<style scoped>
.chart-section {
  width: 100%;
  margin-bottom: 24px;
}
.card-grid {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  width: 100%;
}
.chart-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px 0 rgba(24,144,255,0.07);
  border: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  min-width: 260px;
  max-width: 420px;
  flex: 1 1 320px;
  position: relative;
}
.treemap-card {
  min-width: 340px;
  max-width: 520px;
  flex: 2 1 380px;
  padding: 0 0 18px 0;
}
.doughnut-card {
  min-width: 220px;
  max-width: 320px;
  flex: 1 1 220px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px 8px 24px;
}
.card-title {
  font-size: 1.12rem;
  font-weight: 700;
  color: #222;
  letter-spacing: 0.5px;
}
.card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  justify-content: flex-start;
  align-items: center;
  padding: 10px 20px 10px 20px;
  font-size: 13px;
  color: #888;
  border-top: 1px solid #ececec;
  border-radius: 0 0 14px 14px;
  background: #fafbfc;
}
.footer-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding-right: 10px;
  line-height: 1.7;
}
.footer-total {
  margin-left: auto;
  font-weight: 500;
  color: #888;
  letter-spacing: 0.5px;
}
.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 4px;
  border: 1px solid #e0e0e0;
}
.dot.正常 { background: #52c41a; }
.dot.警告 { background: #faad14; }
.dot.故障 { background: #ff4d4f; }
.dot.离线 { background: #d9d9d9; }
.chart-divider {
  width: 100%;
  height: 1px;
  background: #ececec;
 
}
@media (max-width: 900px) {
  .card-grid { flex-direction: column; gap: 18px; }
  .chart-card, .treemap-card, .doughnut-card { min-width: 0; max-width: 100%; }
  .card-header { padding: 14px 12px 6px 12px; }
}
</style> 