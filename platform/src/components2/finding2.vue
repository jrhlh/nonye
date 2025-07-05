<template>
  <div class="key-findings-container">
    <h2 class="title">关键发现</h2>
    <ul class="findings-list">
      <!-- 使用v-for动态渲染随机数据，保持原有HTML结构 -->
      <li v-for="item in shuffledData" :key="item.title" class="finding-item">
        <span :class="['finding-icon', item.type]">{{ item.icon }}</span>
        <div class="finding-content">
          <span class="finding-title">{{ item.title }}</span>
          <span class="finding-description">{{ item.description }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import {ref, onMounted} from 'vue';

export default {
  setup() {
    // 定义土壤检测关键发现数据（⚠️全部改为!）
    const findingsData = [
      {
        icon: '✓',
        type: 'success',
        title: '最佳pH水平',
        description: '土壤pH处于作物生长的理想范围内，有助于促进养分吸收和微生物活性。'
      },
      {icon: '!', type: 'warning', title: '氮缺乏', description: '土壤中氮含量不足，可能会限制作物的生长和发育。'},
      {
        icon: '!',
        type: 'alert',
        title: '高盐度',
        description: '土壤盐度较高，可能会影响作物的水分吸收和养分利用效率。需密切监测灌溉水的质量和用量。'
      },
      {
        icon: '✓',
        type: 'success',
        title: '充足磷储备',
        description: '土壤中磷元素含量充裕，能够有效支持作物根系发育和开花结果，对提升作物产量具有积极作用。'
      },
      {
        icon: '!',
        type: 'warning',
        title: '钾元素失衡',
        description: '土壤钾含量低于正常水平，易导致作物抗逆性下降，增加倒伏风险，需及时补充钾肥。'
      },
      {
        icon: '!',
        type: 'alert',
        title: '重金属超标',
        description: '土壤中镉、铅等重金属含量超出安全阈值，可能造成作物重金属富集，需采取土壤修复措施降低污染。'
      }
    ];

    // 随机排序并截取3条数据的函数
    const getRandomItems = (data, count) => {
      const shuffled = [...data].sort(() => Math.random() - 0.5);
      return shuffled.slice(0, count);
    };

    // 定义响应式数据存储随机结果
    const shuffledData = ref(getRandomItems(findingsData, 3));

    // 组件挂载时重新生成随机数据
    onMounted(() => {
      shuffledData.value = getRandomItems(findingsData, 3);
    });

    return {
      shuffledData
    };
  }
};
</script>

<style scoped>
/* 保持原有样式不变，调整alert类型样式（图标颜色与背景） */
.key-findings-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 395px;
  margin: 0;
  padding-left: 20px;
}

h2 {
  position: relative;
  top: 20px;
}

.title {
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 36px;
  padding-bottom: 10px;
  width: 390px;
  border-bottom: 1px solid #eee;
  position: relative;
  right: 11px;
}

.findings-list {
  list-style: none;
  padding-left: 7px;
  margin: 0;
}

.finding-item {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.finding-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #4CAF50;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.finding-icon.warning {
  background-color: #FFC107;
}

.finding-icon.alert {
  background-color: #f44336; /* 红色背景，突出警告感 */
  color: white;
}

.finding-content {
  display: flex;
  flex-direction: column;
}

.finding-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.finding-description {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}
</style>