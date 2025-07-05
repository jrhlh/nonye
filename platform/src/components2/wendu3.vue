<template>
  <div class="top">
    <h2 style="font-size: 34px">温度分析</h2>
  </div>
  <!-- 温度阈值设置卡片 -->
  <div class="analysis-card">
    <h2 class="card-title" style="font-size: 25px">数据报表：温度阈值设置</h2>
    <div class="threshold-controls">
      <span class="threshold-label">温度阈值</span>
      <el-input-number
          v-model="temperatureThreshold"
          :min="0"
          :max="50"
          :step="1"
          size="small"
          class="threshold-input"
          @blur="handleBlur"
      />
      <el-button type="primary" size="small" @click="applyThreshold">执行</el-button>
    </div>
    <div class="tubiao">
      <wendu4/>
    </div>
  </div>

  <!-- 温度统计数据卡片 -->
  <div class="analysis-card">
    <h2 class="card-title" style="font-size: 25px">数据报表：温度统计</h2>
    <div class="stats-grid">
      <div class="stat-item" style="background-color: #f0f9eb;">
        <div class="stat-label">当前温度</div>
        <div class="stat-value">24.5℃</div>
      </div>
      <div class="stat-item" style="background-color: #fef0f0;">
        <div class="stat-label">24小时最高温</div>
        <div class="stat-value">28.8℃</div>
      </div>
      <div class="stat-item" style="background-color: #e6f7ff;">
        <div class="stat-label">24小时最低温</div>
        <div class="stat-value">21.2℃</div>
      </div>
      <div class="stat-item" style="background-color: #fdf6ec;">
        <div class="stat-label">平均温度</div>
        <div class="stat-value">24.1℃</div>
      </div>
    </div>
  </div>

  <!-- 温度异常记录卡片 -->
  <div class="analysis-card">
    <h2 class="card-title" style="font-size: 25px">数据报表：温度异常记录</h2>
    <el-table :data="anomalyRecords" style="width: 100%">
      <el-table-column prop="time" label="时间" width="180"></el-table-column>
      <el-table-column prop="temperature" label="温度" width="120"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status.includes('高温') ? 'danger' : 'info'" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="action" label="处理情况"></el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { ElMessageBox } from 'element-plus';
import Wendu4 from "../components2/wendu4.vue";
import eventBus from '../utlis/event-bus'; // 引入事件总线

// 从全局状态获取初始阈值
const temperatureThreshold = ref(eventBus.getThreshold());
const previousThreshold = ref(eventBus.getThreshold());

// 处理输入框失去焦点事件
const handleBlur = () => {
  if (temperatureThreshold.value !== previousThreshold.value) {
    showConfirmDialog('温度阈值', temperatureThreshold.value, applyThreshold);
  }
};

// 显示确认弹窗
const showConfirmDialog = (type: string, value: number, onConfirm: () => void) => {
  ElMessageBox.confirm(
      `确定要将 ${type} 修改为：${value}℃ 吗？`,
      '确认修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'custom-message-box',
        center: false
      }
  )
      .then(() => {
        onConfirm();
      })
      .catch(() => {
        // 用户点击了取消，恢复全局阈值
        temperatureThreshold.value = eventBus.getThreshold();
        console.log('已取消修改，阈值已恢复为:', eventBus.getThreshold());
      });
};

// 应用阈值到全局状态
const applyThreshold = () => {
  eventBus.setThreshold(temperatureThreshold.value);
  previousThreshold.value = temperatureThreshold.value;
  console.log('应用温度阈值:', temperatureThreshold.value);
};

// 异常记录数据
const anomalyRecords = ref([
  {
    time: '2024-07-30 14:30',
    temperature: '28.9℃',
    status: '高温预警',
    action: '建议开启通风降温'
  },
  {
    time: '2024-07-30 02:15',
    temperature: '18.2℃',
    status: '低温预警',
    action: '建议开启加热设备'
  }
]);

// 监听全局阈值变化，同步到本地
onMounted(() => {
  eventBus.on('thresholdUpdated', (threshold: number) => {
    temperatureThreshold.value = threshold;
    previousThreshold.value = threshold;
  });
});

onBeforeUnmount(() => {
  // 清理事件监听
  eventBus.emit('thresholdUpdated', null);
});
</script>

<style scoped>
/* 保留原有CSS样式 */
.top h2 {
  font-size: 1.7rem;
  position: relative;
  top: -5px;
  margin-bottom: 10px;
}

/* 卡片通用样式 */
.analysis-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.analysis-card h2 {
  padding-bottom: 17px;
}

.card-title {
  color: #333;
  font-size: 1.2rem;
  margin-bottom: 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  position: relative;
  right: 15px;
}

/* 阈值设置区域 */
.threshold-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  right: -5px;
  z-index: 1000;
}

.threshold-label {
  font-weight: bold;
  color: #555;
  font-size: 17px;
}

.threshold-input {
  width: 120px;
}

.tubiao {
  margin-bottom: -30px;
}

/* 统计数据区域 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.stat-item {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 15px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}
</style>