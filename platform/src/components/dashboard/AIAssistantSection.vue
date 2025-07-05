<template>
  <section class="ai-section">
    <div class="section-header">
      <h2 class="section-title">智能助手</h2>
      <div class="badge primary">Beta</div>
    </div>
    <div class="ai-assistant">
      <Askai />
    </div>
  </section>
</template>

<script setup lang="ts">
import Askai from '../../components1/askai.vue';
</script>

<style scoped>
.ai-section { margin-bottom: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-title { font-size: 18px; font-weight: 600; color: #262626; }
.badge.primary { background: #e6f7ff; color: var(--dashboard-primary); padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: 500; }
.ai-assistant {
  background: var(--dashboard-card-bg);
  border-radius: var(--dashboard-radius);
  box-shadow: var(--dashboard-shadow);
  padding: 24px;
}
</style> 