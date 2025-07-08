<script setup lang="ts">
import Sidebar from './Sidebar.vue';
import HeaderBar from './HeaderBar.vue';
import { RouterView } from 'vue-router';
import { ref, watch } from 'vue';
import gsap from 'gsap';

const collapsed = ref(false);
const sidebarWidth = ref(210);
const toggleSidebar = () => { collapsed.value = !collapsed.value; };

watch(collapsed, (val) => {
  gsap.to(sidebarWidth, {
    value: val ? 60 : 210,
    duration: 0.32,
    ease: 'power2.inOut',
  });
});
</script>

<template>
  <div class="layout-root">
    <aside class="sidebar" :style="{ width: sidebarWidth + 'px' }">
      <Sidebar :collapsed="collapsed" />
    </aside>
    <main class="main-content">
      <HeaderBar :collapsed="collapsed" :toggleSidebar="toggleSidebar"class="ll"/>
      <section class="main-section">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<style scoped>
*{
  margin: 0;
  padding: 0;
}
.layout-root {
  display: flex;

  overflow: hidden;
  background: #f5f7fa;
}
.sidebar {
  width: 210px!important;
  flex: 0 0 210px!important;
  transition: width 0.32s cubic-bezier(.42,0,.58,1);
  min-width: 0;
  z-index: 2;
}
.main-content {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

}
.main-section {
  flex: 1;
  background: #f5f7fa;
  overflow-y: auto;
  max-height: calc(100vh - 60px);
  /* 美化滚动条 */
  scrollbar-width: thin;
  scrollbar-color: #b3d4fc #f5f7fa;


}
.main-section::-webkit-scrollbar {
  width: 8px;
  background: #f5f7fa;
}
.main-section::-webkit-scrollbar-thumb {
  background: #b3d4fc;
  border-radius: 6px;
  transition: background 0.2s;
}
.main-section::-webkit-scrollbar-thumb:hover {
  background: #1890ff;
}
@media (max-width: 900px) {
  .sidebar { width: 56px !important; }
  .main-section { padding: 16px 8px; }
}
</style>