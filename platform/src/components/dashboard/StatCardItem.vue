<template>
  <div class="stat-card" :class="{ danger }" tabindex="0">
    <div class="stat-icon" :style="{ background: iconBgColor }">
      <component :is="iconComp" :size="24" :color="iconColor" />
    </div>
    <div class="stat-content">
      <div class="stat-row stat-row-top">
        <span class="stat-value">{{ displayValue }}</span>
        <span class="stat-trend" :class="trend" :style="{ transform: `translateY(${arrowY}px)` }">
          <svg v-if="trend === 'up'" width="12" height="12" viewBox="0 0 16 16">
            <path d="M8 12V4M8 4l-3 3M8 4l3 3" :stroke="trendColor" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
          <svg v-else width="12" height="12" viewBox="0 0 16 16">
            <path d="M8 4v8M8 12l-3-3M8 12l3-3" :stroke="trendColor" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
          <span>{{ trendValue }}</span>
        </span>
      </div>
      <div class="stat-row stat-row-bottom">
        <span class="stat-label">{{ label }}</span>
        <span class="stat-desc">{{ desc }}</span>
      </div>
      <div class="stat-progress">
        <div class="progress-bar" :class="{ danger }" :style="{ width: progressWidth + '%', background: progressGradient }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick, computed } from 'vue';

const props = defineProps({
  iconComp: { type: Object, required: true },
  value: { type: Number, default: 0 },
  trend: { type: String, default: 'up' },
  trendValue: { type: String, default: '' },
  label: { type: String, default: '' },
  desc: { type: String, default: '' },
  progress: { type: Number, default: 0 },
  iconColor: { type: String, default: '#667eea' },
  progressColor: { type: String, default: '#667eea' },
  danger: { type: Boolean, default: false }
});

// 计算属性
const iconBgColor = computed(() => {
  if (props.danger) return 'rgba(255, 77, 79, 0.1)';
  return `${props.iconColor}15`;
});

const trendColor = computed(() => {
  if (props.danger) return '#ff4d4f';
  return props.trend === 'up' ? '#52c41a' : '#ff4d4f';
});

const progressGradient = computed(() => {
  if (props.danger) {
    return 'linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%)';
  }
  return `linear-gradient(90deg, ${props.progressColor} 0%, ${props.progressColor}80 100%)`;
});

// 数字动画
const displayValue = ref(0);
let rafId: number | null = null;

const animateValue = (from: number, to: number, duration = 900) => {
  const start = performance.now();
  const step = (now: number) => {
    const progress = Math.min((now - start) / duration, 1);
    displayValue.value = Math.floor(from + (to - from) * progress);
    if (progress < 1) rafId = requestAnimationFrame(step);
    else displayValue.value = to;
  };
  rafId && cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(step);
};

watch(() => props.value, (val, old) => {
  animateValue(old ?? 0, val ?? 0);
}, { immediate: true });

// 进度条动画
const progressWidth = ref(0);
watch(() => props.progress, (val) => {
  nextTick(() => {
    progressWidth.value = val;
  });
}, { immediate: true });

// 箭头动画
const arrowY = ref(0);
let arrowDir = 1;
let arrowAnimId: number | null = null;

const animateArrow = () => {
  arrowY.value += arrowDir * 0.15;
  if (arrowY.value > 1.5) arrowDir = -1;
  if (arrowY.value < -1.5) arrowDir = 1;
  arrowAnimId = requestAnimationFrame(animateArrow);
};

onMounted(() => animateArrow());
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  min-height: 80px;
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
  backdrop-filter: blur(10px);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: rgba(255, 255, 255, 0.3);
}

.stat-card.danger {
  border-color: rgba(255, 77, 79, 0.2);
}

.stat-card.danger:hover {
  border-color: rgba(255, 77, 79, 0.3);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  position: relative;
  height: 100%;
  padding-bottom: 12px;
}

.stat-row {
  display: flex;
  align-items: baseline;
  width: 100%;
  min-width: 0;
}

.stat-row-top {
  margin-bottom: 4px;
  gap: 12px;
}

.stat-row-bottom {
  gap: 8px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
  white-space: nowrap;
  line-height: 1.2;
}

.stat-trend {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  gap: 4px;
  transition: transform 0.3s ease;
  white-space: nowrap;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
}

.stat-trend.up span { 
  color: #52c41a; 
}

.stat-trend.down span { 
  color: #ff4d4f; 
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.stat-desc {
  font-size: 0.75rem;
  color: #999;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 120px;
}

.stat-progress {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 3px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stat-card {
    padding: 16px;
    min-height: 70px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    margin-right: 12px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .stat-trend {
    font-size: 0.75rem;
    padding: 1px 6px;
  }
  
  .stat-label {
    font-size: 0.8rem;
  }
  
  .stat-desc {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 12px;
    min-height: 60px;
  }
  
  .stat-icon {
    width: 36px;
    height: 36px;
    margin-right: 10px;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
  
  .stat-row-top {
    gap: 8px;
  }
  
  .stat-row-bottom {
    gap: 6px;
  }
}
</style> 