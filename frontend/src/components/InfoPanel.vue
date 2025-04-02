<template>
  <div class="info-panel card">
    <h2>系统信息</h2>
    
    <!-- Agent状态面板 -->
    <div class="status-panel mb-2">
      <h3>Agent状态</h3>
      
      <div v-if="Object.keys(agentStatus).length === 0" class="empty-state">
        还没有Agent状态信息
      </div>
      
      <div v-for="(status, id) in agentStatus" :key="id" class="status-item">
        <strong>{{ id }}:</strong>
        <span class="status-badge" :class="status">{{ status }}</span>
      </div>
    </div>
    
    <!-- 任务历史面板 -->
    <div class="history-panel">
      <h3>任务历史</h3>
      
      <div v-if="taskHistory.length === 0" class="empty-state">
        还没有任务历史记录
      </div>
      
      <div v-for="(task, index) in taskHistory" :key="index" class="history-item">
        <div class="history-header">
          <div>
            <strong>Agent:</strong> {{ task.agent_id }}
          </div>
          <div>
            <span class="status-badge" :class="task.status">{{ task.status }}</span>
          </div>
        </div>
        
        <div><strong>任务:</strong> {{ task.task }}</div>
        
        <div v-if="task.result" class="task-result">
          <strong>结果:</strong> {{ formatResult(task.result) }}
        </div>
        
        <div v-if="task.error" class="task-error">
          <strong>错误:</strong> {{ task.error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InfoPanel',
  props: {
    agentStatus: {
      type: Object,
      required: true
    },
    taskHistory: {
      type: Array,
      required: true
    }
  },
  methods: {
    formatResult(result) {
      if (!result) return '';
      
      // 如果结果太长，截断显示
      if (result.length > 100) {
        return `${result.substring(0, 100)}...`;
      }
      
      return result;
    }
  }
}
</script>

<style scoped>
.status-item, 
.history-item {
  padding: 10px;
  margin-bottom: 8px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.history-item {
  border-left: 3px solid #3498db;
}

.status-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.8rem;
  background-color: #95a5a6;
  color: white;
}

.status-badge.idle {
  background-color: #27ae60;
}

.status-badge.busy {
  background-color: #f39c12;
}

.status-badge.error {
  background-color: #e74c3c;
}

.status-badge.completed {
  background-color: #2ecc71;
}

.status-badge.failed {
  background-color: #e74c3c;
}

.status-badge.assigned {
  background-color: #3498db;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.task-result {
  margin-top: 5px;
  font-size: 0.9rem;
}

.task-error {
  margin-top: 5px;
  color: #e74c3c;
  font-size: 0.9rem;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #7f8c8d;
  background-color: #f8f9fa;
  border-radius: 5px;
}
</style> 