<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    :type="type"
    @click="handleClick"
  >
    <slot name="icon" />
    <span v-if="$slots.default" class="button-text">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  outline?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  type: 'button',
  outline: false,
  loading: false
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => [
  'base-button',
  `base-button--${props.variant}`,
  `base-button--${props.size}`,
  {
    'base-button--outline': props.outline,
    'base-button--loading': props.loading,
    'base-button--disabled': props.disabled
  }
]);

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.base-button:disabled,
.base-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.base-button--loading {
  pointer-events: none;
}

/* 尺寸 */
.base-button--small {
  padding: 6px 12px;
  font-size: 12px;
  min-height: 32px;
}

.base-button--medium {
  padding: 8px 16px;
  font-size: 14px;
  min-height: 36px;
}

.base-button--large {
  padding: 12px 24px;
  font-size: 16px;
  min-height: 44px;
}

/* 变体 */
.base-button--primary {
  background: #1890ff;
  color: white;
}

.base-button--primary:hover:not(:disabled) {
  background: #40a9ff;
}

.base-button--secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #d9d9d9;
}

.base-button--secondary:hover:not(:disabled) {
  background: #e6f7ff;
  border-color: #1890ff;
}

.base-button--danger {
  background: #ff4d4f;
  color: white;
}

.base-button--danger:hover:not(:disabled) {
  background: #ff7875;
}

.base-button--success {
  background: #52c41a;
  color: white;
}

.base-button--success:hover:not(:disabled) {
  background: #73d13d;
}

.base-button--warning {
  background: #faad14;
  color: white;
}

.base-button--warning:hover:not(:disabled) {
  background: #ffc53d;
}

/* 轮廓样式 */
.base-button--outline.base-button--primary {
  background: transparent;
  color: #1890ff;
  border: 1px solid #1890ff;
}

.base-button--outline.base-button--primary:hover:not(:disabled) {
  background: #1890ff;
  color: white;
}

.base-button--outline.base-button--secondary {
  background: transparent;
  color: #666;
  border: 1px solid #d9d9d9;
}

.base-button--outline.base-button--secondary:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #1890ff;
  color: #1890ff;
}

.base-button--outline.base-button--danger {
  background: transparent;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
}

.base-button--outline.base-button--danger:hover:not(:disabled) {
  background: #ff4d4f;
  color: white;
}

.button-text {
  display: inline-block;
}
</style> 