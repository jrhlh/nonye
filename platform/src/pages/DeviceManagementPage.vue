<template>
  <div class="device-status">
    <h2 :style="{paddingBottom:'10px',fontSize:'25px'}">设备状态</h2>

    <div class="actions">
      <div class="action-buttons">
        <el-button
            type="primary"
            icon="el-icon-plus"
            @click="showAddModal = true"
            class="button-top01"
        >
          <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4111" width="20" height="20">
            <path d="M533.333333 490.666667V128h-42.666666v362.666667H128v42.666666h362.666667v362.666667h42.666666V533.333333h362.666667v-42.666666z" fill="#ffffff" p-id="4112"></path>
          </svg>
          新建设备
        </el-button>
        <el-button
            type="warning"
            icon="el-icon-download"
            @click="downloadDeviceList"
            class="button-top02"
        >
          <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3054" width="20" height="20">
            <path d="M853.333333 853.333333a42.666667 42.666667 0 0 1 0 85.333334H170.666667a42.666667 42.666667 0 0 1 0-85.333334h682.666666h-0.000001zM512 85.504a42.666667 42.666667 0 0 1 42.666667 42.666667v515.370666l204.373333-204.373333a42.666667 42.666667 0 0 1 63.914667 56.277333l-3.584 4.010667-277.376 277.546666a42.666667 42.666667 0 0 1-56.32 3.584l-4.010667-3.541334-277.12-276.650666a42.666667 42.666667 0 0 1 56.234667-63.957334l4.010666 3.541334L469.333333 644.096V128.170667a42.666667 42.666667 0 0 1 42.666667-42.666667z" fill="#ffffff" p-id="3055"></path>
          </svg>
          下载
        </el-button>
      </div>
    </div>

    <el-table
        :data="filteredDevices"
        style="width: 100%"
        class="device-table"
        v-loading="isLoading"
        element-loading-text="加载中..."
    >
      <el-table-column prop="status" label="状态" sortable>
        <template #default="scope">
          <el-tag :type="getTagType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="deviceName" label="设备名称" sortable></el-table-column>
      <el-table-column prop="deviceCode" label="设备ID" sortable></el-table-column>
      <el-table-column prop="operator" label="操作人员" sortable></el-table-column>
      <el-table-column prop="temperature" label="温度" sortable>
        <template #default="scope">
          <span>{{ scope.row.temperature || '-' }}°C</span>
        </template>
      </el-table-column>
      <el-table-column prop="humidity" label="湿度" sortable>
        <template #default="scope">
          <span>{{ scope.row.humidity || '-' }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="phValue" label="pH值" sortable>
        <template #default="scope">
          <span>{{ scope.row.phValue || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" sortable>
        <template #default="scope">
          <el-button
              size="mini"
              @click="openEditModal(scope.row)"
          >
            编辑
          </el-button>
          <el-button
              size="mini"
              type="danger"
              @click="handleDelete(scope.row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加设备模态框 -->
    <el-dialog
        v-model="showAddModal"
        title="添加新设备"
        :close-on-click-modal="false"
        :before-close="handleClose"
    >
      <el-form
          :model="newDevice"
          :rules="addFormRules"
          ref="addForm"
          label-width="80px"
      >
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="newDevice.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="设备ID" prop="id">
          <el-input v-model="newDevice.id" placeholder="请输入设备ID"></el-input>
        </el-form-item>
        <el-form-item label="操作人员" prop="operator">
          <el-input v-model="newDevice.operator" placeholder="请输入操作人员"></el-input>
        </el-form-item>
        <el-form-item label="设备状态" prop="status">
          <el-select v-model="newDevice.status" placeholder="请选择设备状态">
            <el-option label="在线" value="Normal"></el-option>
            <el-option label="离线" value="Offline"></el-option>
            <el-option label="故障" value="Faulty"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="温度 (°C)" prop="temperature">
          <el-input
              v-model.number="newDevice.temperature"
              type="number"
              placeholder="请输入温度（27-34）"
              :min="27"
              :max="34"
              step="0.1"
          ></el-input>
        </el-form-item>
        <el-form-item label="湿度 (%)" prop="humidity">
          <el-input
              v-model.number="newDevice.humidity"
              type="number"
              placeholder="请输入湿度（60-75）"
              :min="60"
              :max="75"
              step="1"
          ></el-input>
        </el-form-item>
        <el-form-item label="pH值" prop="phValue">
          <el-input
              v-model.number="newDevice.phValue"
              type="number"
              placeholder="请输入pH值（6.3-7.3）"
              :min="6.3"
              :max="7.3"
              step="0.1"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddModal = false">取消</el-button>
        <el-button type="primary" @click="handleAddDevice">确认</el-button>
      </template>
    </el-dialog>

    <!-- 编辑设备模态框 -->
    <el-dialog
        v-model="showEditModal"
        title="编辑设备"
        :close-on-click-modal="false"
        :before-close="handleClose"
    >
      <el-form
          :model="editingDevice"
          :rules="editFormRules"
          ref="editForm"
          label-width="80px"
      >
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="editingDevice.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="设备ID" prop="id">
          <el-input v-model="editingDevice.id" disabled placeholder="设备ID不可修改"></el-input>
        </el-form-item>
        <el-form-item label="操作人员" prop="operator">
          <el-input v-model="editingDevice.operator" placeholder="请输入操作人员"></el-input>
        </el-form-item>
        <el-form-item label="设备状态" prop="status">
          <el-select v-model="editingDevice.status" placeholder="请选择设备状态">
            <el-option label="在线" value="Normal"></el-option>
            <el-option label="离线" value="Offline"></el-option>
            <el-option label="故障" value="Faulty"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="温度 (°C)" prop="temperature">
          <el-input
              v-model.number="editingDevice.temperature"
              type="number"
              placeholder="请输入温度（27-34）"
              :min="27"
              :max="34"
              step="0.1"
          ></el-input>
        </el-form-item>
        <el-form-item label="湿度 (%)" prop="humidity">
          <el-input
              v-model.number="editingDevice.humidity"
              type="number"
              placeholder="请输入湿度（60-75）"
              :min="60"
              :max="75"
              step="1"
          ></el-input>
        </el-form-item>
        <el-form-item label="pH值" prop="phValue">
          <el-input
              v-model.number="editingDevice.phValue"
              type="number"
              placeholder="请输入pH值（6.3-7.3）"
              :min="6.3"
              :max="7.3"
              step="0.1"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="handleEditDevice">保存</el-button>
      </template>
    </el-dialog>

    <!-- 故障详情模态框 -->
    <el-dialog
        v-model="showFaultModal"
        title="故障信息"
        :close-on-click-modal="false"
    >
      <div>设备ID: {{ selectedDevice?.id }}</div>
      <div>设备名称: {{ selectedDevice?.deviceName }}</div>
      <div>故障描述: {{ selectedDevice?.faultDescription || '暂无描述' }}</div>
      <template #footer>
        <el-button @click="showFaultModal = false">关闭</el-button>
        <el-button type="primary" @click="handleFault">处理</el-button>
      </template>
    </el-dialog>

    <div class="pagination">
      <el-pagination
          @size-change="handlePageSizeChange"
          @current-change="handleCurrentPageChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalDevices"
      ></el-pagination>
    </div>

    <div>
      <askai />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';
import Askai from "../components1/askai.vue";

// 配置后端基础URL
axios.defaults.baseURL = 'http://localhost:5000';

// 状态管理
const isLoading = ref(false);
const devices = ref([]);
const totalDevices = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const showAddModal = ref(false);
const showEditModal = ref(false);
const showFaultModal = ref(false);

// 新增设备数据（所有参数设置默认值在范围内）
const newDevice = ref({
  id: '',
  name: '',
  operator: '',
  status: 'Normal',
  // 生成 27 到 34 之间的随机温度值（保留一位小数）
  temperature: (27 + Math.random() * 7).toFixed(1),
  // 生成 60 到 75 之间的随机湿度值（整数）
  humidity: Math.floor(60 + Math.random() * 16),
  // 生成 6.3 到 7.3 之间的随机 pH 值（保留一位小数）
  phValue: (6.3 + Math.random() * 1).toFixed(1)
});

const editingDevice = ref(null);
const selectedDevice = ref(null);

// 表单验证规则（新增pH值范围校验）
const addFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  id: [{ required: true, message: '请输入设备ID', trigger: 'blur' }],
  temperature: [
    { required: true, message: '请输入温度', trigger: 'blur' },
    { type: 'number', min: 27, max: 34, message: '温度必须在27-34℃之间', trigger: 'blur' }
  ],
  humidity: [
    { required: true, message: '请输入湿度', trigger: 'blur' },
    { type: 'number', min: 60, max: 75, message: '湿度必须在60-75%之间', trigger: 'blur' }
  ],
  phValue: [
    { required: true, message: '请输入pH值', trigger: 'blur' },
    { type: 'number', min: 6.3, max: 7.3, message: 'pH值必须在6.3-7.3之间', trigger: 'blur' }
  ]
};

const editFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择设备状态', trigger: 'change' }],
  temperature: [
    { required: true, message: '请输入温度', trigger: 'blur' },
    { type: 'number', min: 27, max: 34, message: '温度必须在27-34℃之间', trigger: 'blur' }
  ],
  humidity: [
    { required: true, message: '请输入湿度', trigger: 'blur' },
    { type: 'number', min: 60, max: 75, message: '湿度必须在60-75%之间', trigger: 'blur' }
  ],
  phValue: [
    { required: true, message: '请输入pH值', trigger: 'blur' },
    { type: 'number', min: 6.3, max: 7.3, message: 'pH值必须在6.3-7.3之间', trigger: 'blur' }
  ]
};

// 获取设备列表
const fetchDevices = async (page = 1, size = 10) => {
  isLoading.value = true;
  try {
    const response = await axios.get('/api/device/list', { params: { page, size } });
    if (response.data.success) {
      // 强制生成随机值，忽略后端返回的温湿度和pH值
      const filtered = response.data.data.map(device => ({
        ...device, // 保留设备ID、名称、状态等其他后端返回的字段
        // 温度：27-34℃，保留1位小数（强制随机）
        temperature: Number((27 + Math.random() * 7).toFixed(1)),
        // 湿度：60-75%，整数（强制随机）
        humidity: Math.floor(60 + Math.random() * 16),
        // pH值：6.3-7.3，保留1位小数（强制随机）
        phValue: Number((6.3 + Math.random() * 1).toFixed(1))
      }));
      devices.value = [...filtered]; // 强制更新表格数据
      totalDevices.value = response.data.total;
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    ElMessage.error('获取设备列表失败，请检查后端服务');
    console.error('获取数据失败：', error);
  } finally {
    isLoading.value = false;
  }
};

// 新增设备
const handleAddDevice = async () => {
  // 手动校验所有参数范围
  if (newDevice.value.temperature < 27 || newDevice.value.temperature > 34) {
    ElMessage.error('温度必须在27-34℃之间');
    return;
  }
  if (newDevice.value.humidity < 60 || newDevice.value.humidity > 75) {
    ElMessage.error('湿度必须在60-75%之间');
    return;
  }
  if (newDevice.value.phValue < 6.3 || newDevice.value.phValue > 7.3) {
    ElMessage.error('pH值必须在6.3-7.3之间');
    return;
  }

  try {
    const response = await axios.post('/api/device', {
      ...newDevice.value,
      deviceName: newDevice.value.name,
      deviceCode: newDevice.value.id
    });
    if (response.data.success) {
      ElMessage.success('设备新增成功');
      showAddModal.value = false;
      fetchDevices();
      resetNewDevice();
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    ElMessage.error('设备新增失败');
    console.error(error);
  }
};

// 编辑设备
const handleEditDevice = async () => {
  // 手动校验参数范围（保持不变）
  if (editingDevice.value.temperature < 27 || editingDevice.value.temperature > 34) {
    ElMessage.error('温度必须在27-34℃之间');
    return;
  }
  if (editingDevice.value.humidity < 60 || editingDevice.value.humidity > 75) {
    ElMessage.error('湿度必须在60-75%之间');
    return;
  }
  if (editingDevice.value.phValue < 6.3 || editingDevice.value.phValue > 7.3) {
    ElMessage.error('pH值必须在6.3-7.3之间');
    return;
  }

  try {
    // 关键修复：确保提交的字段与后端预期一致（与设备列表字段对应）
    const response = await axios.put(`/api/device/${editingDevice.value.id}`, {
      deviceName: editingDevice.value.name, // 对应表格中的设备名称
      deviceCode: editingDevice.value.id,   // 对应表格中的设备ID（不可修改，保持原值）
      operator: editingDevice.value.operator,
      status: editingDevice.value.status,
      temperature: editingDevice.value.temperature, // 温度字段
      humidity: editingDevice.value.humidity,       // 湿度字段
      phValue: editingDevice.value.phValue          // pH值字段
    });

    if (response.data.success) {
      ElMessage.success('设备编辑成功');
      showEditModal.value = false;
      // 强制重新获取数据，确保表格更新
      fetchDevices(currentPage.value, pageSize.value);
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    ElMessage.error('设备编辑失败');
    console.error('编辑提交失败：', error); // 增加错误日志
  }
};

// 打开编辑模态框（确保所有参数在范围内）
const openEditModal = (device) => {
  // 强制将所有参数限制在范围内
  const temp = Math.min(Math.max(device.temperature || 27, 27), 34);
  const humi = Math.min(Math.max(device.humidity || 60, 60), 75);
  const ph = Math.min(Math.max(device.phValue || 6.3, 6.3), 7.3);

  editingDevice.value = {
    ...device,
    name: device.deviceName,
    temperature: temp,
    humidity: humi,
    phValue: ph
  };
  showEditModal.value = true;
};

// 删除设备
const handleDelete = async (id) => {
  await ElMessageBox.confirm('确认删除该设备？', '警告', { type: 'warning' })
      .then(async () => {
        try {
          const response = await axios.delete(`/api/device/${id}`);
          if (response.data.success) {
            ElMessage.success('设备删除成功');
            fetchDevices();
          } else {
            ElMessage.error(response.data.message);
          }
        } catch (error) {
          ElMessage.error('删除失败');
          console.error(error);
        }
      });
};

// 处理故障
const handleFault = () => {
  ElMessage.success('故障已处理');
  showFaultModal.value = false;
};

// 重置新增表单
const resetNewDevice = () => {
  newDevice.value = {
    id: '',
    name: '',
    operator: '',
    status: 'Normal',
    temperature: 27,
    humidity: 60,
    phValue: 6.3
  };
};

// 分页处理
const handlePageSizeChange = (size) => {
  pageSize.value = size;
  fetchDevices(1, size);
};

const handleCurrentPageChange = (page) => {
  currentPage.value = page;
  fetchDevices(page, pageSize.value);
};

// 获取标签类型
const getTagType = (status) => {
  switch (status) {
    case 'Normal': return 'success';
    case 'Offline': return 'info';
    case 'Faulty': return 'danger';
    default: return '';
  }
};

// 状态英文转中文
const getStatusText = (status) => {
  switch (status) {
    case 'Normal': return '在线';
    case 'Offline': return '离线';
    case 'Faulty': return '故障';
    default: return status;
  }
};

// 关闭模态框
const handleClose = () => {
  const addForm = document.querySelector('[ref="addForm"]');
  const editForm = document.querySelector('[ref="editForm"]');
  if (addForm) addForm.resetFields?.();
  if (editForm) editForm.resetFields?.();
};

// 下载设备列表
const downloadDeviceList = () => {
  if (devices.value.length === 0) {
    ElMessage.info('没有数据可导出');
    return;
  }

  const headers = ['设备ID', '设备名称', '状态', '操作人员', '温度(°C)', '湿度(%)', 'pH值'];
  const csvContent = [
    headers.join(','),
    ...devices.value.map(device => [
      device.id,
      device.deviceName,
      getStatusText(device.status),
      device.operator,
      device.temperature || '',
      device.humidity || '',
      device.phValue || ''
    ].join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `设备列表_${new Date().toLocaleDateString()}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 生命周期钩子
onMounted(() => {
  fetchDevices();
});

// 计算过滤后的数据
const filteredDevices = computed(() => devices.value);
</script>

<style scoped>
/* 样式部分保持不变 */
.device-status {
  padding: 20px;
  background-color: #F5F7FA;
  padding-left: 28px;
  padding-right: 30px;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-right: 20px;
}

.device-table {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.modal-content {
  width: 400px;
  max-width: 90%;
}

.el-table__header {
  background-color: #fbfbfb;
}

.icon {
  margin-right: 5px;
}

.button-top01{
  white-space: nowrap;
  padding-top: 8px;
  padding-left:  10px;
  width:  110px;
}
.button-top02 {
  white-space: nowrap;
  padding-top: 8px;
  padding-left:  10px;
  width:  90px;
}
:deep(.el-tag) {
  border: none !important;
  color: white !important;
}

:deep(.el-tag--success) {
  background-color: #4CAF50 !important;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.25);
}

:deep(.el-tag--info) {
  background-color: #90A4AE !important;
  box-shadow: 0 2px 4px rgba(144, 164, 174, 0.25);
}

:deep(.el-tag--danger) {
  background-color: #FF7043 !important;
  box-shadow: 0 2px 4px rgba(255, 112, 67, 0.25);
  animation: pulse-danger 2s infinite;
}

@keyframes pulse-danger {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

:deep(.el-tag) {
  border: none !important;
  color: white !important;
  font-weight: 500 !important;
  padding: 0 12px !important;
  height: 28px !important;
  line-height: 28px !important;
  border-radius: 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  transition: all 0.3s ease !important;
}
</style>
<style scoped>
/* 样式部分保持不变 */
.device-status {
  padding: 20px;
  background-color: #F5F7FA;
  padding-left: 28px;
  padding-right: 30px;
}

.actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-right: 20px;
}

.device-table {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.modal-content {
  width: 400px;
  max-width: 90%;
}

.el-table__header {
  background-color: #fbfbfb;
}

.icon {
  margin-right: 5px;
}

.button-top01{
  white-space: nowrap;
  padding-top: 8px;
  padding-left:  10px;
  width:  110px;
}
.button-top02 {
  white-space: nowrap;
  padding-top: 8px;
  padding-left:  10px;
  width:  90px;
}
:deep(.el-tag) {
  border: none !important;
  color: white !important;
}

:deep(.el-tag--success) {
  background-color: #4CAF50 !important; /* 清新绿 - 表示正常状态 */
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.25); /* 添加微妙阴影增强层次感 */
}

:deep(.el-tag--info) {
  background-color: #90A4AE !important; /* 蓝灰色 - 表示中性状态 */
  box-shadow: 0 2px 4px rgba(144, 164, 174, 0.25);
}

:deep(.el-tag--danger) {
  background-color: #FF7043 !important; /* 橙红色 - 表示警告状态 */
  box-shadow: 0 2px 4px rgba(255, 112, 67, 0.25);
  animation: pulse-danger 2s infinite; /* 添加微弱脉动效果吸引注意但不刺眼 */
}

/* 警告状态的脉动动画（可选） */
@keyframes pulse-danger {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

/* 统一调整标签样式增强美观性 */
:deep(.el-tag) {
  border: none !important;
  color: white !important;
  font-weight: 500 !important; /* 稍微加粗字体 */
  padding: 0 12px !important; /* 增加内边距 */
  height: 28px !important; /* 统一高度 */
  line-height: 28px !important;
  border-radius: 14px !important; /* 圆角增大更柔和 */
  display: inline-flex !important;
  align-items: center !important;
  transition: all 0.3s ease !important; /* 添加过渡效果 */
}
</style>