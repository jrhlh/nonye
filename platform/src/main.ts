// main.js
import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';
import router from './router'; // 引入配置好的路由
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import './style.css';

const app = createApp(App);

app.use(createPinia()); // 安装 Pinia
app.use(router); // 安装 Vue Router
app.use(ElementPlus); // 安装 Element Plus (如果有的话)

app.mount('#app');