<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ modalTitle }}</h3>
        <button class="modal-close" @click="handleClose">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label>用户名 <span class="required">*</span></label>
          <input 
            type="text" 
            v-model="formData.username" 
            placeholder="输入用户名" 
            required
            :disabled="mode === 'edit'"
          >
          <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
        </div>
        
        <div class="form-group" v-if="mode === 'add'">
          <label>密码 <span class="required">*</span></label>
          <input 
            type="password" 
            v-model="formData.password" 
            placeholder="输入密码" 
            required
          >
          <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
        </div>
        
        <div class="form-group">
          <label>邮箱</label>
          <input 
            type="email" 
            v-model="formData.email" 
            placeholder="输入邮箱"
          >
          <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
        </div>
        
        <div class="form-group">
          <label>权限级别 <span class="required">*</span></label>
          <select v-model="formData.permissionLevel">
            <option value="Admin" v-if="canCreateAdmin">管理员 (Admin)</option>
            <option value="Supervisor">主管 (Supervisor)</option>
            <option value="Operator">操作员 (Operator)</option>
          </select>
          <div v-if="errors.permissionLevel" class="error-message">{{ errors.permissionLevel }}</div>
        </div>
        
        <div class="form-group">
          <label>联系电话</label>
          <input 
            type="tel" 
            v-model="formData.phone" 
            placeholder="输入联系电话"
          >
          <div v-if="errors.phone" class="error-message">{{ errors.phone }}</div>
        </div>
        
        <div class="form-group">
          <label>入职日期</label>
          <input 
            type="date" 
            v-model="formData.hire_date"
          >
        </div>
        
        <div class="form-actions">
          <BaseButton 
            type="button" 
            variant="secondary" 
            @click="handleClose"
          >
            取消
          </BaseButton>
          <BaseButton 
            type="submit" 
            variant="primary"
            :loading="isSubmitting"
          >
            {{ mode === 'add' ? '添加' : '更新' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import BaseButton from '../../ui/BaseButton.vue';

interface User {
  username: string;
  permissionLevel: 'Admin' | 'Supervisor' | 'Operator';
  password?: string;
  email?: string;
  phone?: string;
  hire_date?: string;
}

interface Props {
  visible: boolean;
  mode: 'add' | 'edit';
  userData?: User | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  submit: [user: User];
}>();

// 响应式数据
const isSubmitting = ref(false);
const formData = ref<User>({
  username: '',
  permissionLevel: 'Operator',
  password: '',
  email: '',
  phone: '',
  hire_date: ''
});

const errors = ref<Partial<Record<keyof User, string>>>({});

// 计算属性
const modalTitle = computed(() => {
  return props.mode === 'add' ? '添加新人员' : '编辑人员信息';
});

const canCreateAdmin = computed(() => {
  // 这里可以根据当前用户权限判断是否可以创建管理员
  return true;
});

// 方法
const validateForm = (): boolean => {
  errors.value = {};
  
  if (!formData.value.username.trim()) {
    errors.value.username = '用户名不能为空';
  }
  
  if (props.mode === 'add' && !formData.value.password) {
    errors.value.password = '密码不能为空';
  }
  
  if (formData.value.email && !isValidEmail(formData.value.email)) {
    errors.value.email = '请输入有效的邮箱地址';
  }
  
  if (formData.value.phone && !isValidPhone(formData.value.phone)) {
    errors.value.phone = '请输入有效的电话号码';
  }
  
  return Object.keys(errors.value).length === 0;
};

const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    emit('submit', { ...formData.value });
  } catch (error) {
    console.error('提交失败:', error);
  } finally {
    isSubmitting.value = false;
  }
};

const handleClose = () => {
  emit('close');
};

const resetForm = () => {
  formData.value = {
    username: '',
    permissionLevel: 'Operator',
    password: '',
    email: '',
    phone: '',
    hire_date: ''
  };
  errors.value = {};
};

// 监听用户数据变化
watch(() => props.userData, (newUserData) => {
  if (newUserData && props.mode === 'edit') {
    formData.value = { ...newUserData };
  } else {
    resetForm();
  }
}, { immediate: true });

// 监听模态框显示状态
watch(() => props.visible, (visible) => {
  if (!visible) {
    resetForm();
  }
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #666;
}

.modal-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #262626;
}

.required {
  color: #ff4d4f;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-group input:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-form {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style> 