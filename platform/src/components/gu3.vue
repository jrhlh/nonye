<template>
  <div id="all">
    <div class="fault-management-dashboard">
      <h1>故障管理仪表</h1>
      <p>故障管理 > 仪表盘</p>

      <div class="fault-container">
        <div class="fault-box">
          <div class="top">
            <p>今日故障</p>
            <!-- 动态显示故障增加数，红色箭头 -->
            <span class="increase" :class="{ 'text-red': todayIncrease > 0 }">
              {{ todayIncrease > 0 ? '↑ ' + todayIncrease : '→ 0' }}
            </span>
          </div>
          <!-- 动态显示今日故障数 -->
          <p class="fault-count">{{ todayFaults }}</p>
        </div>

        <div class="fault-limit-box">
          <p style="font-size: 1.1rem">本月累计故障数</p>
          <!-- 动态显示累计故障数/上限 -->
          <p class="limit-count">{{ monthlyFaults }}/{{ limit }}</p>
          <div class="progress-bar">
            <!-- 动态计算进度条宽度 -->
            <div class="progress" :style="{ width: progressWidth }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="middle-container">
      <div class="middle-left"><gu4/></div>
      <div class="middle-right"><gu5/></div>
    </div>

    <div class="under"><gu6/></div>
    <div>
      <!-- 你的页面内容 -->
      <askai />
    </div>
  </div>
</template>

<script>
import axios from 'axios'; // 引入HTTP请求库
import Gu4 from "../components3/gu4.vue";
import Gu5 from "../components3/gu5.vue";
import Gu6 from "../components3/gu6.vue";
import Askai from "../components/dashboard/ai/askai.vue";

export default {
  name: 'FaultManagementDashboard',
  components: {Askai, Gu6, Gu5, Gu4 },
  data() {
    return {
      todayFaults: 0,       // 今日故障数
      todayIncrease: 0,     // 今日故障增减数
      monthlyFaults: 0,     // 本月累计故障数
      limit: 300,           // 故障上限（可从后端获取或固定值）
      isLoading: false      // 加载状态
    };
  },
  computed: {
    progressWidth() {
      // 防止除数为0，添加安全判断
      return this.limit === 0
          ? '0%'
          : `${(this.monthlyFaults / this.limit) * 100}%`;
    }
  },
  mounted() {
    this.fetchDashboardData(); // 组件挂载后立即获取数据
  },
  methods: {
    async fetchDashboardData() {
      this.isLoading = true; // 显示加载状态
      try {
        // 调用后端故障仪表盘接口（需与后端API路径一致）
        const response = await axios.get('http://localhost:5000/dashboard');
        const {todayFaults, increase, monthlyFaults, limit} = response.data;

        // 更新数据到组件状态
        this.todayFaults = todayFaults;
        this.todayIncrease = increase;
        this.monthlyFaults = monthlyFaults;
        this.limit = limit;
      } catch (error) {
        console.error('获取故障数据失败:', error);
        // 处理错误（如提示用户）
        if (error.response) {
          console.error('状态码:', error.response.status);
        }
      } finally {
        this.isLoading = false; // 隐藏加载状态
      }
    }
  }
}
</script>

<style scoped>
/* 原有CSS样式保持不变 */
* {
  margin: 0;
  padding: 0;
}

#all {
  padding: 20px;
  height: 100vh;
  overflow-y: scroll;
  scrollbar-width: none;
  -ms-overflow-style: none;
  background-color: #fbfbfb;
}

#all::-webkit-scrollbar {
  display: none;
}

.fault-management-dashboard {
  font-family: Arial, sans-serif;
  width: 99.3%;
  margin-left: 6px;
}

.fault-management-dashboard h1 {
  font-size: 1.5em;
}

.fault-management-dashboard p {
  margin-top: 10px;
  margin-bottom: 20px;
  margin-left: 2px;
}

.fault-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;

}

.fault-box, .fault-limit-box {
  border: 1px solid #f8f6f6;
  border-radius: 5px;
  padding-left: 15px;
  width: 48%;
  height: 65px;
  box-shadow: 0 2px 3px 1px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.fault-box {
  height: 120px;
}

.fault-limit-box {
  height: 120px;
}

.top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.fault-count {
  font-size: 2.3em;
  color: #1a73e8;
  position: relative;
  top: -18px;
}

.increase {
  color: red;
  font-size: 1.1rem;
  position: relative;
  top: 15px;
  right: 20px;
}

.progress-bar {
  background: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
  height: 10px;
  position: relative;
  top: -20px;
  width: 97%;
}

.progress {
  background: #1a73e8;
  height: 100%;
  border-radius: 5px;
  margin-left: 2px;
}

.limit-count {
  font-size: 2.1em;
  text-align: left;
  position: relative;
  top: -12px;
}

.middle-container {
  display: flex;
  height: 500px;
  margin-top: 26px;
  margin-left: 8px;
  border-radius: 5px;
}

.middle-left {
  width: 45%;
}

.under {
  width: 99.1%;
  height: 670px;
  margin-top: 20px;
  position: relative;
  right: -8px;
}
</style>