<template>
  <div id="all">
    <div class="fault-management-dashboard">
      <h1>故障管理仪表</h1>
      <p>故障管理 > 仪表盘</p>

      <div class="top-container">
        <div class="fault-box">
          <div class="top">
            <p>今日故障</p>
            <span class="increase" :class="{ 'text-red': (todayIncrease ) > 0 }">
              {{ (todayIncrease) > 0 ? '↑ ' + (todayIncrease ) : '→ 0' }}
            </span>
          </div>
          <p class="fault-count">{{ todayFaults }}</p>
        </div>

        <div class="fault-limit-box">
          <p class="limit-title">本月累计故障数</p>
          <p class="limit-count">{{ todayFaults  + 1}}/{{ limit }}</p>
          <div class="progress-bar">
            <div class="progress" :style="{ width: progressWidth }"></div>
          </div>
        </div>
      </div>

      <div class="middle-container">
        <div class="middle-box"><gu4/></div>
        <div class="middle-box"><gu5/></div>
      </div>

      <div class="bottom-container">
        <gu6/>
      </div>

      <div class="askai-container">
        <askai />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Gu4 from "../components3/gu4.vue";
import Gu5 from "../components3/gu5.vue";
import Gu6 from "../components3/gu6.vue";
import Askai from "../components1/askai.vue";

export default {
  name: 'FaultManagementDashboard',
  components: {Askai, Gu6, Gu5, Gu4 },
  data() {
    return {
      todayFaults: 0,
      todayIncrease: 0,
      monthlyFaults: 0,
      limit: 100,
      isLoading: false
    };
  },
  computed: {
    progressWidth() {
      return this.limit === 0
          ? '0%'
          : `${Math.min((this.monthlyFaults / this.limit) * 100, 100)}%`;
    }
  },
  mounted() {
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      this.isLoading = true;
      try {
        const response = await axios.get('http://localhost:5000/dashboard');
        const {todayFaults, increase, monthlyFaults, limit} = response.data;

        this.todayFaults = todayFaults;
        this.todayIncrease = increase;
        this.monthlyFaults = monthlyFaults;
        this.limit = limit;
      } catch (error) {
        console.error('获取故障数据失败:', error);
        if (error.response) {
          console.error('状态码:', error.response.status);
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#all {
  padding: 20px;
  min-height: 100vh;
  background-color: #F5F7FA;
  padding-left: 30px;
}

.fault-management-dashboard {
  font-family: Arial, sans-serif;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.fault-management-dashboard h1 {
  font-size: 1.5em;
  margin-bottom: 8px;
}

.fault-management-dashboard > p {
  margin-bottom: 20px;
  color: #666;
}

/* 顶部容器 - 包含两个小框 */
.top-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.fault-box, .fault-limit-box {
  flex: 1;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  min-height: 120px;
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 1rem;
  color: #555;
}

.fault-count {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1a73e8;
  margin-top: 8px;
}

.increase {
  color: #d32f2f;
  font-weight: bold;
  font-size: 1rem;
}

.text-red {
  color: red;
}

.limit-title {
  font-size: 1rem;
  color: #555;
  margin-bottom: 8px;
}

.limit-count {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 12px;
}

.progress-bar {
  background: #f0f0f0;
  border-radius: 4px;
  height: 8px;
  width: 100%;
  overflow: hidden;
}

.progress {
  background: #1a73e8;
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 中部容器 - 包含两个大框 */
.middle-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  height: 500px;
}

.middle-box {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

/* 底部容器 - 单个大框 */
.bottom-container {
  width: 100%;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

/* AskAI容器 */
.askai-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .middle-container {
    flex-direction: column;
    height: auto;
  }

  .middle-box {
    height: 400px;
    margin-bottom: 20px;
  }

  .middle-box:last-child {
    margin-bottom: 0;
  }
}
</style>