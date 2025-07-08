<script setup lang="ts">
import { ChevronDown, Menu as MenuIcon } from 'lucide-vue-next';
import { computed } from 'vue';

// 导入本地头像图片
import c1 from '/src/assets/c1.jpg';
import c2 from '/src/assets/c2.jpg';
import c3 from '/src/assets/c3.jpg';
import c4 from '/src/assets/c4.jpg';
import c5 from '/src/assets/c5.jpg';
import c6 from '/src/assets/c6.jpg';

const avatarImages = [c1, c2, c3, c4, c5, c6];

const props = defineProps<{ collapsed: boolean, toggleSidebar: () => void }>();

// 获取用户名和随机头像
const username = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}').username || '未登录';
  } catch {
    return '未登录';
  }
});

const randomAvatar = computed(() => {
  if (username.value === '未登录') {
    return c1; // 默认头像
  }
  const randomIndex = Math.floor(Math.random() * avatarImages.length);
  return avatarImages[randomIndex];
});
</script>

<template>
  <header class="main-header">
    <div class="header-left">
      <button class="collapse-btn" @click="props.toggleSidebar">
        <MenuIcon :size="22" :style="{ transform: props.collapsed ? 'rotate(180deg)' : 'none' }" />
      </button>
      <span class="header-title">智慧农业监控平台</span>
    </div>
    <div class="header-right">
      <div class="user-block">
        <img :src="randomAvatar" class="user-avatar" alt="avatar" />
        <span class="user-name">{{ username }}</span>
        <ChevronDown :size="18" class="user-arrow" />
      </div>
    </div>
  </header>
</template>

<style scoped>
/* 添加头像样式 */
.user-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid #e6f0ff;
  background: #fafdff;
  box-shadow: 0 1px 4px rgba(24,144,255,0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 3px 8px rgba(24,144,255,0.15);
}

/* 保持原有样式不变 */
.main-header {
  width: 100%;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #fafdff 60%, #e6f0ff 100%);
  border-bottom: 1.5px solid #e6f0ff;
  box-shadow: 0 2px 8px 0 rgba(24,144,255,0.04);
  padding: 0 36px;
  z-index: 100;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.collapse-btn {
  background: none;
  border: none;
  outline: none;
  color: #1890ff;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.18s, transform 0.32s cubic-bezier(.42,0,.58,1);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 2px 0 0;
}
.collapse-btn:hover {
  opacity: 1;
  transform: scale(1.18);
}
.header-title {
  font-size: 22px;
  font-weight: 900;
  color: #1890ff;
  letter-spacing: 2px;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 18px;
}
.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(24,144,255,0.06);
  padding: 4px 16px 4px 10px;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s;
  border: 1px solid #e6f0ff;
  width: 140px;
}
.user-block:hover {
  background: #e6f7ff;
  box-shadow: 0 4px 16px rgba(24,144,255,0.10);
}
.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #222;
  letter-spacing: 0.5px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-arrow {
  color: #1890ff;
  opacity: 0.85;
  margin-left: 2px;
}
@media (max-width: 900px) {
  .main-header { padding: 0 8px; height: 48px; }
  .header-title { font-size: 15px; }
  .user-avatar { width: 24px; height: 24px; }
  .user-name { font-size: 12px; }
  .header-right { gap: 6px; }
  .user-block { padding: 2px 8px 2px 4px; gap: 4px; }
}
</style>