<template>
  <div class="device-status">
    <h2>设备状态</h2>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>仪表盘</el-breadcrumb-item>
      <el-breadcrumb-item>设备状态</el-breadcrumb-item>
    </el-breadcrumb>

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
            {{ scope.row.status }}
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
            <el-option label="在线" value="Online"></el-option>
            <el-option label="离线" value="Offline"></el-option>
            <el-option label="故障" value="Faulty"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="温度 (°C)" prop="temperature">
          <el-input
              v-model.number="newDevice.temperature"
              type="number"
              placeholder="请输入温度"
          ></el-input>
        </el-form-item>
        <el-form-item label="湿度 (%)" prop="humidity">
          <el-input
              v-model.number="newDevice.humidity"
              type="number"
              placeholder="请输入湿度"
          ></el-input>
        </el-form-item>
        <el-form-item label="pH值" prop="phValue">
          <el-input
              v-model.number="newDevice.phValue"
              type="number"
              step="0.1"
              placeholder="请输入pH值"
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
            <el-option label="在线" value="Online"></el-option>
            <el-option label="离线" value="Offline"></el-option>
            <el-option label="故障" value="Faulty"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="温度 (°C)" prop="temperature">
          <el-input
              v-model.number="editingDevice.temperature"
              type="number"
              placeholder="请输入温度"
          ></el-input>
        </el-form-item>
        <el-form-item label="湿度 (%)" prop="humidity">
          <el-input
              v-model.number="editingDevice.humidity"
              type="number"
              placeholder="请输入湿度"
          ></el-input>
        </el-form-item>
        <el-form-item label="pH值" prop="phValue">
          <el-input
              v-model.number="editingDevice.phValue"
              type="number"
              step="0.1"
              placeholder="请输入pH值"
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
      <!-- 你的页面内容 -->
      <askai />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
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
const newDevice = ref({
  id: '',
  name: '',
  operator: '',
  status: 'Online',
  temperature: null,
  humidity: null,
  phValue: null
});
const editingDevice = ref(null);
const selectedDevice = ref(null);

// 表单验证规则
const addFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  id: [{ required: true, message: '请输入设备ID', trigger: 'blur' }]
};

const editFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择设备状态', trigger: 'change' }]
};

// 获取设备列表
const fetchDevices = async (page = 1, size = 10) => {
  isLoading.value = true;
  try {
    // 使用相对路径，自动拼接baseURL
    const response = await axios.get('http://localhost:5000/api/device/list', { params: { page, size } });
    if (response.data.success) {
      devices.value = response.data.data;
      totalDevices.value = response.data.total;
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    ElMessage.error('获取设备列表失败，请检查后端服务');
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// 新增设备
const handleAddDevice = async () => {
  try {
    // 使用相对路径
    const response = await axios.post('http://localhost:5000/api/device', newDevice.value);
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
  try {
    // 使用相对路径
    const response = await axios.put(`http://localhost:5000/api/device/${editingDevice.value.id}`, editingDevice.value);
    if (response.data.success) {
      ElMessage.success('设备编辑成功');
      showEditModal.value = false;
      fetchDevices();
    } else {
      ElMessage.error(response.data.message);
    }
  } catch (error) {
    ElMessage.error('设备编辑失败');
    console.error(error);
  }
};

// 删除设备
const handleDelete = async (id) => {
  await ElMessageBox.confirm('确认删除该设备？', '警告', {
    type: 'warning'
  }).then(async () => {
    // 使用相对路径
    const response = await axios.delete(`http://localhost:5000/api/device/${id}`);
    if (response.data.success) {
      ElMessage.success('设备删除成功');
      fetchDevices();
    } else {
      ElMessage.error(response.data.message);
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
    status: 'Online',
    temperature: null,
    humidity: null,
    phValue: null
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
    case 'Online': return 'success';
    case 'Offline': return 'info';
    case 'Faulty': return 'danger';
    default: return '';
  }
};

// 打开编辑模态框
const openEditModal = (device) => {
  editingDevice.value = { ...device };
  showEditModal.value = true;
};

// 关闭模态框时重置表单
const handleClose = () => {
  // 修复this指向问题
  if (this.$refs.addForm) this.$refs.addForm.resetFields();
  if (this.$refs.editForm) this.$refs.editForm.resetFields();
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
      device.status,
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
  link.setAttribute('download', `设备列表_${new Date().toLocaleDateString()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 生命周期钩子
onMounted(() => {
  fetchDevices();
});

// 计算过滤后的数据
const filteredDevices = computed(() => {
  return devices.value;
});
</script>

<style scoped>
.device-status {
  padding: 20px;
  background-color: #fbfbfb;
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

</style>