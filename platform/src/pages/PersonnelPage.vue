<template>
  <div class="personnel-page">

    <PersonnelManagement 
      :current-user="currentUser"
      @user-created="handleUserCreated"
      @user-updated="handleUserUpdated"
      @user-deleted="handleUserDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseButton from '../components/ui/BaseButton.vue';
import PersonnelManagement from '../components/features/personnel/PersonnelManagement.vue';

const showAddModal = ref(false);

const currentUser = {
  username: 'admin001',
  permissionLevel: 'Admin'
};

const handleUserCreated = (user: any) => {
  console.log('用户创建:', user);
};

const handleUserUpdated = (user: any) => {
  console.log('用户更新:', user);
};

const handleUserDeleted = (username: string) => {
  console.log('用户删除:', username);
};
</script>

<style scoped>
.personnel-page {
  padding: 24px;
  background: #f5f7fa;
}

@media (max-width: 768px) {
  .personnel-page {
    padding: 16px;
  }
}
</style> 