<script setup lang="ts">
import { ref } from 'vue'
import axios, { type AxiosError } from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const verificationCode = ref('')
const errorMessage = ref('')

let countdownInterval: number | undefined;

const login = () => {
  router.push('/login')
}

const sendVerificationCode = async () => {
  if (!username.value) {
    errorMessage.value = "请输入邮箱"
    return
  }

  try {
    await axios.post('http://localhost:5000/captcha/email', {
      email: username.value
    })

    let timeLeft = 60
    const button = document.querySelector('.get-code-button') as HTMLButtonElement

    if (button) {
      button.disabled = true
      button.textContent = `${timeLeft}s 后重试`

      if (countdownInterval !== undefined) {
        clearInterval(countdownInterval)
      }

      countdownInterval = window.setInterval(() => {
        timeLeft--
        button.textContent = `${timeLeft}s 后重试`
        if (timeLeft <= 0) {
          clearInterval(countdownInterval)
          countdownInterval = undefined
          button.disabled = false
          button.textContent = "获取验证码"
        }
      }, 1000)
    }

    alert('验证码已发送，请检查您的邮箱')
  } catch (error) {
    const axiosError = error as AxiosError
    if (axiosError.response) {
      const data = axiosError.response.data as { message?: string }
      errorMessage.value = data.message || '发送验证码失败'
    } else {
      errorMessage.value = '无法连接到服务器，请确保后端正在运行。'
    }
  }
}

const register = async () => {
  if (!verificationCode.value) {
    errorMessage.value = "请输入验证码"
    return
  }

  try {
    const response = await axios.post('http://localhost:5000/register', {
      username: username.value,
      password: password.value,
      code: verificationCode.value
    })

    if (response.status === 201) {
      alert('注册成功！即将跳转到登录页面')
      router.push('/login')
    }
  } catch (error) {
    const axiosError = error as AxiosError
    if (axiosError.response) {
      const data = axiosError.response.data as { message?: string }
      errorMessage.value = data.message || '注册失败，请检查输入内容'
    } else {
      errorMessage.value = '无法连接到服务器，请确保后端正在运行。'
    }
  }
}
</script>

<template>
  <div id="all">
    <div class="login-top">
      <img src="../assets/oo.png" alt="" class="fullscreen-bg">
      <div class="scroll-container">
        <div class="login-top-box">
          <h1>禾境智联后台管理系统</h1>
          <h2>注册</h2>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <!-- 用户名输入 -->
          <div class="input-group">
            <img src="../assets/信件.png" alt="" class="input-icon">
            <input v-model="username" type="text" placeholder="请输入邮箱" class="reinput-field">
          </div>
          <!-- 密码输入 -->
          <div class="input-group">
            <img src="../assets/suo.png" alt="" class="input-icon">
            <input v-model="password" type="password" placeholder="请输入密码" class="reinput-field">
          </div>
          <!-- 验证码输入 -->
          <div class="input-group code-input-group">
            <img src="../assets/验证码.png" alt="" class="input-icon">
            <input type="text" v-model="verificationCode" placeholder="短信验证码" class="reinput-field01">
            <button class="get-code-button" @click.prevent="sendVerificationCode">获取验证码</button>
          </div>
          <button @click="register" class="login-button">注册</button>
          <p class="login-p" style="padding-left:5px" @click.prevent="login">已有帐户？去登录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.scroll-container {
  overflow: hidden;
  height: 100vh;
  width: 100%;
}
#all {
  min-height: 98vh;
  min-width: 100%;
  margin: 0;
  padding: 0;
}
.login-top {
  position: relative;
}

.fullscreen-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  z-index: 1;
}

/* 登录盒子样式 */
.login-top-box {
  width: 500px;
  position: relative;
  z-index: 100000;
  padding-top: 90px;
  padding-left: 115px;
  color: #11659a;
  font-family: "Roboto", sans-serif;
  font-size: 17px;

}
.login-top-box h2{
  padding-top: 85px;
  font-size: 30px;
  font-weight: bolder;
  color: #3c3c3c;
  padding-bottom: 25px;
}

.error-message {
  color: red;
  margin-bottom: 15px;
}

/* ========== 图标与输入框定位关键样式 ========== */

.input-group {
  position: relative;
  height: 50px;
  margin-bottom: 20px;

  width: 344px;
}

.input-icon {
  position: absolute;
  left: 19px;
  top: 65%;
  transform: translateY(-50%);
  width: 22px;
  pointer-events: none;
}

.reinput-field,
.reinput-field01 {
  width: 340px;
  height: 50px;
  border-radius: 23px;
  margin-top: 10px;
  font-size: 17px;
  color: #3c3c3c;
  background-color: #f0f0f0;
  border: none;
  padding-left: 50px;
}

.code-input-group {
  position: relative; /* 定位上下文 */
}

.get-code-button {
  position: absolute;
  right: 5px; /* 距离输入框右边一点距离 */
  top: 69%;
  transform: translateY(-50%);
  width: 100px;
  height: 48px;
  background: linear-gradient(to right, #055aba, #007bff);
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  z-index: 10;
}

.reinput-field01 {
  padding-right: 100px; /* 留出按钮空间，防止文字被遮挡 */
}

.login-button {
  width: 338px;
  height: 42px;
  padding: 10px;
  background: linear-gradient(to right, #055aba, #007bff);
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 22px;
}
</style> 