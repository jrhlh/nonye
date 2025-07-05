<template>
  <div class="app-container">
    <div class="personnel-pro">
      <!-- 顶部统计区域 -->
      <div class="top-box">
        <div class="top">
          <svg t="1748235916990" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="12494" width="40" height="50">
            <path d="M484 98.2c-100.8 0-182.4 81.7-182.4 182.4C301.6 381.4 383.3 463 484 463c100.8 0 182.4-81.7 182.4-182.4 0.1-100.8-81.6-182.4-182.4-182.4z m0 310.2c-70.6 0-127.8-57.2-127.8-127.8S413.4 152.8 484 152.8 611.8 210 611.8 280.6c0.1 70.6-57.2 127.8-127.8 127.8z" fill="#739FCB" p-id="12495" />
            <path d="M479.6 550.8C269.7 550.8 99.5 719.6 98 928.3H861.3c-1.5-208.7-171.7-377.5-381.7-377.5zM162.5 873.3c27.4-153.2 161.7-269.6 323.4-269.6s296 116.3 323.4 269.6H162.5z" fill="#739FCB" p-id="12496" />
          </svg>
          <h1>人员管理系统</h1>
        </div>
        <div class="divider"></div>
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-header">
              <h2>{{ totalUsers }}</h2>
              <span class="change-percentage">↑ 25%</span>
            </div>
            <p>总人数</p>
          </div>
          <div class="stat-card" v-if="isAdmin">
            <div class="stat-header">
              <h2>{{ adminCount }} / {{ supervisorCount + operatorCount }}</h2>
              <span class="change-percentage01">
                {{ adminCount }} 管理员 {{ supervisorCount }} 主管 {{ operatorCount }} 操作员
              </span>
            </div>
            <p>管理人员</p>
          </div>
          <div class="stat-card" v-if="isAdmin || isSupervisor">
            <div class="stat-header">
              <h2>{{ onDutyCount }} / {{ totalUsers }}</h2>
              <span class="change-percentage01">早晚执勤</span>
            </div>
            <p>值班人数</p>
          </div>
        </div>
      </div>

      <!-- 人员管理和操作日志区域 -->
      <div class="management-and-logs">
        <!-- 人员管理表格 -->
        <div class="personnel-management">
          <div class="management-header">
            <h2>人员管理</h2>
            <div class="management-controls" v-if="isAdmin">
              <select v-model="filterPermission" class="filter-select">
                <option value="all">全部权限</option>
                <option value="Admin">管理员</option>
                <option value="Supervisor">主管</option>
                <option value="Operator">操作员</option>
              </select>
              <button @click="showAddModal = true" class="add-button" v-if="isAdmin">
                + 添加人员
              </button>
            </div>
          </div>

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
            <tr v-for="user in filteredUsers" :key="user.username" :class="{'table-row-hover': isHovered(user.username)}">
              <td>
                <div
                    :class="[
                      'permission-badge',
                      user.permissionLevel === 'Admin' ? 'admin-bg' :
                      user.permissionLevel === 'Supervisor' ? 'supervisor-bg' :
                      user.permissionLevel === 'Operator' ? 'operator-bg' :
                      'bg-gray-100 text-gray-600'
                    ]"
                >
                  {{ translatePermission(user.permissionLevel) }}
                </div>
              </td>
              <td>{{ user.username }}</td>
              <td>{{ user.hire_date || '未设置' }}</td>
              <td>
                <div class="device-container">
                  <svg t="1748246060883" class="icon" style="width: 20px" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="14446" width="20" height="20">
                    <path d="M815.43 40H200.06C91.48 40 3.16 128.33 3.16 236.9v396.37c0 108.57 88.32 196.9 196.9 196.9h268.49v76.27H269.77v78.41h475.96v-78.41H546.96v-76.27h268.47c108.58 0 196.9-88.33 196.9-196.9V236.9c0-108.57-88.32-196.9-196.9-196.9z m118.49 593.27c0 65.33-53.14 118.49-118.49 118.49H200.06c-65.34 0-118.49-53.15-118.49-118.49V236.9c0-65.33 53.14-118.49 118.49-118.49h615.37c65.34 0 118.49 53.15 118.49 118.49v396.37z" fill="#333333" p-id="14447" />
                    <path d="M247.69 286.38h520.12v78.41H247.69zM247.69 505.38h355.86v78.41H247.69z" fill="#C6C6C6" p-id="14448" />
                  </svg>
                  <span>{{ user.linked_devices || 0 }}</span>
                </div>
              </td>
              <td>
                <button
                    @click="editUser(user)"
                    class="edit-button"
                    v-if="canEditUser(user)"
                    :title="canEditUser(user) ? '编辑用户' : '无编辑权限'"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-6.293 3.353 4.293-4.293 1.293 1.293-4.293 4.293-1.293-1.293z" />
                  </svg>
                </button>
                <button
                    @click="deleteUser(user.username)"
                    class="delete-button"
                    v-if="canDeleteUser(user)"
                    :title="canDeleteUser(user) ? '删除用户' : '无删除权限'"
                    @mouseenter="showDeleteConfirm = user.username"
                    @mouseleave="showDeleteConfirm = ''"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3.5 0a.5.5 0 0 1-1 0v6a.5.5 0 0 1 1 0V6Z" />
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z" />
                  </svg>
                  <!-- 删除确认提示 -->
                  <div v-if="showDeleteConfirm === user.username" class="delete-tooltip">
                    确定要删除用户 {{ user.username }} 吗？此操作不可撤销
                  </div>
                </button>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- 操作日志区域 -->
        <div class="operation-logs" v-if="isAdmin || isSupervisor">
          <div class="logs-header">
            <h2>操作日志</h2>
            <div class="log-filters">
              <select v-model="logFilterType" class="filter-select">
                <option value="all">所有类型</option>
                <option value="USER_CREATE">用户创建</option>
                <option value="USER_UPDATE">用户更新</option>
                <option value="USER_DELETE">用户删除</option>
                <option value="DEVICE_MANAGE">设备管理</option>
                <option value="DATA_VIEW">数据查看</option>
                <option value="PERMISSION_CHANGE">权限变更</option>
                <option value="SYSTEM_OPERATION">系统操作</option>
              </select>
            </div>
          </div>
          <ul class="log-list">
            <li v-for="log in filteredLogs" :key="log.id" :class="getLogClass(log.type)">
              <div v-if="isAdmin || log.user === currentUser.username">
                <div class="log-header">
                  <span class="log-type">{{ LOG_TYPES[log.type] || log.type }}</span>
                  <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                </div>
                <div class="log-message">{{ log.message }}</div>
                <div class="log-user">操作人: {{ log.user || '系统' }}</div>
                <div class="log-details" v-if="log.details">{{ log.details }}</div>
              </div>
            </li>
            <li v-if="logs.length === 0 && isLogsLoaded" class="empty-log">
              <div class="empty-message">暂无操作日志记录</div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 添加人员模态框 -->
      <div v-if="showAddModal" class="modal-overlay">
        <div class="modal-content">
          <h3>添加新人员</h3>
          <div class="form-group">
            <label>用户名 <span class="required">*</span></label>
            <input type="text" v-model="newUser.username" placeholder="输入用户名" required>
            <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
          </div>
          <div class="form-group">
            <label>密码 <span class="required">*</span></label>
            <input type="password" v-model="newUser.password" placeholder="输入密码" required>
            <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" v-model="newUser.email" placeholder="输入邮箱">
            <div v-if="emailError" class="error-message">{{ emailError }}</div>
          </div>
          <div class="form-group">
            <label>权限级别 <span class="required">*</span></label>
            <select
                v-model="newUser.permissionLevel"
                @change="formatAndValidatePermission"
            >
              <option value="Admin" v-if="currentUser.username === 'root'">管理员 (Admin)</option>
              <option value="Supervisor">主管 (Supervisor)</option>
              <option value="Operator">操作员 (Operator)</option>
            </select>
            <div v-if="permissionError" class="error-message">{{ permissionError }}</div>
          </div>
          <div class="form-group">
            <label>联系电话</label>
            <input type="tel" v-model="newUser.phone" placeholder="输入联系电话">
            <div v-if="phoneError" class="error-message">{{ phoneError }}</div>
          </div>
          <div class="form-group">
            <label>入职日期 <span class="required">*</span></label>
            <input
                type="date"
                v-model="newUser.hire_date"
                required
                :min="getMinimumDate()"
            >
          </div>
          <div class="form-group">
            <label>关联设备</label>
            <input type="number" v-model="newUser.linked_devices" min="0" max="5">
          </div>
          <div class="modal-actions">
            <button @click="confirmCancel" class="cancel-button">取消</button>
            <button @click="handleAddUser" class="create-button">创建</button>
          </div>
        </div>
      </div>

      <!-- 修改人员模态框 -->
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal-content">
          <h3>修改人员信息</h3>
          <div class="form-group">
            <label>权限级别</label>
            <select
                v-model="editingUser.permissionLevel"
                :disabled="!canEditPermission"
                @change="formatAndValidatePermission"
            >
              <option value="Admin" v-if="currentUser.username === 'root' && editingUser.username !== 'root'">管理员 (Admin)</option>
              <option value="Supervisor" v-if="canEditPermission">主管 (Supervisor)</option>
              <option value="Operator" v-if="canEditPermission">操作员 (Operator)</option>
            </select>
            <div v-if="permissionError" class="error-message">{{ permissionError }}</div>
          </div>
          <div class="form-group">
            <label>用户名</label>
            <input type="text" v-model="editingUser.username" disabled>
          </div>
          <div class="form-group">
            <label>入职日期</label>
            <input type="date" v-model="editingUser.hire_date">
          </div>
          <div class="form-group">
            <label>关联设备</label>
            <input type="number" v-model="editingUser.linked_devices" min="0" max="5">
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" v-model="editingUser.email" placeholder="输入邮箱">
          </div>
          <div class="form-group">
            <label>联系电话</label>
            <input type="tel" v-model="editingUser.phone" placeholder="输入联系电话">
          </div>
          <div class="form-group" v-if="canEditStatus">
            <label>状态</label>
            <select v-model="editingUser.status">
              <option value="Active">活跃</option>
              <option value="Inactive">未活跃</option>
            </select>
          </div>
          <div class="form-group">
            <label>修改密码</label>
            <input type="password" v-model="editingUser.password" placeholder="留空表示不修改密码">
          </div>
          <div class="modal-actions">
            <button @click="showEditModal = false" class="cancel-button">取消</button>
            <button @click="handleEditUser" class="create-button">保存</button>
          </div>
        </div>
      </div>
    </div>
    <div>
      <!-- 你的页面内容 -->
      <askai />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import Askai from "../components1/askai.vue";

// 权限枚举
const PERMISSION_LEVEL = {
  Admin: 'Admin',
  Supervisor: 'Supervisor',
  Operator: 'Operator'
};

// 有效权限数组
const validPermissions = Object.values(PERMISSION_LEVEL);

// 日志类型映射
const LOG_TYPES = {
  'USER_CREATE': '用户创建',
  'USER_UPDATE': '用户更新',
  'USER_DELETE': '用户删除',
  'DEVICE_MANAGE': '设备管理',
  'DATA_VIEW': '数据查看',
  'PERMISSION_CHANGE': '权限变更',
  'SYSTEM_OPERATION': '系统操作'
};

// 日志类型样式映射
const LOG_TYPE_CLASSES = {
  'USER_CREATE': 'log-success',
  'USER_UPDATE': 'log-info',
  'USER_DELETE': 'log-warning',
  'DEVICE_MANAGE': 'log-info',
  'DATA_VIEW': 'log-info',
  'PERMISSION_CHANGE': 'log-warning',
  'SYSTEM_OPERATION': 'log-success'
};

// 从localStorage获取用户信息
const userInfo = JSON.parse(localStorage.getItem('user') || '{}');

// 当前用户
const currentUser = ref({
  username: userInfo.username || '',
  permissionLevel: userInfo.is_admin ? 'Admin' : 'Supervisor' // 根据实际情况调整
});

// 计算属性判断用户角色
const isAdmin = computed(() => currentUser.value.permissionLevel === 'Admin');
const isSupervisor = computed(() => currentUser.value.permissionLevel === 'Supervisor');
const isOperator = computed(() => currentUser.value.permissionLevel === 'Operator');

// 数据状态
const users = ref([]);
const logs = ref([]);
const filterPermission = ref('all');
const logFilterType = ref('all');
const showAddModal = ref(false);
const showEditModal = ref(false);
const newUser = ref({
  username: '',
  password: '',
  permissionLevel: 'Operator',
  email: '',
  phone: '',
  hire_date: new Date().toISOString().split('T')[0],
  linked_devices: 0
});
const editingUser = ref({});
const permissionError = ref('');
const usernameError = ref('');
const passwordError = ref('');
const emailError = ref('');
const phoneError = ref('');
const showDeleteConfirm = ref('');
const isLogsLoaded = ref(false);

// 统一错误处理函数
const handleError = (error, message = '操作失败') => {
  console.error(message, error);
  const errorMessage = error?.response?.data?.message || message;
  alert(errorMessage);
};

// 权限判断方法
const canEditUser = (user) => {
  // 只有管理员可以编辑用户
  if (!isAdmin.value) return false;

  // 禁止修改root用户
  if (user.username === 'root') return false;

  return true;
};

const canDeleteUser = (user) => {
  // 只有管理员可以删除用户
  if (!isAdmin.value) return false;

  // 禁止删除root用户
  if (user.username === 'root') return false;

  return true;
};

// 过滤用户列表
const filteredUsers = computed(() => {
  if (isOperator.value) {
    return users.value.filter(u => u.username === currentUser.value.username);
  }

  if (filterPermission.value === 'all') {
    return users.value;
  }

  return users.value.filter(user => user.permissionLevel === filterPermission.value);
});

// 过滤日志
const filteredLogs = computed(() => {
  if (!isAdmin.value && !isSupervisor.value) return [];

  return logs.value.filter(log =>
      logFilterType.value === 'all' || log.type === logFilterType.value
  );
});

// 统计信息
const totalUsers = computed(() => users.value.length);
const adminCount = computed(() =>
    users.value.filter(u => u.permissionLevel === 'Admin').length
);
const supervisorCount = computed(() =>
    users.value.filter(u => u.permissionLevel === 'Supervisor').length
);
const operatorCount = computed(() =>
    users.value.filter(u => u.permissionLevel === 'Operator').length
);
const onDutyCount = computed(() =>
    users.value.filter(u => u.status === 'Active').length
);

// 权限翻译函数
const translatePermission = (permission) => {
  return {
    'Admin': '管理员',
    'Supervisor': '主管',
    'Operator': '操作员'
  }[permission] || '未知';
};

// 获取日志类型样式类
const getLogClass = (type) => LOG_TYPE_CLASSES[type] || 'log-info';

// 获取最小日期（今天之前）
const getMinimumDate = () => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 格式化并验证权限级别
const formatAndValidatePermission = () => {
  // 强制转换为首字母大写
  newUser.value.permissionLevel = newUser.value.permissionLevel.charAt(0).toUpperCase() +
      newUser.value.permissionLevel.slice(1).toLowerCase();
  editingUser.value.permissionLevel = editingUser.value.permissionLevel.charAt(0).toUpperCase() +
      editingUser.value.permissionLevel.slice(1).toLowerCase();

  // 验证权限级别
  if (
      !validPermissions.includes(newUser.value.permissionLevel) &&
      !validPermissions.includes(editingUser.value.permissionLevel)
  ) {
    permissionError.value = '权限级别必须为Admin、Supervisor或Operator';
    newUser.value.permissionLevel = 'Operator';
    editingUser.value.permissionLevel = 'Operator';
  } else {
    permissionError.value = '';
  }

  // 权限级别为Admin时的额外验证
  if (
      (newUser.value.permissionLevel === 'Admin' && currentUser.value.username !== 'root') ||
      (editingUser.value.permissionLevel === 'Admin' && currentUser.value.username !== 'root')
  ) {
    permissionError.value = '只有root用户可以设置管理员权限';
    newUser.value.permissionLevel = 'Supervisor';
    editingUser.value.permissionLevel = 'Supervisor';
  }
};

// 验证用户名
const validateUsername = (username) => {
  if (!username.trim()) {
    usernameError.value = '用户名不能为空';
    return false;
  }
  if (username.length < 3 || username.length > 20) {
    usernameError.value = '用户名长度需在3-20个字符之间';
    return false;
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    usernameError.value = '用户名只能包含字母、数字和下划线';
    return false;
  }
  usernameError.value = '';
  return true;
};

// 验证密码
const validatePassword = (password) => {
  if (!password) {
    passwordError.value = '密码不能为空';
    return false;
  }
  if (password.length < 6) {
    passwordError.value = '密码长度不能少于6位';
    return false;
  }
  passwordError.value = '';
  return true;
};

// 验证邮箱
const validateEmail = (email) => {
  if (!email) {
    emailError.value = '';
    return true;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    emailError.value = '请输入有效的邮箱地址';
    return false;
  }
  emailError.value = '';
  return true;
};

// 验证电话
const validatePhone = (phone) => {
  if (!phone) {
    phoneError.value = '';
    return true;
  }
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    phoneError.value = '请输入有效的手机号码';
    return false;
  }
  phoneError.value = '';
  return true;
};

onMounted(() => {
  fetchUsers();
  if (isAdmin.value || isSupervisor.value) {
    fetchLogs();
  }
});

// 获取用户数据
const fetchUsers = async () => {
  try {
    const response = await axios.get('http://localhost:5000/personnel/users', {
      headers: {
        Authorization: `Bearer ${userInfo.token}`
      }
    });

    users.value = response.data.data
        .filter(user => user && user.username)
        .map(user => ({
          ...user,
          permissionLevel: validPermissions.includes(user.permission_level)
              ? user.permission_level
              : 'Operator',
          hire_date: user.hire_date || '',
          status: user.status || 'Active',
          linked_devices: user.linked_devices || 0,
          email: user.email || '',
          phone: user.phone || ''
        }));

    // 确保root为管理员
    users.value = users.value.map(user =>
        user.username === 'root' ? { ...user, permissionLevel: 'Admin' } : user
    );
  } catch (error) {
    handleError(error, '获取用户数据失败');
  }
};

// 获取日志数据
const fetchLogs = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/personnel/logs`, {
      headers: {
        Authorization: `Bearer ${userInfo.token}`
      }
    });
    logs.value = response.data.data || [];
    isLogsLoaded.value = true;
  } catch (error) {
    handleError(error, '获取日志数据失败');
    isLogsLoaded.value = true;
  }
};

// 添加用户
const handleAddUser = async () => {
  // 验证必填字段
  if (!validateUsername(newUser.value.username)) return;
  if (!validatePassword(newUser.value.password)) return;
  if (!newUser.value.hire_date) {
    alert('请选择入职日期');
    return;
  }
  if (!validateEmail(newUser.value.email)) return;
  if (!validatePhone(newUser.value.phone)) return;

  // 再次验证权限级别（防止绕过前端验证）
  newUser.value.permissionLevel = newUser.value.permissionLevel.charAt(0).toUpperCase() +
      newUser.value.permissionLevel.slice(1).toLowerCase();
  if (!validPermissions.includes(newUser.value.permissionLevel)) {
    alert('权限级别必须为Admin、Supervisor或Operator');
    newUser.value.permissionLevel = 'Operator';
    return;
  }

  // 权限级别为Admin时的额外验证
  if (newUser.value.permissionLevel === 'Admin' && currentUser.value.username !== 'root') {
    alert('只有root用户可以创建管理员');
    newUser.value.permissionLevel = 'Supervisor';
    return;
  }

  // 检查用户名是否已存在
  if (users.value.some(user => user.username === newUser.value.username)) {
    usernameError.value = '用户名已存在';
    return;
  }

  // 构建请求数据
  const requestData = {
    username: newUser.value.username,
    password: newUser.value.password,
    permissionLevel: newUser.value.permissionLevel,
    hire_date: newUser.value.hire_date,
    email: newUser.value.email,
    phone: newUser.value.phone,
    linked_devices: newUser.value.linked_devices,
    status: 'Active',
    createdBy: currentUser.value.username
  };

  try {
    const response = await axios.post('http://localhost:5000/personnel/users', requestData, {
      headers: {
        Authorization: `Bearer ${userInfo.token}`
      }
    });

    if (response.status === 201) {
      fetchUsers();
      showAddModal.value = false;
      alert('用户创建成功');
      resetNewUser();
    } else {
      handleError(response.data, '创建用户失败');
    }
  } catch (error) {
    handleError(error, '创建用户失败');
  }
};

// 编辑用户
const editUser = (user) => {
  if (!canEditUser(user)) {
    alert('只有管理员可以编辑用户');
    return;
  }

  editingUser.value = {
    username: user.username,
    permissionLevel: user.permissionLevel,
    hire_date: user.hire_date || new Date().toISOString().split('T')[0],
    linked_devices: user.linked_devices || 0,
    status: user.status || 'Active',
    email: user.email || '',
    phone: user.phone || '',
    password: '' // 密码字段留空，不修改密码
  };

  showEditModal.value = true;
};

// 保存编辑
const handleEditUser = async () => {
  if (!editingUser.value.hire_date) {
    alert('请选择入职日期');
    return;
  }

  // 验证邮箱和电话
  if (!validateEmail(editingUser.value.email)) return;
  if (!validatePhone(editingUser.value.phone)) return;

  // 再次验证权限级别（防止绕过前端验证）
  editingUser.value.permissionLevel = editingUser.value.permissionLevel.charAt(0).toUpperCase() +
      editingUser.value.permissionLevel.slice(1).toLowerCase();
  if (!validPermissions.includes(editingUser.value.permissionLevel)) {
    alert('权限级别必须为Admin、Supervisor或Operator');
    editingUser.value.permissionLevel = 'Operator';
    return;
  }

  // 权限级别为Admin时的额外验证
  if (
      editingUser.value.permissionLevel === 'Admin' &&
      currentUser.value.username !== 'root' &&
      editingUser.value.username !== 'root'
  ) {
    alert('只有root用户可以设置管理员权限');
    editingUser.value.permissionLevel = 'Supervisor';
    return;
  }

  const payload = {
    permissionLevel: editingUser.value.permissionLevel,
    hire_date: editingUser.value.hire_date,
    linked_devices: editingUser.value.linked_devices,
    status: editingUser.value.status,
    email: editingUser.value.email,
    phone: editingUser.value.phone
  };

  // 如果有输入密码，则更新密码
  if (editingUser.value.password) {
    payload.password = editingUser.value.password;
  }

  try {
    const response = await axios.put(
        `http://localhost:5000/personnel/users/${editingUser.value.username}`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${userInfo.token}`
          }
        }
    );

    if (response.status === 200) {
      fetchUsers();
      showEditModal.value = false;
      alert('用户信息更新成功');
    } else {
      handleError(response.data, '更新用户失败');
    }
  } catch (error) {
    handleError(error, '更新用户失败');
  }
};

// 删除用户
const deleteUser = async (username) => {
  if (username === 'root') {
    alert('禁止删除root用户');
    return;
  }

  const userToDelete = users.value.find(u => u.username === username);
  if (!userToDelete) {
    alert('未找到该用户');
    return;
  }

  if (!canDeleteUser(userToDelete)) {
    alert('只有管理员可以删除用户');
    return;
  }

  if (!confirm(`确定要删除用户 ${username} 吗？此操作不可撤销。`)) return;

  try {
    const response = await axios.delete(`http://localhost:5000/personnel/users/${username}`, {
      headers: {
        Authorization: `Bearer ${userInfo.token}`
      }
    });

    if (response.status === 200) {
      fetchUsers();
      alert('用户删除成功');
    } else {
      handleError(response.data, '删除用户失败');
    }
  } catch (error) {
    handleError(error, '删除用户失败');
  }
};

// 重置表单
const resetNewUser = () => {
  newUser.value = {
    username: '',
    password: '',
    permissionLevel: 'Operator',
    email: '',
    phone: '',
    hire_date: new Date().toISOString().split('T')[0],
    linked_devices: 0
  };
  usernameError.value = '';
  passwordError.value = '';
  emailError.value = '';
  phoneError.value = '';
  permissionError.value = '';
};

// 取消添加
const confirmCancel = () => {
  showAddModal.value = false;
  resetNewUser();
};

// 行悬停状态
const isHovered = (username) => {
  let hovered = ref(false);
  return hovered.value;
};
</script>

<style scoped>
/* 全局样式 */
.app-container {
  height: 100vh;
  overflow-y: scroll;
  scrollbar-width: none; /* Firefox */
  background-color: #fbfbfb;
}

.app-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge */
}

.personnel-pro {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  color: #333;
  background: #fbfbfb;
}

/* 顶部区域样式 */
.top-box {
  height: 155px;
  background-color: #FFFFFF;

  padding: 20px;
}

.top {
  display: flex;
  position: relative;
  top: -20px;
  height: 10px;
}

.icon01 {
  width: 40px;
  height: 50px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 18px;
  font-size: 23px;
}

.divider {
  height: 1px;
  background: #eaeaea;
  margin: 27px 0;
  margin-bottom: 40px;
}

.stats-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background-color: #FFFFFF;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
  height: 60px;
  position: relative;
  top: -27px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.stat-card h2 {
  margin: 0;
  font-size: 24px;
  color: #2B6CB0;
}

.change-percentage {
  font-size: 14px;
  color: green;
}

.change-percentage01 {
  font-size: 14px;
  color: #7E8390;
}

.stat-card p {
  margin: 5px 0;
  color: #6B7280;
}


/* 管理和日志区域样式 */
.management-and-logs {
  display: flex;
  margin-top: 20px;

}

.personnel-management {
  width: 62%;
  background-color: #FFFFFF;
  padding: 20px;
  margin-left: 20px;
  border-radius: 8px;
  height: 500px;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
}

.operation-logs {
  flex-grow: 1;
  background-color: #FFFFFF;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 290px);
  overflow-y: auto;
  margin-left: 20px;

}

.operation-logs h2 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 18px;
  margin-bottom: 15px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.log-filters {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background-color: #ffffff;
  font-size: 14px;
}

/* 表格样式 */
.personnel-table {
  width: 100%;
  border-collapse: collapse;
}

.personnel-table th,
.personnel-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #eaeaea;
  font-size: 14px;
}

.personnel-table th {
  text-align: left;
  background-color: #f8f9fa;
  font-weight: 500;
  color: #495057;
  position: sticky;
  top: 0;
  z-index: 1;
}

.personnel-table tbody tr {
  transition: background-color 0.2s;
}

.personnel-table tbody tr:hover {
  background-color: #f9f9f9;
}

.table-row-hover {
  background-color: #f0f8ff;
}

.device-container {
  display: flex;
  align-items: center;
  gap: 5px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.management-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.management-controls {
  display: flex;
  gap: 15px;
}

.add-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.add-button:hover {
  background-color: #45a049;
}

.edit-button,
.delete-button {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 2px;
}

.edit-button:hover {
  color: #2196F3;
}

.delete-button:hover {
  color: #F44336;
}

/* 日志样式 */
/* 操作日志区域样式 */
.operation-logs {
  flex-grow: 1;
  background-color: #FFFFFF;
  padding: 20px;
  margin-left: 20px;
  border-radius: 8px;
  margin-right: 20px;
}

.operation-logs h2 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 18px;
}

.log-list {
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
}

/* 时间线样式 */
.log-list::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.log-list li {
  margin-bottom: 15px;
  padding-left: 30px;
  position: relative;
}

/* 日志类型标记点 */
.log-list li::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 5px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #e0e0e0;
  z-index: 1;
}

.log-list li.log-success::before {
  background: #4CAF50;
}

.log-list li.log-warning::before {
  background: #FFC107;
}

.log-list li.log-error::before {
  background: #F44336;
}

.log-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.log-type {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.log-type-success {
  background: #E8F5E9;
  color: #4CAF50;
}

.log-type-warning {
  background: #FFF3E0;
  color: #FF9800;
}

.log-type-error {
  background: #FFEBEE;
  color: #F44336;
}

.log-time {
  color: #7E8390;
  font-size: 12px;
}

.log-message {
  font-weight: 500;
  margin-bottom: 3px;
}

.log-details {
  color: #7E8390;
  font-size: 14px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 18px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #F44336;
  margin-left: 5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button,
.create-button {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
}

.cancel-button {
  background-color: #f5f5f5;
  color: #333;
}

.cancel-button:hover {
  background-color: #e5e5e5;
}

.create-button {
  background-color: #4CAF50;
  color: white;
}

.create-button:hover {
  background-color: #45a049;
}

/* 权限徽章样式 */
.permission-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  min-width: 60px;
  text-align: center;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.admin-bg {
  background-color: #FFE0E0;
  color: #FF4444;
  border-color: #FFCCCC;
}

.supervisor-bg {
  background-color: #E0F0FF;
  color: #2176FF;
  border-color: #B3D4FF;
}

.operator-bg {
  background-color: #E0FFE5;
  color: #00C851;
  border-color: #B3FFC6;
}

.bg-gray-100 {
  background-color: #F5F5F5;
  color: #616161;
  border-color: #D0D0D0;
}

.error-message {
  font-size: 12px;
  margin-top: 5px;
  color: #F44336;
}

/* 删除提示样式 */
.delete-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 10;
}
</style>