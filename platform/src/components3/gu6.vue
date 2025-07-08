<template>
  <div class="fault-management-container">
    <div class="toolbar">
      <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索设备ID或名称"
          class="search-box"
      />
      <div class="status-buttons">
        <button
            class="status-button"
            :class="{ active: selectedStatus === 'all' }"
            @click="handleStatusChange('all')"
        >
          全部
        </button>
        <button
            class="status-button"
            :class="{ active: selectedStatus === 'pending' }"
            @click="handleStatusChange('pending')"
        >
          待处理
        </button>
        <button
            class="status-button"
            :class="{ active: selectedStatus === 'in-progress' }"
            @click="handleStatusChange('in-progress')"
        >
          处理中
        </button>
        <button
            class="status-button"
            :class="{ active: selectedStatus === 'resolved' }"
            @click="handleStatusChange('resolved')"
        >
          已解决
        </button>
      </div>
    </div>

    <div class="table-container">
      <table class="fault-table">
        <thead>
        <tr>
          <th>故障信息</th>
          <th>设备ID</th>
          <th>设备名称</th>
          <th>时间信息</th>
          <th>相关人员</th>
          <th>处理状态</th>
          <th style="position: relative;right: -20px">操作</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="fault in filteredFaults" :key="fault.id">
          <td>{{ fault.faultInfo || '无' }}</td>
          <td>{{ fault.deviceId }}</td>
          <td>{{ fault.deviceName }}</td>
          <td>{{ formatTimestamp(fault.timestamp) }}</td>
          <td>{{ fault.assignedTo || '未指派' }}</td>
          <td>
            <span :class="['status', fault.statusClass]">{{ fault.status }}</span>
          </td>
          <td v-if="fault.status === '功能故障' || fault.status === '离线故障'">
            <button
                class="notify-button"
                @click="notifyResponsible(fault)"
            >
              通知负责人
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <span>
        显示 {{ (currentPage - 1) * pageSize + 1 }} 到
        10 条，共 10 条记录
      </span>
      <div class="page-buttons">
        <button @click="prevPage" :disabled="currentPage === 1">&lt;</button>
        <button
            v-for="page in totalPages"
            :key="page"
            :class="{ active: currentPage === page }"
            @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button @click="nextPage" :disabled="currentPage === totalPages">&gt;</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FaultManagement',
  data() {
    return {
      searchQuery: '',
      selectedStatus: 'all',
      currentPage: 1,
      pageSize: 10,
      faults: [],
      total: 0
    };
  },
  computed: {
    filteredFaults() {
      return this.faults.slice(
          (this.currentPage - 1) * this.pageSize,
          this.currentPage * this.pageSize
      );
    },
    totalPages() {
      return Math.ceil(this.total / this.pageSize);
    }
  },
  methods: {
    async fetchFaults() {
      try {
        const response = await fetch(`http://localhost:5000/fault-list?page=${this.currentPage}&size=${this.pageSize}&search=${this.searchQuery}&status=${this.selectedStatus}`);
        const data = await response.json();
        if (data.success) {
          this.faults = data.data;
          this.total = data.total;
        } else {
          console.error('获取故障列表失败:', data.message);
        }
      } catch (error) {
        console.error('网络请求失败:', error);
      }
    },
    handleStatusChange(status) {
      this.selectedStatus = status;
      this.currentPage = 1;
      this.fetchFaults();
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchFaults();
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchFaults();
      }
    },
    formatTimestamp(timestamp) {
      if (!timestamp) return '-';
      const date = new Date(timestamp);
      return date.toLocaleString();
    },
    async notifyResponsible(fault) {
      try {
        const response = await fetch(`http://localhost:5000/api/fault/notify/${fault.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP错误 ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        if (data.success) {
          // 邮件发送成功，根据日志记录状态显示提示
          if (data.logStatus === 'success') {
            this.$message.success('通知已发送并记录');
          } else {
            this.$message({
              type: 'success',
              message: '通知已发送，但记录日志失败',
              description: '邮件已送达，系统日志可能不完整'
            });
          }
          this.fetchFaults(); // 刷新数据
        } else {
          // 邮件发送失败或其他错误
          let errorMsg = data.message;
          if (data.emailStatus === 'failed') {
            errorMsg = '邮件发送失败，请检查邮箱配置';
          }
          this.$message.error(errorMsg);
        }
      } catch (error) {
        console.error('通知请求失败:', error);
        this.$message.error('通知处理异常，请重试');
      }
    }
  },
  mounted() {
    this.fetchFaults();
  },
  watch: {
    searchQuery() {
      this.currentPage = 1;
      this.fetchFaults();
    },
    selectedStatus() {
      this.currentPage = 1;
      this.fetchFaults();
    },
    currentPage() {
      this.fetchFaults();
    }
  }
};
</script>

<style scoped>
.fault-management-container {
  font-family: Arial, sans-serif;
  padding: 20px;

  width: 1390px; /* 固定容器宽度 */
  margin: 0 auto;
  padding-right: 10px; /* 增加右内边距 */
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 300px;
  height: 35px;
  font-size: 17px;
  margin-left: 5px;
}

.status-buttons {
  display: flex;
  gap: 10px;
  margin-right: 15px;
  padding-right: 12px;
}

.status-button {
  width: 100px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #f0f0f0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.status-button.active {
  background-color: #1a73e8;
  color: #fff;
  transform: translateY(-2px);
}

.table-container {
  width: 100%; /* 改为100%自适应 */
  overflow-x: auto;
}

.fault-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  table-layout: fixed;
}


.fault-table th, .fault-table td {
  padding: 12px;
  text-align: left;
  word-wrap: break-word;
  /* 让单元格内容垂直居中 */
  vertical-align: middle;
}

.fault-table tbody tr::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px; /* 左边留白20px */
  right: 20px; /* 统一右边留白20px */
  height: 1px;
  background-color: #ddd;
}

/* 调整列宽分配（新增第7列后重新计算） */
.fault-table th:nth-child(1), .fault-table td:nth-child(1) { width: 13%; } /* 故障信息 */
.fault-table th:nth-child(2), .fault-table td:nth-child(2) { width: 15%; }  /* 设备ID */
.fault-table th:nth-child(3), .fault-table td:nth-child(3) { width: 12%; } /* 设备名称 */
.fault-table th:nth-child(4), .fault-table td:nth-child(4) { width: 18%; } /* 时间信息 */
.fault-table th:nth-child(5), .fault-table td:nth-child(5) { width: 12%; } /* 相关人员 */
.fault-table th:nth-child(6), .fault-table td:nth-child(6) { width: 10%; } /* 处理状态 */
.fault-table th:nth-child(7), .fault-table td:nth-child(7) { width: 5%; } /* 操作列 */

.status {
  padding: 5px 10px;
  border-radius: 8px;
  color: #fff;
}

.status.pending { background-color: #ffcccc; color: #ff3d3d; }
.status.in-progress { background-color: #cce5ff; color: #1a73e8; }
.status.resolved { background-color: #ccffcc; color: #28a745; }

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.page-buttons { display: flex; gap: 5px; }

.page-buttons button {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  background-color: #f0f0f0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-buttons button.active {
  background-color: #1a73e8;
  color: #fff;
  transform: translateY(-2px);
}

/* 通知按钮样式 */
.notify-button {
  padding: 4px 8px;
  border: 1px solid #1a73e8;
  border-radius: 4px;
  background-color: #fff;
  color: #1a73e8;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
  white-space: nowrap;
  /* 关键：用 Flex 布局让按钮在单元格内居中 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.notify-button:hover {
  background-color: #e3f2fd;
}
</style>