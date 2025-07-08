<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue';
import {ElMessageBox} from 'element-plus';
import shidu4 from "../components2/shidu4.vue"

const activeButton = ref(null);
const lowerThreshold = ref(70);
const upperThreshold = ref(85);
const previousLowerThreshold = ref(70); // 保存上一次确认的下限阈值
const previousUpperThreshold = ref(85); // 保存上一次确认的上限阈值
const isEditingThreshold = ref(false); // 标记是否正在编辑阈值
const thresholdInputRef = ref(null); // 阈值输入框的引用
let blurTimeout = null;

const handleButtonClick = (buttonType) => {
  activeButton.value = buttonType;
  console.log(`${buttonType} 按钮被点击`);
};

const showConfirmationDialog = (type, value, onConfirm) => {
  ElMessageBox.confirm(
      `确定要将${type}修改为：${value}% 吗？`,
      '确认修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
  )
      .then(() => {
        onConfirm();
      })
      .catch(() => {
        // 恢复为上一次确认的值
        if (type === '下限阈值') {
          lowerThreshold.value = previousLowerThreshold.value;
        } else if (type === '上限阈值') {
          upperThreshold.value = previousUpperThreshold.value;
        }
      });
};

const handleBlur = (type) => {
  // 清除之前的定时器，防止多次触发
  if (blurTimeout) {
    clearTimeout(blurTimeout);
  }

  // 延迟执行，确保点击事件不会立即触发确认（避免冲突）
  blurTimeout = setTimeout(() => {
    if (type === 'lower' && lowerThreshold.value !== previousLowerThreshold.value) {
      showConfirmationDialog('下限阈值', lowerThreshold.value, () => {
        previousLowerThreshold.value = lowerThreshold.value;
      });
    } else if (type === 'upper' && upperThreshold.value !== previousUpperThreshold.value) {
      showConfirmationDialog('上限阈值', upperThreshold.value, () => {
        previousUpperThreshold.value = upperThreshold.value;
      });
    }
  }, 200);
};

const handleFocus = () => {
  isEditingThreshold.value = true; // 标记为正在编辑
};

const handleClickOutside = (event) => {
  if (thresholdInputRef.value && !thresholdInputRef.value.contains(event.target)) {
    handleBlur('lower'); // 可以根据实际情况判断是下限还是上限
    handleBlur('upper'); // 这里简单处理为同时检查上下限，可以根据需求优化
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
  if (blurTimeout) {
    clearTimeout(blurTimeout);
  }
});
</script>

<template>
  <div class="humidity-analysis">
    <h2>湿度分析</h2>
    <p>实时监测土壤湿度变化，预测未来趋势</p>

    <div class="stats-container">
      <div class="stat-box">
        <p>当前湿度</p>
        <p class="value">75%</p>
      </div>
      <div class="stat-box">
        <p>今日平均</p>
        <p class="value">68%</p>
      </div>
      <div class="stat-box">
        <p>最高湿度</p>
        <p class="value">82%</p>
      </div>
      <div class="stat-box">
        <p>最低湿度</p>
        <p class="value">55%</p>
      </div>
    </div>
    <div class="threshold-settings" ref="thresholdInputRef">
      <div class="threshold-item">
        <label>下限阈值</label>
        <input
            type="number"
            v-model="lowerThreshold"
            @focus="handleFocus"
            @blur="handleBlur('lower')"
            min="0"
            max="100"
        />
        <span>%RH</span>
      </div>
      <div class="threshold-item">
        <label>上限阈值</label>
        <input
            type="number"
            v-model="upperThreshold"
            @focus="handleFocus"
            @blur="handleBlur('upper')"
            min="0"
            max="100"
        />
        <span>%RH</span>
      </div>
      <div class="unit-display">
        %RH/g·m³
      </div>
    </div>
    <div class="action-buttons">
      <button
          class="btn auto"
          :class="{ active: activeButton === 'auto' }"
          @click="handleButtonClick('auto')"
          style="border: 1px solid #c1d3e1"
      >
        自动加湿
      </button>
      <button
          class="btn vent"
          :class="{ active: activeButton === 'vent' }"
          @click="handleButtonClick('vent')"
          style="border: 1px solid #dfd0bc"
      >
        通风除湿
      </button>
      <button
          class="btn maintain"
          :class="{ active: activeButton === 'maintain' }"
          @click="handleButtonClick('maintain')"
          style="border: 1px solid #d8d8da"
      >
        维持现状
      </button>
    </div>

    <div class="chart-container">
      <div class="chart-placeholder">
        <shidu4/>
      </div>
    </div>

    <div class="chart-stats">
      <p>24h平均值: 67%</p>
      <p>预测最高值: 85%</p>
      <p>预测最低值: 52%</p>
      <p>波动范围: 33%</p>
    </div>

    <div class="temperature-alerts">
      <h3>湿度异常预警</h3>
      <div class="alert">
        <span>5月30日</span>
        <span>湿度超过上限阈值 15%</span>
        <span class="status">已处理</span>
      </div>
      <div class="alert">
        <span>6月16日</span>
        <span>湿度低于下限阈值 18%</span>
        <span class="status">已处理</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 样式保持不变 */
.humidity-analysis {
  font-family: Arial, sans-serif;
  max-width: 800px;
  background-color: white;
  border-radius: 8px;
}

h2 {
  margin-bottom: 12px;
  margin-top: 0;
  color: #333;
  font-size: 1.7rem;
  position: relative;
  left: -20px;
}

p {
  margin: 5px 0;
  color: #666;
}

.stats-container {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
  gap: 10px;
}

.stat-box {
  flex: 1;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  background-color: #f8f9fa;
}

.stat-box:nth-child(1) {
  background-color: #e6f3ff;
}

.stat-box:nth-child(2) {
  background-color: #f0f9eb;
}

.stat-box:nth-child(3) {
  background-color: #f8e8fd;
  color: #a855f7;
}

.stat-box:nth-child(4) {
  background-color: #fff7e6;
  color: #f97316;
}

.value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 5px;
}

.threshold-settings {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.threshold-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.threshold-item label {
  font-size: 14px;
  color: #666;
}

.threshold-item input {
  width: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.threshold-item input:focus {
  outline: none;
  border-color: #4d90fe;
  box-shadow: 0 0 0 2px rgba(77, 144, 254, 0.2);
}

.threshold-item span {
  font-size: 14px;
  color: #666;
}

.unit-display {
  font-size: 14px;
  color: #999;
  font-style: italic;
}

.action-buttons {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  flex: 1;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn.active {
  transform: translateY(0);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auto {
  background-color: #e0f2fe;
  color: #0369a1;
}

.auto.active {
  background-color: #bae6fd;
}

.vent {
  background-color: #ffedd5;
  color: #9a3412;
}

.vent.active {
  background-color: #fed7aa;
}

.maintain {
  background-color: #f3f4f6;
  color: #4b5563;
}

.maintain.active {
  background-color: #e5e7eb;
}

.chart-container {
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FFFFFF;
}

.chart-placeholder {
  color: #999;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  font-size: 14px;
  color: #666;
}

.temperature-alerts {
  background-color: #F0F9EB;
  padding: 15px;
  border-radius: 8px;
}

.temperature-alerts h3 {
  margin-top: 0;
  color: #069f35;
}

.alert {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
}

.status {
  color: #28A77E;
  font-weight: bold;
  background-color: #CCFFCC;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

:deep(.custom-message-box) {
  height: 300px !important; /* 设置弹窗高度 */
  max-height: 80vh !important; /* 最大高度为视口的 80% */
  display: flex;
  flex-direction: column;
}

:deep(.custom-message-box .el-message-box__content) {
  flex: 1; /* 内容区域占据剩余空间 */
  overflow-y: auto; /* 如果内容超出，显示滚动条 */
}
</style>