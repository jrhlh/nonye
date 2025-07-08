<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios, { type AxiosError } from 'axios';

const router = useRouter();
const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const errorMessage = ref('');

// 跳转到注册页面
const register = () => {
  router.push('/register');
};

// 登录功能
const login = async () => {
  try {
    const response = await axios.post('http://localhost:5000/auth/login', {
      username: username.value,
      password: password.value
    }, {
      withCredentials: true // 发送跨域请求时携带cookie
    });

    if (response.data.success) {
      const { username: userUsername, is_admin } = response.data;

      localStorage.setItem('user', JSON.stringify({
        username: userUsername,
        is_admin,
        token: response.data.token
      }));

      router.push('/dashboard');
    }
  } catch (error) {
    const axiosError = error as AxiosError;
    if (axiosError.response) {
      errorMessage.value = (axiosError.response.data as { message?: string })?.message || '登录失败';
    } else {
      errorMessage.value = '无法连接到服务器';
    }
  }
};
</script>

<template>
  <div id="all">
    <div class="login-top">
      <img src="../assets/oo.png" alt="" class="fullscreen-bg">
      <div class="scroll-container">
        <div class="login-top-box">
          <h1>禾境智联后台管理系统</h1>
          <h2>登录</h2>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <!-- 用户名输入 -->
          <div class="input-group">
            <img src="../assets/人像.png" alt="" class="input-icon">
            <input v-model="username" type="text" placeholder="请输入账号" class="input-field">
          </div>
          <!-- 密码输入 -->
          <div class="input-group">
            <img src="../assets/suo.png" alt="" class="input-icon">
            <input v-model="password" type="password" placeholder="请输入密码" class="input-field">
          </div>
          <button @click="login" class="login-button">登录</button>
          <p class="login-p" style="padding-left:5px" @click.prevent="register">没有帐户？去注册</p>
          <p class="login-p1" style="padding-left:5px">
            <input type="checkbox" v-model="rememberMe" id="remember">
            <label for="remember">记住密码</label>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全局重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#all {
  min-height: 98vh;
  min-width: 100%;
  margin: 0;
  padding: 0;
}

.scroll-container {
  overflow: hidden;
  height: 80vh;
  width: 100%;
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

.login-top-box {
  width: 500px;
  position: relative;
  z-index: 1000;
  padding-top: 90px;
  padding-left: 115px;
  color: #11659a;
  font-family: "Roboto", sans-serif;
  font-size: 17px;
}

.login-top-box h2 {
  padding-top: 85px;
  font-size: 30px;
  font-weight: bolder;
  color: #3c3c3c;
  padding-bottom: 25px;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-bottom: 10px;
}

/* ========== 图标与输入框定位关键样式 ========== */

.input-group {
  position: relative;
  height: 50px; /* 与 input 高度一致 */
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 17px;
  top: 50%;
  transform: translateY(-50%);
  width: 21px;
  pointer-events: none;
}

.input-field {
  width: 340px;
  padding-left: 50px;
  height: 50px;
  border-radius: 23px;
  background-color: #f0f0f0;
  border: none;
  font-size: 17px;
  color: #3c3c3c;

}

.login-button {
  width: 125px;
  height: 40px;
  padding: 10px;
  background: linear-gradient(to right, #055aba, #007bff);
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  margin-top: 7px;
  font-size: 14px;
}

.login-p {
  font-size: 17px;
  padding-top: 40px;
}

.login-p1 {
  position: relative;
  top: -94px;
  left: 244px;
  color: black;
}
</style>