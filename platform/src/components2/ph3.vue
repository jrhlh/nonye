<template>
  <div id="all">
<!--    抽屉中的组件-->
    <h2>土壤PH值检测</h2>
    <div class="top-box">
      <div class="box01">
        <h1>{{ currentPh }}</h1>
        <p>当前pH值</p>
        <div class="top-box-item">
          <div class="icons">
            <svg t="1748146770314" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9500" width="200" height="200">
              <path d="M896 896H96a32 32 0 0 1-32-32V224a32 32 0 0 1 64 0v608h768a32 32 0 1 1 0 64z" p-id="9501" fill="#4CAF50"></path>
              <path d="M247.008 640a32 32 0 0 1-20.992-56.192l200.992-174.24a32 32 0 0 1 42.272 0.288l172.128 153.44 229.088-246.304a32 32 0 0 1 46.88 43.616l-250.432 269.216a31.936 31.936 0 0 1-44.704 2.08l-174.56-155.52-179.744 155.84a31.872 31.872 0 0 1-20.928 7.776z" p-id="9502" fill="#4CAF50"></path>
            </svg>
            <p>酸化速率: <span>{{ acidificationRate }} </span>pH/月</p>
          </div>
        </div>
      </div>
      <div class="box02">
        <div class="recommendation">
          <div class="recommendation-item01">
            <svg t="1748177369120" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4378" width="200" height="200">
              <path d="M477.717333 633.536c-91.2 41.472-166.826667 25.898667-204.778666 12.650667l115.648-307.861334c1.386667-3.584 2.069333-7.36 2.048-11.157333V67.968h234.069333v257.024c0 3.946667 0.725333 7.808 2.133333 11.477333l106.026667 273.813334c-63.36-13.717333-158.293333-20.864-255.146667 23.253333z m475.861334 344.981333L698.133333 319.082667V67.968h42.154667c20.266667 0 36.714667-15.210667 36.714667-33.984S760.576 0 740.288 0H279.104c-20.266667 0-36.714667 15.210667-36.714667 33.984s16.426667 33.984 36.714667 33.984h38.186667v253.418667L70.293333 978.858667c-3.904 10.389333-2.112 21.888 4.757334 30.848s18.026667 14.293333 29.909333 14.293333h814.037333a37.76 37.76 0 0 0 30.058667-14.421333c6.869333-9.045333 8.554667-20.629333 4.522667-31.061334z" fill="#2095f3" p-id="4379"></path>
            </svg>
            <h3>建议石灰用量：</h3>
            <p>{{ limeDosage }}kg/亩</p>
          </div>
          <div class="recommendation-item">
            <svg t="1748177539509" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="15491" width="200" height="200">
              <path d="M612.290147 560.971341c344.559477 60.231803 369.467773-339.711052 369.467773-339.711052C598.22071 193.869453 612.290147 560.971341 612.290147 560.971341z" fill="#12803B" p-id="15492"></path>
              <path d="M42.4713 190.703343c1.942235 0.121773 17.494443 1.199315 41.836851 5.78168-26.108634-4.683672-41.967834-5.788843-42.059931-5.794983C42.322921 190.69311 42.396599 190.698227 42.4713 190.703343c-0.132006-0.008186-0.218988-0.013303-0.224104-0.013303 0 0-0.004093 0-0.004093 0l0 0-0.001023 0c0 0 0.001023 0 0.001023 0 7.349385 348.193237 320.04413 379.335515 448.876334 406.539086 15.860223 75.53944 20.753673 165.070546 9.771551 271.189446-1.927909 18.629289 14.760169 34.114982 33.487695 34.114982l0.001023 0c18.808368 0 33.948183-15.398712 33.625842-34.205033C563.512211 606.290503 568.007595 219.915665 42.4713 190.703343z" fill="#12803B" p-id="15493"></path>
            </svg>

            <h3>推荐作物：</h3>
          </div>
          <div class="crops">
            <span v-for="crop in recommendedCrops" :key="crop">{{ crop }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- 中间阈值部分 -->
    <div class="full-width-div">
      <div class="middle-box">
        <div class="box1">
          <p>酸性阈值</p>
          <input
              v-model="acidThreshold"
              @blur="handleBlur('acid')"
              type="text" class="values" value="5.5" style="padding-left: 10px;font-size: 17px;color: #1a1a1a;">
        </div>
        <div class="box2">
          <p>碱性阈值</p>
          <input
              v-model="alkaliThreshold"
              @blur="handleBlur('alkali')"
              type="text" class="values02" value="8.5" style="padding-left: 10px;font-size: 17px;color: #1a1a1a;">
        </div>
        <div class="box3">
          <button class="button01" @click="adjustWithLime">
            <svg t="1748188616712" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3170" data-spm-anchor-id="a313x.search_index.0.i1.87e73a81qgjsSz" width="200" height="200">
              <path d="M691.2 51.2a25.6 25.6 0 0 1 4.608 50.7904L691.2 102.4H665.6v179.968a384 384 0 0 0 58.4704 203.6736l9.1136 13.8752 177.1008 257.5872c25.2928 36.8128 28.5696 84.4288 8.6016 124.3648a118.272 118.272 0 0 1-96.8192 65.024l-8.9088 0.3072H210.8416a118.2208 118.2208 0 0 1-105.728-65.3312 122.624 122.624 0 0 1 3.584-116.3264l5.0176-8.0384 177.152-257.536A384 384 0 0 0 357.9904 299.008L358.4 282.368V102.4h-25.6a25.6 25.6 0 0 1-4.608-50.7904L332.8 51.2h358.4zM614.4 102.4H409.6v179.968a435.2 435.2 0 0 1-66.9184 231.8848l-9.6768 14.6944-177.1008 257.5872c-14.6944 21.4016-16.64 49.152-5.0176 72.3968a67.072 67.072 0 0 0 53.0944 36.7104l6.8608 0.3584h602.3168c25.3952 0 48.5888-14.336 59.904-37.0688a71.424 71.424 0 0 0-0.9728-65.792l-3.9936-6.6048-177.152-257.5872a435.2 435.2 0 0 1-76.1856-228.9664L614.4 282.368V102.4z m0 409.6a25.6 25.6 0 0 1 20.6848 10.5472l197.2736 271.2576c8.0896 11.1104 12.4416 24.4736 12.4416 38.1952a38.4 38.4 0 0 1-38.4 38.4H217.6a38.4 38.4 0 0 1-38.4-38.4c0-13.7216 4.352-27.136 12.4416-38.1952l197.2736-271.2576A25.6 25.6 0 0 1 409.6 512z" fill="#2196F3" p-id="3171"></path>
            </svg>石灰调节
          </button>
          <button class="button02" @click="adjustWithSulfur">
            <svg t="1748189502695" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5509" width="200" height="200">
              <path d="M812.885333 868.352L628.053333 590.336H393.898667L210.602667 868.693333a31.573333 31.573333 0 0 0-5.12 17.92c0 16.896 14.165333 31.232 30.890666 31.232h551.082667c17.066667 0 30.890667-15.189333 30.890667-31.914666a38.741333 38.741333 0 0 0-5.461334-18.090667c0.170667 0.170667 0.341333 0.853333 0 0.512z m111.957334-35.84L698.368 494.933333a294.4 294.4 0 0 1-42.837333-158.549333V126.464c0-15.530667 3.413333-29.354667 8.192-41.813333h32.768a32.768 32.768 0 0 0 32.768-32.768v-6.826667a32.768 32.768 0 0 0-32.768-32.597333H327.338667a32.768 32.768 0 0 0-32.768 32.597333v6.826667c0 18.090667 14.677333 32.768 32.768 32.768h29.866666c5.12 12.8 9.045333 27.136 9.045334 42.837333v209.066667c0 58.197333-16.554667 112.298667-45.397334 158.549333l-111.274666 172.714667-110.933334 164.522666a136.704 136.704 0 0 0-20.48 72.704c0 63.317333 36.864 118.954667 142.848 118.954667h581.973334c106.154667 0 142.848-55.637333 142.848-118.954667a139.605333 139.605333 0 0 0-20.992-72.533333z m-66.730667 102.4c-9.898667 9.386667-26.282667 16.725333-55.466667 16.725333H220.842667c-29.013333 0-46.933333-7.850667-56.832-17.408a41.301333 41.301333 0 0 1-13.653334-30.037333c0-11.264 3.242667-22.869333 8.704-32.085333l223.744-339.626667c35.498667-56.832 55.637333-124.586667 55.637334-196.266667V84.821333h144.554666v251.562667c0 70.485333 17.578667 138.410667 53.930667 196.437333l226.986667 338.773334a60.586667 60.586667 0 0 1 9.045333 32.085333c0 14.336-8.874667 25.088-14.848 31.232z" fill="#FF5252" p-id="5510"></path>
            </svg>硫磺调节
          </button>
          <button class="button03" @click="autoBalance">
            <svg t="1748189189618" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4326" width="200" height="200">
              <path d="M956.2 651L826.9 380.8c-7.8-13.5-23.3-47.4-44.5-47.4-0.9 0-1.8 0.1-2.7 0.2-0.7 0-1.4-0.1-2.1-0.1H545.7V296c49.1-14.4 84.9-59.8 84.9-113.5 0-65.3-53-118.3-118.3-118.3S394 117.2 394 182.5c0 52.6 34.3 97.1 81.7 112.5v38.5H242.5c-1.2 0-2.4 0.1-3.6 0.2-1.1-0.2-2.2-0.3-3.4-0.3-12.6 0-27.3 12-43.5 47.4L66.8 651c-0.9 1.6-1.5 3.3-1.6 5h-0.1c-0.4 7-2.4 69.9 42.7 117.5 30.3 32 73.4 48.3 127.9 48.3 54.6 0 98-16.2 129.3-48.1 19.6-20.1 33.8-46.4 41-76.2 4.7-19.5 5.1-34.9 5.1-39.3 0.2-2.4-0.3-4.9-1.7-7.2L291 403.6h184.8V888H291c-19.3 0-35 15.7-35 35s15.7 35 35 35h442.1c19.3 0 35-15.7 35-35s-15.7-35-35-35H545.7V403.6h182.5L613.6 651c-0.9 1.6-1.5 3.3-1.6 5h-0.1c-0.4 7-2.4 69.9 42.7 117.5 30.3 32 73.4 48.3 127.9 48.3 54.6 0 98-16.2 129.3-48.1 19.6-20.1 33.8-46.4 41-76.2 4.7-19.5 5.1-34.9 5.1-39.3 0.1-2.4-0.4-4.9-1.7-7.2zM512.3 134.2c26.6 0 48.3 21.7 48.3 48.3s-21.7 48.3-48.3 48.3-48.3-21.6-48.3-48.3 21.7-48.3 48.3-48.3zM235.6 751.8c-34.3 0-60.1-8.8-76.7-26-17.3-18-22.2-42.3-23.5-55.9H340c-2 13.9-7.9 37.5-25.6 55.3-17.5 17.7-44 26.6-78.8 26.6z m-68-151.9l68.7-148.2 70.9 148.2H167.6z m615.6-148.3l70.9 148.2H714.4l68.8-148.2z m-0.8 300.2c-34.3 0-60.1-8.8-76.7-26-17.3-18-22.2-42.3-23.5-55.9h204.6c-2 13.9-7.9 37.5-25.6 55.3-17.5 17.7-44 26.6-78.8 26.6z" p-id="4327" fill="#4DB051"></path>
            </svg>自动平衡
          </button>
        </div>
      </div>
      <div class="tubiao">
        <ph4 :phData="phData"></ph4>
      </div>
    </div>
  </div>
</template>

<style>
#all {
  width: 100%;
  height: 100%;
  font-family: Arial, sans-serif;
}

#all h2{
  margin-top: 0;
  margin-left: 18px;
  color: #333;
  font-size: 1.7rem;
}

.top-box {
  width: 95%;
  height: 185px;
  margin-left: 20px;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  margin-top: 20px;
}

.box01 {
  padding: 10px;
  text-align: center;
  background-color: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.box01 h1 {
  font-size: 48px;
  margin: 0;
  color: #2196F3;
}

.box01 p {
  margin: 0 0;
  color: #666;
  font-size: 16px;
}

.box02 {
  padding: 15px;
  background-color: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
}

.icons {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.icons span {
  color: #4CAF50;
  font-weight: bold;
  padding-left: 5px;
  padding-right: 5px;
}

.icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.recommendation {
  display: flex;
  flex-direction: column;
  height: 100%;

}

.recommendation-item01 {
  display: flex;
  margin-bottom: 15px;
  margin-left: 3px;
}

.recommendation-item {
  display: flex;
  margin-bottom: 10px;
  margin-left: 3px;
}

.recommendation h3 {
  margin: 0 0 5px 0;
  font-size: 17px;
  color: #666;
  font-weight: 600;
}

.recommendation p {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: bold;
}

.crops {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 5px;
  margin-left: 3px;
}

.crops span {
  background-color: #f0f9eb;
  color: #4CAF50;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 19.9px;
  width: 87px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: static; /* 移除不必要的定位 */
}

.top-box-item {
  margin-top: 10px;
}

/* 新增的 div 样式 */
.full-width-div {
  width: 95.8%;
  background-color: #FFFFFF; /* 可根据需要更改背景颜色 */
  padding: 20px;
  box-sizing: border-box; /* 确保 padding 包含在宽度内 */
  position: relative;
  left: 16px;
  margin-top: 28px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
  height: 560px;
  padding-top: 35px;

}

.middle-box {
  display: flex;
  width: 100%;
  height: 60px;
}

.box1 {
  width: 18%;
  height: 60px;
  margin-right: 10px;
  margin-left: 3px;
  position: relative;

}

.box1 p {
  position: relative;

}
.box1 input {
  position: relative;
  top: 5px;
  width: 100px;
  height: 35px;
}

.box2 {
  width: 18%;
  height: 60px;
  position: relative;

}
.box2 input {
  position: relative;
  top: 5px;
  width: 100px;
  height: 35px;
}
.box2 p {
  position: relative;

}

.box3 {
  flex-grow: 1;
  display: flex;
  justify-content: flex-end; /* 将按钮对齐到右侧 */
  align-items: center; /* 垂直居中 */
  position: relative;
  top: -10px;
  right: -1px;
}

.threshold-input {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  text-align: center;
  font-size: 16px;
  outline: none;
  padding: 0 10px; /* 添加内边距，避免文字紧贴边框 */
  box-sizing: border-box; /* 确保padding不影响总宽度 */
}


.values {
  width: 57px;
  height: 30px;
  position: relative;
  top: -22px;
  border: #FF5252 2px solid;
  border-radius: 5px;
  padding-right: 50px;
}

.values02 {
  width: 60px;
  height: 30px;
  position: relative;
  top: -22px;
  border: #2196F3 2px solid;
  border-radius: 5px;
  padding-right: 50px;
}

.values p {
  padding: 6px 5px;
}

.values02 p {
  padding: 6px 5px;
}

.icon01 {
  width: 20px;
  height: 23px;
  margin-right: 8px;
}

.button01 {
  position: relative;
  top: 20px;
  height: 40px;
  width: 110px;
  font-size: 15px;
  background-color: #E3F2FD;
  border-radius: 7px;
  border: none;
  margin-right: 8px;
  display: flex; /* 使用 Flexbox 布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}

.button02 {
  position: relative;
  top: 20px;
  height: 40px;
  width: 110px;
  font-size: 15px;
  background-color: #FFEBEE;
  border-radius: 7px;
  border: none;
  margin-right: 8px;
  display: flex; /* 使用 Flexbox 布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}

.button03 {
  position: relative;
  top: 20px;
  height: 40px;
  width: 110px;
  font-size: 15px;
  background-color: #E8F5E9;
  border-radius: 7px;
  border: none;
  display: flex; /* 使用 Flexbox 布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}
/* 移除碱性阈值相关的样式 */
.values {
  height: 30px;
  position: relative;
  top: -22px;
  border: #FF5252 2px solid;
  border-radius: 5px;
}

.values p {
  padding: 6px 5px;
}

.values:focus, .values02:focus {
  outline: none; /* 确保聚焦时没有外边框 */
}



</style>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import Ph4 from './Ph4.vue';
import { ElMessageBox } from 'element-plus'
import axios from 'axios';

// 定义响应式数据
const currentPh = ref('6.5');
const acidificationRate = ref('-0.1');
const limeDosage = ref('120');
const recommendedCrops = ref(['水稻', '小麦', '玉米', '大豆']);
const phData = ref([]);
const acidThreshold = ref(5.5)
const alkaliThreshold = ref(8.5)
const previousAcidThreshold = ref(5.5)
const previousAlkaliThreshold = ref(8.5)

// 获取当前pH值数据
const fetchPhData = async () => {
  try {
    // 调用后端API获取5月27日的pH数据（假设后端接口已正确实现）
    const response = await axios.get('http://localhost:5000/ph_data/get_ph_data', {
      params: {
        time_range: 'today',
        sample_method: 'fixed'
      }
    });

    if (response.data.data.length > 0) {
      // 计算5月27日的平均pH值
      const avgPh = response.data.data.reduce((sum, item) => sum + item.ph, 0) / response.data.data.length;
      currentPh.value = avgPh.toFixed(2);

      // 根据pH值计算推荐的石灰用量（示例逻辑，实际应根据业务规则调整）
      calculateLimeDosage(avgPh);
    }
  } catch (error) {
    console.error('获取pH数据失败', error);
  }
};

const handleBlur = (type: string) => {
  if (type === 'acid' && acidThreshold.value !== previousAcidThreshold.value) {
    showConfirmationDialog('酸性阈值', acidThreshold.value, () => {
      previousAcidThreshold.value = acidThreshold.value
    })
  } else if (type === 'alkali' && alkaliThreshold.value !== previousAlkaliThreshold.value) {
    showConfirmationDialog('碱性阈值', alkaliThreshold.value, () => {
      previousAlkaliThreshold.value = alkaliThreshold.value
    })
  }
}

const showConfirmationDialog = (type: string, value: number, onConfirm: () => void) => {
  ElMessageBox.confirm(
      `确定要修改 ${type} 为 ${value} 吗？`,
      '确认修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'custom-message-box', // 添加自定义类名
        center: false // 确保内容不居中
      }
  )
      .then(() => {
        onConfirm()
      })
      .catch(() => {
        // 恢复原始值
        if (type === '酸性阈值') {
          acidThreshold.value = previousAcidThreshold.value
        } else {
          alkaliThreshold.value = previousAlkaliThreshold.value
        }
      })
}

// 根据pH值计算石灰用量
const calculateLimeDosage = (phValue: number) => {
  // 示例逻辑：pH越低，需要的石灰越多
  if (phValue < 5.5) {
    limeDosage.value = '150';
  } else if (phValue < 6.0) {
    limeDosage.value = '120';
  } else if (phValue < 6.6) {
    limeDosage.value = '80';
  } else {
    limeDosage.value = '0';
  }
};

// 石灰调节功能
const adjustWithLime = () => {
  alert(`即将使用${limeDosage.value}kg/亩的石灰进行土壤调节`);
  // 实际应用中这里应调用后端API执行调节操作
};

// 硫磺调节功能
const adjustWithSulfur = () => {
  alert('硫磺调节功能已触发');
  // 实际应用中这里应调用后端API执行调节操作
};

// 自动平衡功能
const autoBalance = () => {
  alert('自动平衡功能已触发');
  // 实际应用中这里应调用后端API执行自动调节操作
};

// 监听pH值变化，更新推荐作物
watch(currentPh, (newValue) => {
  const phNum = parseFloat(newValue);
  updateRecommendedCrops(phNum);
});

// 根据pH值更新推荐作物
const updateRecommendedCrops = (phValue: number) => {
  if (phValue < 5.5) {
    recommendedCrops.value = ['马铃薯', '草莓', '蓝莓'];
  } else if (phValue < 7.0) {
    recommendedCrops.value = ['水稻', '小麦', '玉米', '大豆'];
  } else {
    recommendedCrops.value = ['棉花', '甜菜', '苜蓿'];
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchPhData();

  // 模拟定期刷新数据（实际应用中可根据需求设置刷新频率）
  setInterval(fetchPhData, 60000); // 每分钟刷新一次
});
</script>