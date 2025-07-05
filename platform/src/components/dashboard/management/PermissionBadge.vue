<template>
  <div :class="badgeClasses">
    {{ translatePermission(level) }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  level: 'Admin' | 'Supervisor' | 'Operator';
}

const props = defineProps<Props>();

const badgeClasses = computed(() => [
  'permission-badge',
  props.level === 'Admin' ? 'admin-bg' :
  props.level === 'Supervisor' ? 'supervisor-bg' :
  props.level === 'Operator' ? 'operator-bg' :
  'bg-gray-100 text-gray-600'
]);

const translatePermission = (level: string) => {
  const translations = {
    'Admin': '管理员',
    'Supervisor': '主管',
    'Operator': '操作员'
  };
  return translations[level as keyof typeof translations] || level;
};
</script>

<style scoped>
.permission-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  min-width: 60px;
}

.admin-bg {
  background: #ff4d4f;
  color: white;
}

.supervisor-bg {
  background: #faad14;
  color: white;
}

.operator-bg {
  background: #1890ff;
  color: white;
}

.bg-gray-100 {
  background: #f5f5f5;
}

.text-gray-600 {
  color: #666;
}
</style> 