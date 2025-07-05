<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <h3 v-if="title" class="card-title">{{ title }}</h3>
      </slot>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </div>
    
    <div v-if="$slots.divider" class="card-divider"></div>
    
    <div class="card-content">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  title?: string;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
  shadow?: boolean;
  border?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'medium',
  shadow: true,
  border: true
});

const cardClasses = computed(() => [
  'base-card',
  `base-card--${props.variant}`,
  `base-card--padding-${props.padding}`,
  {
    'base-card--shadow': props.shadow,
    'base-card--border': props.border
  }
]);
</script>

<style scoped>
.base-card {
  background: #fff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.base-card--default {
  background: #fff;
}

.base-card--elevated {
  background: #fff;
}

.base-card--outlined {
  background: transparent;
}

.base-card--shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.base-card--border {
  border: 1px solid #f0f0f0;
}

.base-card--outlined.base-card--border {
  border: 1px solid #d9d9d9;
}

/* 内边距 */
.base-card--padding-none .card-content {
  padding: 0;
}

.base-card--padding-small .card-content {
  padding: 12px;
}

.base-card--padding-medium .card-content {
  padding: 16px;
}

.base-card--padding-large .card-content {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0 16px;
  gap: 12px;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.card-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 12px 16px 0 16px;
}

.card-content {
  flex: 1;
  min-height: 0;
}

.card-footer {
  padding: 12px 16px 16px 16px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

/* 响应式 */
@media (max-width: 768px) {
  .card-header {
    padding: 12px 12px 0 12px;
  }
  
  .base-card--padding-medium .card-content {
    padding: 12px;
  }
  
  .base-card--padding-large .card-content {
    padding: 16px;
  }
  
  .card-footer {
    padding: 8px 12px 12px 12px;
  }
}
</style> 