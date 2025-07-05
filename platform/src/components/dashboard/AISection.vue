<template>
  <section class="ai-section">
    <div class="ai-grid">
      <!-- AI预警系统卡片 -->
      <div class="ai-card ai-warning-card">
        <div class="card-header">
          <div class="header-content">
            <div class="title-section">
              <h3 class="card-title">AI预警系统</h3>
              <p class="card-subtitle">智能分析环境数据，提前预警风险</p>
            </div>
            <div class="status-badge">
              <div class="status-dot active"></div>
              <span class="status-text">实时监控</span>
            </div>
          </div>
          <div class="header-actions">
            <button class="action-btn">
              <Settings :size="16" />
              <span>配置</span>
            </button>
          </div>
        </div>
        <div class="card-content">
          <AIyujing />
        </div>
      </div>


    </div>
  </section>
</template>

<script setup lang="ts">
import { Settings } from 'lucide-vue-next';
import AIyujing from '../../components1/AIyujing.vue';
</script>

<style scoped>
.ai-section {
  margin-bottom: var(--spacing-2xl);
}

.ai-grid {
  display: grid;
  grid-template-rows: 1fr;
  gap: var(--spacing-2xl);
}

.ai-card {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ai-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* AI预警系统卡片特殊样式 */
.ai-warning-card {
  background: linear-gradient(135deg, rgba(255, 77, 79, 0.05) 0%, rgba(250, 173, 20, 0.05) 100%);
  border-color: rgba(255, 77, 79, 0.1);
}

.ai-warning-card:hover {
  border-color: rgba(255, 77, 79, 0.2);
}



/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-xl) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.5);
}

.header-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
}

.title-section {
  flex: 1;
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  letter-spacing: -0.5px;
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
  line-height: 1.4;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.active {
  background: var(--success-color);
}

.status-dot.info {
  background: var(--info-color);
}

.status-text {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

/* 卡片内容 */
.card-content {
  flex: 1;
  padding: var(--spacing-2xl);
  display: flex;
  flex-direction: column;
}

/* 脉冲动画 */
@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .ai-grid {
    gap: var(--spacing-xl);
  }
}

@media (max-width: 768px) {
  .ai-section {
    margin-bottom: var(--spacing-xl);
  }
  
  .ai-grid {
    gap: var(--spacing-lg);
  }
  
  .card-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
    padding: var(--spacing-lg) var(--spacing-xl);
  }
  
  .header-content {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .status-badge {
    align-self: flex-start;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
  
  .card-content {
    padding: var(--spacing-xl);
  }
}

@media (max-width: 480px) {
  .card-header {
    padding: var(--spacing-md) var(--spacing-lg);
  }
  
  .card-title {
    font-size: var(--font-size-lg);
  }
  
  .card-subtitle {
    font-size: var(--font-size-xs);
  }
  
  .action-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-xs);
  }
  
  .card-content {
    padding: var(--spacing-lg);
  }
}
</style> 