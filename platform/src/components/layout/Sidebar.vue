<script setup lang="ts">
import { Home, BarChart, AlertTriangle, Settings, Users, LogOut } from 'lucide-vue-next';
import { useRouter, useRoute } from 'vue-router';
import { ref, watch, nextTick, onMounted } from 'vue';
import gsap from 'gsap';

const props = defineProps<{ collapsed: boolean }>();

const router = useRouter();
const route = useRoute();

const sidebarRef = ref<HTMLElement | null>(null);
const menuItemRefs = ref<HTMLElement[]>([]);
const logoRef = ref<HTMLElement | null>(null);
const logoTitleRef = ref<HTMLElement | null>(null);
const menuLabelRefs = ref<HTMLElement[]>([]);
const showLabels = ref(!props.collapsed);

const menu = [
  { name: '首页', icon: Home, route: '/dashboard' },
  { name: '数据报表', icon: BarChart, route: '/reports' },
  { name: '故障列表', icon: AlertTriangle, route: '/monitoring' },
  { name: '设备管理', icon: Settings, route: '/devices' },
  { name: '人员管理', icon: Users, route: '/personnel' },
];

const goTo = (r: string) => {
  if (route.path !== r) router.push(r);
};

const handleLogout = () => {
  localStorage.removeItem('user');
  router.push('/login');
};

onMounted(() => {
  // 初始动画（展开）
  if (menuItemRefs.value.length) {
    gsap.fromTo(menuItemRefs.value,
      { opacity: 0, x: -20 },
      { opacity: 1, x: 0, duration: 0.22, stagger: 0.04, ease: 'power2.out' }
    );
  }
  // 初始隐藏所有label
  menuLabelRefs.value.forEach(el => {
    gsap.set(el, { opacity: props.collapsed ? 0 : 1, x: props.collapsed ? -10 : 0, pointerEvents: props.collapsed ? 'none' : 'auto' });
  });
});

watch(() => props.collapsed, (collapsed) => {
  const allLabels = [logoTitleRef.value, ...menuLabelRefs.value].filter(Boolean);
  if (!collapsed) {
    showLabels.value = false; // 先隐藏文本
    gsap.to(sidebarRef.value, {
      width: 210,
      duration: 0.32,
      ease: 'power2.inOut',
      onComplete: () => {
        nextTick(() => {
          showLabels.value = true; // 宽度动画结束后再显示文本
          // LOGO标题和菜单文本飞入动画
          if (logoTitleRef.value) {
            gsap.fromTo(logoTitleRef.value,
              { opacity: 0, x: -20, pointerEvents: 'none' },
              { opacity: 1, x: 0, duration: 0.18, ease: 'power2.out', pointerEvents: 'auto' }
            );
          }
          const menuLabels = menuLabelRefs.value.filter(Boolean);
          if (menuLabels.length) {
            gsap.fromTo(menuLabels,
              { opacity: 0, x: -20, pointerEvents: 'none' },
              { opacity: 1, x: 0, pointerEvents: 'auto', duration: 0.18, stagger: 0.06, ease: 'power2.out' }
            );
          }
        });
      }
    });
    // LOGO图片动画可与宽度动画同步
    if (logoRef.value) {
      gsap.to(logoRef.value, {
        scale: 1,
        opacity: 1,
        duration: 0.18,
        ease: 'power2.out'
      });
    }
  } else {
    showLabels.value = false; // 收缩时立即隐藏文本
    if (allLabels.length) {
      gsap.to(allLabels, {
        opacity: 0, x: -10, duration: 0.14, stagger: 0.03, ease: 'power2.in',
        onStart: () => {
          menuLabelRefs.value.forEach(el => { if (el) el.style.pointerEvents = 'none'; });
        }
      });
    }
    if (logoRef.value) {
      gsap.to(logoRef.value, {
        scale: 0.92,
        opacity: 0.7,
        duration: 0.14,
        ease: 'power2.in'
      });
    }
    gsap.to(sidebarRef.value, {
      width: 60,
      duration: 0.32,
      ease: 'power2.inOut'
    });
  }
}, { immediate: true });
</script>

<template>
  <aside :class="['sidebar', { collapsed: props.collapsed }]" ref="sidebarRef">
    <div class="logo-area" :class="{ center: props.collapsed }">
      <img ref="logoRef" src="../../assets/图层 4.png" alt="logo" class="logo-img" :class="{ center: props.collapsed }" />
      <span ref="logoTitleRef" class="logo-title" v-if="showLabels">禾境智联</span>
    </div>
    <nav class="menu-list">
      <ul>
        <li v-for="(item, idx) in menu" :key="item.name"
            @click="goTo(item.route)"
            :class="['menu-item', { active: route.path === item.route, collapsed: props.collapsed }]"
            ref="el => menuItemRefs.value[idx] = el">
          <span class="icon-wrap" :class="{ center: props.collapsed }">
            <component :is="item.icon" class="menu-icon" :size="22" />
          </span>
          <span class="menu-label" ref="el => menuLabelRefs.value[idx] = el" v-if="showLabels">{{ item.name }}</span>
        </li>
      </ul>
    </nav>
    <div class="logout-area" @click="handleLogout">
      <span class="icon-wrap" :class="{ center: props.collapsed }">
        <LogOut class="menu-icon" :size="22" />
      </span>
      <span class="menu-label" ref="el => menuLabelRefs.value[menu.length] = el" v-if="showLabels">退出登录</span>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 210px;
  background: #fff;
  border-right: 1.5px solid #e6f0ff;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  z-index: 101;
  transition: width 0.2s;
  min-width: 56px;
  box-shadow: none;
}
.sidebar.collapsed {
  width: 60px;
  min-width: 56px;
}
.logo-area {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 16px;
  gap: 8px;
  border-bottom: 1.5px solid #e6f0ff;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #fff;
}
.logo-area.center {
  justify-content: center;
  gap: 0;
}
.logo-img {
  width: 30px;
  height: 30px;
  border-radius: 6px;
}
.logo-img.center {
  margin: 0 auto;
}
.logo-title {
  font-size: 18px;
  font-weight: 900;
  color: #1890ff;
  letter-spacing: 2px;
  margin-left: 4px;
  transition: opacity 0.2s;
  white-space: nowrap;
}
.collapse-btn {
  background: none;
  border: none;
  outline: none;
  color: #1890ff;
  margin-right: 6px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.18s, transform 0.18s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.collapse-btn:hover {
  opacity: 1;
  transform: scale(1.18);
}
.menu-list {
  flex: 1;
  margin-top: 10px;
}
.menu-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 18px 10px 18px;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  border-radius: 6px;
  margin: 4px 8px;
  transition: background 0.18s, color 0.18s, padding 0.2s;
  position: relative;
  font-weight: 500;
  user-select: none;
  border-left: 3px solid transparent;
}
.menu-item.collapsed {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}
.menu-item .icon-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  margin-right: 12px;
  background: transparent;
  transition: background 0.18s, justify-content 0.2s;
}
.menu-item.collapsed .icon-wrap {
  justify-content: center;
  margin-right: 0;
}
.menu-item.active, .menu-item:hover {
  background: #f0f7ff;
  color: #1890ff;
}
.menu-item.active {
  border-left: 3px solid #1890ff;
  background: #e6f7ff;
  color: #1890ff;
}
.menu-item.active .icon-wrap, .menu-item:hover .icon-wrap {
  background: #e6f7ff;
}
.menu-item.active .menu-icon, .menu-item:hover .menu-icon {
  color: #1890ff;
}
.menu-label {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: opacity 0.2s;
  white-space: nowrap;
}
.sidebar.collapsed .menu-label {
  display: none;
}
.logout-area {
  display: flex;
  align-items: center;
  padding: 10px 18px 10px 18px;
  font-size: 16px;
  color: #ff4d4f;
  cursor: pointer;
  border-radius: 6px;
  margin: 8px;
  font-weight: 500;
  transition: background 0.18s, color 0.18s;
}
.logout-area.collapsed {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}
.logout-area .icon-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  margin-right: 12px;
  background: transparent;
  transition: background 0.18s, justify-content 0.2s;
}
.logout-area .icon-wrap.center {
  justify-content: center;
  margin-right: 0;
}
.logout-area.collapsed .icon-wrap {
  justify-content: center;
  margin-right: 0;
}
.logout-area:hover {
  background: #fff1f0;
  color: #ff4d4f;
}
.logout-area:hover .icon-wrap {
  background: #fff1f0;
}
@media (max-width: 900px) {
  .sidebar { width: 56px; min-width: 56px; }
  .logo-title, .menu-label { display: none; }
  .logo-area { padding: 0 6px; }
  .menu-item, .logout-area { padding: 10px 6px; }
}
</style> 