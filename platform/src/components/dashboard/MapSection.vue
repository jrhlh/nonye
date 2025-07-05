<template>
  <section class="map-card">
    <div class="card-header">
      <div class="header-content">
        <span class="card-title">设备地理分布</span>
        <span class="card-subtitle">实时监控设备位置和状态</span>
      </div>
      <div class="card-actions">
        <button class="btn-action" @click="refreshMap">
          <RefreshCw :size="16" />
          刷新
        </button>
        <button class="btn-action btn-primary" @click="showModal = true">
          <Maximize2 :size="16" />
          全屏
        </button>
      </div>
    </div>
    <div class="map-container">
      <DeviceMap
        :points="points"
        :boundary="boundary"
        :center="center"
        :zoom="zoom"
        :showLegend="true"
        style="width:100%;height:100%;"
      />
    </div>
    
  </section>

  <!-- 全屏模态框 - 使用Teleport挂载到body -->
  <Teleport to="body">
    <div v-if="showModal" class="modal-mask" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title">
            <span class="title-text">设备分布地图</span>
            <span class="title-subtitle">点击设备查看详细信息</span>
          </div>
          <button class="modal-close" @click="showModal = false">
            <X :size="20" />
          </button>
        </div>
        <div class="modal-body">
          <DeviceMap
            :points="points"
            :boundary="boundary"
            :center="center"
            :zoom="zoom"
            style="width:100%;height:80vh;min-height:400px;"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RefreshCw, Maximize2, X } from 'lucide-vue-next';
import DeviceMap from './DeviceMap.vue';

const showModal = ref(false);

// 示例数据，可根据实际需要替换
const points = [
  { id: 1, name: '北田传感器', status: 'normal', lat: 27.4605, lng: 120.381, type: '传感器', location: '村北农田' },
  { id: 2, name: '东园控制器', status: 'warning', lat: 27.458, lng: 120.3828, type: '控制器', location: '村东果园' },
  { id: 3, name: '南塘执行器', status: 'fault', lat: 27.458, lng: 120.380, type: '执行器', location: '村南池塘' },
  { id: 4, name: '西园传感器', status: 'normal', lat: 27.459, lng: 120.380, type: '传感器', location: '村西菜园' },
  { id: 5, name: '中心控制器', status: 'offline', lat: 27.460, lng: 120.3818, type: '控制器', location: '村中心' },
  { id: 6, name: '果园监测仪', status: 'normal', lat: 27.46085, lng: 120.3832, type: '传感器', location: '村东果园' },
  { id: 7, name: '村中心设备', status: 'normal', lat: 27.460, lng: 120.3823, type: '服务器', location: '村控制中心' }
];

const boundary: [number, number][] = [
  [27.458, 120.3785],
  [27.4615, 120.3815],
  [27.4605, 120.3845],
  [27.456, 120.3825],
  [27.458, 120.3785]
];

const center: [number, number] = [27.460, 120.381];
const zoom = 18;

const refreshMap = () => {
  // 刷新地图数据
  console.log('刷新地图数据');
};
</script>

<style scoped>
.map-card {
  background: var(--bg-card-hover);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  min-width: 320px;
  max-width: 100%;
  margin-bottom: var(--spacing-2xl);
  padding: 0;
  position: relative;
  backdrop-filter: blur(10px);
  transition: var(--transition-base);
}

.map-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 255, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-xl) var(--spacing-2xl) var(--spacing-lg) var(--spacing-2xl);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-content {
  flex: 1;
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  display: block;
  margin-bottom: var(--spacing-xs);
}

.card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 400;
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.btn-action {
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

.btn-action:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.btn-primary {
  background: var(--gradient-primary);
  color: var(--text-white);
  border-color: transparent;
}

.btn-primary:hover {
  background: var(--gradient-primary-hover);
  transform: translateY(-1px);
}

.map-container {
  width: 100%;
  height: 320px;
  border-radius: 0 0 16px 16px;
  overflow: hidden;
  background: #fafbfc;
}

/* 模态框样式 */
.modal-mask {
  position: fixed;
  z-index: 1000;
  left: 0; 
  top: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
  padding: 20px;
}

.modal-content {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  min-width: 400px;
  max-width: 90vw;
  width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.3s ease;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-title {
  display: flex;
  flex-direction: column;
}

.title-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.title-subtitle {
  font-size: 0.875rem;
  color: #666;
  font-weight: 400;
}

.modal-close {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1a1a1a;
  transform: scale(1.05);
}

.modal-body {
  padding: 0;
  flex: 1;
  overflow: hidden;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .map-container {
    height: 280px;
  }
}

@media (max-width: 1200px) {
  .card-header {
    padding: 16px 20px 12px 20px;
  }
  
  .map-container {
    height: 260px;
  }
}

@media (max-width: 768px) {
  .map-card {
    min-width: 0;
    margin-bottom: 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding: 16px 16px 12px 16px;
  }
  
  .card-actions {
    justify-content: flex-start;
  }
  
  .map-container {
    height: 240px;
  }
  
  .modal-content {
    width: 95vw;
    min-width: 320px;
  }
  
  .modal-header {
    padding: 16px 20px 12px 20px;
  }
  
  .title-text {
    font-size: 1.125rem;
  }
}

@media (max-width: 480px) {
  .card-header {
    padding: 12px 16px 8px 16px;
  }
  
  .card-title {
    font-size: 1rem;
  }
  
  .card-subtitle {
    font-size: 0.8rem;
  }
  
  .btn-action {
    padding: 6px 10px;
    font-size: 0.8rem;
  }
  
  .map-container {
    height: 200px;
  }
  
  .modal-content {
    width: 98vw;
    min-width: 280px;
  }
}
</style>
