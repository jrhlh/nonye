<template>
  <div class="statistics-card-container" :class="{ danger, loading }" tabindex="0">
    <div class="statistics-icon-wrapper" :style="{ background: iconBackgroundColor }">
      <component :is="iconComponent" :size="24" :color="iconColorValue" />
    </div>
    <div class="statistics-content-wrapper">
      <div class="statistics-row statistics-row-top">
        <span class="statistics-value">{{ displayValueWithAnimation }}</span>
        <span class="statistics-trend" :class="trendDirection" :style="{ transform: `translateY(${arrowAnimationOffset}px)` }">
          <svg v-if="trendDirection === 'up'" width="12" height="12" viewBox="0 0 16 16">
            <path d="M8 12V4M8 4l-3 3M8 4l3 3" :stroke="trendColorValue" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
          <svg v-else width="12" height="12" viewBox="0 0 16 16">
            <path d="M8 4v8M8 12l-3-3M8 12l3-3" :stroke="trendColorValue" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
          <span>{{ trendValueText }}</span>
        </span>
      </div>
      <div class="statistics-row statistics-row-bottom">
        <span class="statistics-label">{{ labelText }}</span>
        <span class="statistics-description">{{ descriptionText }}</span>
      </div>
      <div class="statistics-progress-container">
        <div class="progress-bar" :class="{ danger }" :style="{ width: progressBarWidth + '%', background: progressBarGradient }"></div>
      </div>
    </div>
    
    <!-- 加载状态遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from 'vue';

// 定义组件属性接口
interface StatCardItemProps {
  iconComp: any;
  value: number;
  trend: 'up' | 'down' | 'stable';
  trendValue: string;
  label: string;
  desc: string;
  progress: number;
  iconColor: string;
  progressColor: string;
  danger?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<StatCardItemProps>(), {
  value: 0,
  trend: 'up',
  trendValue: '',
  label: '',
  desc: '',
  progress: 0,
  iconColor: '#667eea',
  progressColor: '#667eea',
  danger: false,
  loading: false
});

// 计算属性 - 优化变量名称
const iconBackgroundColor = computed(() => {
  if (props.danger) return 'rgba(255, 77, 79, 0.1)';
  return `${props.iconColor}15`;
});

const trendColorValue = computed(() => {
  if (props.danger) return '#ff4d4f';
  return props.trend === 'up' ? '#52c41a' : '#ff4d4f';
});

const progressBarGradient = computed(() => {
  if (props.danger) {
    return 'linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%)';
  }
  return `linear-gradient(90deg, ${props.progressColor} 0%, ${props.progressColor}80 100%)`;
});

// 文本内容别名
const iconComponent = computed(() => props.iconComp);
const iconColorValue = computed(() => props.iconColor);
const trendDirection = computed(() => props.trend);
const trendValueText = computed(() => props.trendValue);
const labelText = computed(() => props.label);
const descriptionText = computed(() => props.desc);

// 数字动画相关
const displayValueWithAnimation = ref(0);
let animationFrameId: number | null = null;

const animateValueWithSmoothTransition = (fromValue: number, toValue: number, duration = 900) => {
  const startTime = performance.now();
  const step = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    displayValueWithAnimation.value = Math.floor(fromValue + (toValue - fromValue) * easeOutQuart);
    
    if (progress < 1) {
      animationFrameId = requestAnimationFrame(step);
    } else {
      displayValueWithAnimation.value = toValue;
    }
  };
  
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  animationFrameId = requestAnimationFrame(step);
};

// 监听数值变化
watch(() => props.value, (newValue, oldValue) => {
  animateValueWithSmoothTransition(oldValue ?? 0, newValue ?? 0);
}, { immediate: true });

// 进度条动画
const progressBarWidth = ref(0);
watch(() => props.progress, (newProgress) => {
  nextTick(() => {
    progressBarWidth.value = newProgress;
  });
}, { immediate: true });

// 箭头动画
const arrowAnimationOffset = ref(0);
let arrowDirection = 1;
let arrowAnimationId: number | null = null;

const animateArrowWithBounce = () => {
  arrowAnimationOffset.value += arrowDirection * 0.15;
  if (arrowAnimationOffset.value > 1.5) arrowDirection = -1;
  if (arrowAnimationOffset.value < -1.5) arrowDirection = 1;
  arrowAnimationId = requestAnimationFrame(animateArrowWithBounce);
};

// 生命周期管理
onMounted(() => {
  animateArrowWithBounce();
});

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  if (arrowAnimationId) {
    cancelAnimationFrame(arrowAnimationId);
  }
});
</script>

<style scoped>
.statistics-card-container {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  padding: var(--spacing-xl);
  transition: all var(--transition-medium);
  cursor: pointer;
  min-height: 80px;
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  backdrop-filter: blur(10px);
}

.statistics-card-container:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-card-hover);
}

.statistics-card-container.danger {
  border-color: rgba(255, 77, 79, 0.2);
}

.statistics-card-container.danger:hover {
  border-color: rgba(255, 77, 79, 0.3);
}

.statistics-card-container.loading {
  opacity: 0.7;
  pointer-events: none;
}

.statistics-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-lg);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.statistics-card-container:hover .statistics-icon-wrapper {
  transform: scale(1.05);
}

.statistics-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  position: relative;
  height: 100%;
  padding-bottom: var(--spacing-sm);
}

.statistics-row {
  display: flex;
  align-items: baseline;
  width: 100%;
  min-width: 0;
}

.statistics-row-top {
  margin-bottom: var(--spacing-xs);
  gap: var(--spacing-md);
}

.statistics-row-bottom {
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.statistics-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  line-height: 1.2;
}

.statistics-trend {
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
  gap: var(--spacing-xs);
  transition: transform var(--transition-fast);
  white-space: nowrap;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  background: var(--bg-card-hover);
}

.statistics-trend.up span { 
  color: var(--success-color); 
}

.statistics-trend.down span { 
  color: var(--error-color); 
}

.statistics-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.statistics-description {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 120px;
}

.statistics-progress-container {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 3px;
  background: var(--bg-progress);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: var(--radius-sm);
  transition: width var(--transition-slow);
}

/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xl);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-card);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式容器设计 */
@media (max-width: 1600px) {
  .statistics-card-container {
    padding: var(--spacing-lg);
  }
  
  .statistics-icon-wrapper {
    width: 44px;
    height: 44px;
    margin-right: var(--spacing-md);
  }
}

@media (max-width: 1400px) {
  .statistics-card-container {
    padding: var(--spacing-md);
    min-height: 70px;
  }
  
  .statistics-icon-wrapper {
    width: 40px;
    height: 40px;
    margin-right: var(--spacing-sm);
  }
  
  .statistics-value {
    font-size: var(--font-size-xl);
  }
}

@media (max-width: 1200px) {
  .statistics-card-container {
    padding: var(--spacing-sm);
    min-height: 65px;
  }
  
  .statistics-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .statistics-value {
    font-size: var(--font-size-lg);
  }
  
  .statistics-trend {
    font-size: var(--font-size-xs);
    padding: var(--spacing-xs) var(--spacing-xs);
  }
}

@media (max-width: 768px) {
  .statistics-card-container {
    padding: var(--spacing-sm);
    min-height: 60px;
  }
  
  .statistics-icon-wrapper {
    width: 32px;
    height: 32px;
    margin-right: var(--spacing-xs);
  }
  
  .statistics-value {
    font-size: var(--font-size-md);
  }
  
  .statistics-row-top {
    gap: var(--spacing-sm);
  }
  
  .statistics-row-bottom {
    gap: var(--spacing-xs);
  }
}

@media (max-width: 480px) {
  .statistics-card-container {
    padding: var(--spacing-xs);
    min-height: 55px;
  }
  
  .statistics-icon-wrapper {
    width: 28px;
    height: 28px;
  }
  
  .statistics-value {
    font-size: var(--font-size-sm);
  }
  
  .statistics-label {
    font-size: var(--font-size-xs);
  }
  
  .statistics-description {
    font-size: 10px;
  }
}
</style> 