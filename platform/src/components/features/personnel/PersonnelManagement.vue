<template>
  <div class="personnel-management">
    <BaseCard title="人员管理" class="management-card">
      <template #actions>
        <div class="management-controls" v-if="isAdmin">
          <select v-model="filterPermission" class="filter-select">
            <option value="all">全部权限</option>
            <option value="Admin">管理员</option>
            <option value="Supervisor">主管</option>
            <option value="Operator">操作员</option>
          </select>
          <BaseButton
            variant="primary"
            size="small"
            @click="showAddModal = true"
          >
            + 添加人员
          </BaseButton>
        </div>
      </template>

      <div class="table-container">
        <table class="personnel-table">
          <thead>
            <tr>
              <th>权限级别</th>
              <th>用户名</th>
              <th>入职日期</th>
              <th>关联设备</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.username"
              :class="{'table-row-hover': isHovered(user.username)}"
            >
              <td>
                <PermissionBadge :level="user.permissionLevel" />
              </td>
              <td>{{ user.username }}</td>
              <td>{{ user.hire_date || '未设置' }}</td>
              <td>
                <DeviceCount :count="user.linked_devices || 0" />
              </td>
              <td>
                <div class="action-buttons">
                  <BaseButton
                    variant="secondary"
                    size="small"
                    @click="editUser(user)"
                    v-if="canEditUser(user)"
                    :title="canEditUser(user) ? '编辑用户' : '无编辑权限'"
                  >
                    <template #icon>
                      <EditIcon />
                    </template>
                  </BaseButton>
                  <BaseButton
                    variant="danger"
                    size="small"
                    @click="deleteUser(user.username)"
                    v-if="canDeleteUser(user)"
                    :title="canDeleteUser(user) ? '删除用户' : '无删除权限'"
                    @mouseenter="showDeleteConfirm = user.username"
                    @mouseleave="showDeleteConfirm = ''"
                  >
                    <template #icon>
                      <DeleteIcon />
                    </template>
                  </BaseButton>
                </div>
                <!-- 删除确认提示 -->
                <div v-if="showDeleteConfirm === user.username" class="delete-tooltip">
                  确定要删除用户 {{ user.username }} 吗？此操作不可撤销
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- 添加人员模态框 -->
    <PersonnelModal
      v-if="showAddModal"
      :visible="showAddModal"
      :mode="modalMode"
      :user-data="editingUser"
      @close="closeModal"
      @submit="handleUserSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import BaseCard from '../../ui/BaseCard.vue';
import BaseButton from '../../ui/BaseButton.vue';
import PermissionBadge from './PermissionBadge.vue';
import DeviceCount from './DeviceCount.vue';
import PersonnelModal from './PersonnelModal.vue';
import EditIcon from '../../ui/icons/EditIcon.vue';
import DeleteIcon from '../../ui/icons/DeleteIcon.vue';

interface User {
  username: string;
  permissionLevel: 'Admin' | 'Supervisor' | 'Operator';
  hire_date?: string;
  linked_devices?: number;
  email?: string;
  phone?: string;
}

interface Props {
  currentUser: {
    username: string;
    permissionLevel: string;
  };
}

const props = defineProps<Props>();

const emit = defineEmits<{
  userCreated: [user: User];
  userUpdated: [user: User];
  userDeleted: [username: string];
}>();

// 响应式数据
const filterPermission = ref('all');
const showAddModal = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const editingUser = ref<User | null>(null);
const showDeleteConfirm = ref('');

// 模拟用户数据
const users = ref<User[]>([
  {
    username: 'admin001',
    permissionLevel: 'Admin',
    hire_date: '2024-01-15',
    linked_devices: 5
  },
  {
    username: 'supervisor001',
    permissionLevel: 'Supervisor',
    hire_date: '2024-02-20',
    linked_devices: 3
  },
  {
    username: 'operator001',
    permissionLevel: 'Operator',
    hire_date: '2024-03-10',
    linked_devices: 2
  }
]);

// 计算属性
const isAdmin = computed(() => {
  return props.currentUser.permissionLevel === 'Admin' || props.currentUser.username === 'root';
});

const isSupervisor = computed(() => {
  return props.currentUser.permissionLevel === 'Supervisor';
});

const filteredUsers = computed(() => {
  if (filterPermission.value === 'all') {
    return users.value;
  }
  return users.value.filter(user => user.permissionLevel === filterPermission.value);
});

// 方法
const canEditUser = (user: User) => {
  if (isAdmin.value) return true;
  if (isSupervisor.value && user.permissionLevel === 'Operator') return true;
  return false;
};

const canDeleteUser = (user: User) => {
  if (!isAdmin.value) return false;
  if (user.username === props.currentUser.username) return false;
  return true;
};

const isHovered = (username: string) => {
  return showDeleteConfirm.value === username;
};

const editUser = (user: User) => {
  editingUser.value = { ...user };
  modalMode.value = 'edit';
  showAddModal.value = true;
};

const deleteUser = (username: string) => {
  if (confirm(`确定要删除用户 ${username} 吗？此操作不可撤销。`)) {
    users.value = users.value.filter(user => user.username !== username);
    emit('userDeleted', username);
  }
};

const closeModal = () => {
  showAddModal.value = false;
  editingUser.value = null;
  modalMode.value = 'add';
};

const handleUserSubmit = (userData: User) => {
  if (modalMode.value === 'add') {
    users.value.push(userData);
    emit('userCreated', userData);
  } else {
    const index = users.value.findIndex(u => u.username === userData.username);
    if (index !== -1) {
      users.value[index] = userData;
      emit('userUpdated', userData);
    }
  }
  closeModal();
};
</script>

<style scoped>
.personnel-management {
  width: 100%;
}

.management-card {
  margin-bottom: 24px;
}

.management-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.table-container {
  overflow-x: auto;

}

.personnel-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;

}

.personnel-table th,
.personnel-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.personnel-table th {
  background: #fafafa;
  font-weight: 600;
  color: #262626;
}

.personnel-table tbody tr:hover {
  background: #f5f5f5;
}

.table-row-hover {
  background: #f5f5f5;
}

.action-buttons {
  display: flex;
  gap: 8px;
  position: relative;
}

.delete-tooltip {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: #262626;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
}

.delete-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #262626;
}

@media (max-width: 768px) {
  .management-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .personnel-table {
    font-size: 12px;
  }

  .personnel-table th,
  .personnel-table td {
    padding: 8px 12px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
}
</style>