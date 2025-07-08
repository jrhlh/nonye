<template>
  <div id="app">
    <div class="scroll-container">
      <div class="home-container">
        <div class="home-box">
          <div class="home-right">
            <img src="../assets/syh2.png" alt="">
          </div>
          <div class="home-left">
            <div class="home-top">
              <div class="nav-container">
                <div class="top-left">
                  <img src="../assets/图层%204.png" alt="">
                  <p>禾境智联</p>
                </div>
                <div class="top-middle">
                  <p @click.prevent="handleNavigation('Home1')">首页</p>
                  <p @click.prevent="handleNavigation('Shu2')">数据报表</p>
                  <p @click.prevent="handleNavigation('Gu3')">故障列表</p>
                  <p @click.prevent="handleNavigation('She4')">设备管理</p>
                  <p @click.prevent="handleNavigation('Pople5')">人员管理</p>
                </div>

                <!-- 动态显示：未登录时显示 LOGIN，登录后显示用户名 + 登出按钮 -->
                <div class="top-right-container">
                  <div v-if="isLoggedIn">
                    <span class="username-display">{{ username }}</span>
                    <button class="logout-button" @click="logout">Logout</button>
                  </div>
                  <button v-else class="top-right-button" @click="goToLogin">LOGIN</button>
                </div>

              </div>
            </div>
            <div class="home-main">
              <h1>禾境智联HorizonLink</h1>
              <div :style="{width:'90%',paddingTop:'10px'}">
                <p style="line-height: 1.5; font-size: 22px">
                  Lorem ipsum dolor sit amet consectetur adipisicing elit. Quaerat eveniet hic natus? Nihil, repudiandae.
                  A quaerat vel recusandae quis corrupti porro nulla possimus dolore consequuntur perferendis.
                  Nulla, deserunt atque ipsa soluta quaerat quasi saepe a ea numquam incidunt minus quo iure.
                </p>
              </div>

            </div>
            <button class="join-button">join us</button>
            <img src="../assets/syh1.png" alt="" class="syh">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态管理
const isLoggedIn = ref(false)
const username = ref('')

// 页面加载时检查登录状态
onMounted(() => {
  const storedUser = localStorage.getItem('username')
  if (storedUser) {
    isLoggedIn.value = true
    username.value = storedUser
  }
})

// 跳转登录页
const goToLogin = () => {
  router.push('/login')
}

// 登出逻辑
const logout = () => {
  localStorage.removeItem('username')
  localStorage.removeItem('token')
  isLoggedIn.value = false
  username.value = ''
  router.push('/login')
}

// 统一导航处理函数
const handleNavigation = (pageName: string) => {
  if (!isLoggedIn.value) {
    goToLogin()
    return
  }

  // 路由映射表
  const routeMap: Record<string, string> = {
    'Home1': '/dashboard',
    'Shu2': '/reports',
    'Gu3': '/monitoring',
    'She4': '/devices',
    'Pople5': '/personnel'
  }

  const targetRoute = routeMap[pageName] || '/dashboard'
  router.push(targetRoute)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
#app {
  min-height: 100vh;
  min-width: 100vw;
  margin: 0;
  padding: 0;
  position: relative;
}

.scroll-container {
  overflow: hidden;
  height: 100vh;
  width: 100%;
  background-color: white;

}

.home-container {
  margin: auto;
  width: 800px;
  height: 500px;
  position: relative;

}

.home-right img {
  width: 90vh;
  position: absolute;
  right: -370px;
  top: 120px;
}

.home-left {
  position: relative;
  right: 320px;
  width: 640px;
}
.syh{
  width: 94%;
}
.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  width:  100vw;
  padding-right: 90px;
  gap: 30px;

}

.top-left {
  font-size: 24px;
  font-weight: bold;
  position: relative;
  top: -20px;
}

.top-left p{
  position: relative;
  top: -16px;
  right: -48px;
  font-size:  30px;
}

.top-left img{
  width: 40px;
}

.top-middle {
  margin-left: 500px;
  align-items: center;
  gap: 45px;
  font-size: 22px;
  position: relative;
  top: -15px;
  display: flex;
  justify-content: space-around;

  padding-right: 80px;
}

.top-middle p {
  margin: 0;
}
.top-right-button {
  width: 100px;
  height: 40px;
  border-radius: 10px;
  background-color: #4b7fea;
  color: white;
  font-size: 16px;
  font-weight: bold;
  border: none;
  position: relative;
  right: 135px;
  top: -15px;
}

.home-main h1 {
  margin-top: 65px;
  font-size: 65px;
  letter-spacing: 2px;
}

.home-main p {
  margin-top: 40px;
  font-size: 20px;
  line-height: 26px;
  color: #939292;
}

.join-button {
  margin-top: 40px;
  width: 170px;
  height: 50px;
  border-radius: 23px;
  background-color: #4b7fea;
  color: white;
  font-size: 20px;
  font-weight: bold;
  border: none;
}

.home-left img {
  position: relative;
  top: 30px;
}
</style>