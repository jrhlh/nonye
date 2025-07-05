<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import a1 from '../assets/a1.jpg';
import a2 from '../assets/a2.jpg';
import a3 from '../assets/a3.jpg';
import a4 from '../assets/a4.jpg';
import a5 from '../assets/a5.jpg';

const avatars = [a1, a2, a3, a4, a5];
const router = useRouter();
const username = ref('');
const avatar = ref('');

onMounted(() => {
  const storedUsername = localStorage.getItem('username');
  const storedAvatar = localStorage.getItem('avatar');

  if (storedUsername) {
    username.value = storedUsername;
    // 如果 localStorage 中没有存储的头像，则随机选择一个
    avatar.value = storedAvatar || avatars[Math.floor(Math.random() * avatars.length)];
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <img :src="avatar" class="user-avatar"  alt=""/>
</template>

<style scoped>
.user-avatar {
  width: 50px; /* 根据需要调整头像大小 */
  height: 50px;
  border-radius: 50%; /* 圆形头像 */
  object-fit: cover; /* 确保图片比例正确 */
}
</style>