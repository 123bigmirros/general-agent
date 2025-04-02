<template>
  <div class="task-panel-container">
    <!-- 指定Agent任务面板 -->
    <div v-if="selectedAgent" class="task-panel card">
      <h2>给 {{ selectedAgent }} 分配任务</h2>
      
      <textarea 
        v-model="taskDescription" 
        rows="4" 
        placeholder="输入任务描述..."
      ></textarea>
      
      <div class="task-options">
        <label class="checkbox-label">
          <input type="checkbox" v-model="asyncTask"> 
          <span>异步执行</span>
        </label>
      </div>
      
      <button 
        @click="assignTask" 
        :disabled="!taskDescription || isLoading"
      >
        {{ isLoading ? '执行中...' : '分配任务' }}
      </button>
      
      <div v-if="taskResult" class="task-result mt-2">
        <h3>任务结果:</h3>
        <pre>{{ taskResult }}</pre>
      </div>
    </div>
    
    <!-- 广播任务面板 -->
    <div class="broadcast-panel card">
      <h2>广播任务</h2>
      
      <textarea 
        v-model="broadcastTask" 
        rows="4" 
        placeholder="输入广播任务..."
      ></textarea>
      
      <button 
        @click="broadcastToAll" 
        :disabled="!broadcastTask || isBroadcasting"
      >
        {{ isBroadcasting ? '广播中...' : '广播给所有Agent' }}
      </button>
      
      <div v-if="broadcastResult" class="task-result mt-2">
        <h3>广播结果:</h3>
        <pre>{{ broadcastResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'TaskPanel',
  props: {
    selectedAgent: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      taskDescription: '',
      asyncTask: false,
      taskResult: '',
      isLoading: false,
      
      broadcastTask: '',
      broadcastResult: '',
      isBroadcasting: false
    }
  },
  methods: {
    async assignTask() {
      if (!this.selectedAgent || !this.taskDescription) return;
      
      this.isLoading = true;
      this.taskResult = '';
      
      try {
        const response = await api.assignTask(this.selectedAgent, {
          task: this.taskDescription,
          async: this.asyncTask
        });
        
        this.taskResult = JSON.stringify(response.data, null, 2);
        this.$emit('refresh');
        
        // 如果是异步任务，定时刷新
        if (this.asyncTask) {
          this.startPolling();
        }
      } catch (error) {
        this.taskResult = `错误: ${error.response?.data?.error || error.message}`;
      } finally {
        this.isLoading = false;
      }
    },
    
    async broadcastToAll() {
      if (!this.broadcastTask) return;
      
      this.isBroadcasting = true;
      this.broadcastResult = '';
      
      try {
        const response = await api.broadcastTask({
          task: this.broadcastTask
        });
        
        this.broadcastResult = JSON.stringify(response.data, null, 2);
        this.$emit('refresh');
        
        // 开始定时刷新状态
        this.startPolling();
      } catch (error) {
        this.broadcastResult = `错误: ${error.response?.data?.error || error.message}`;
      } finally {
        this.isBroadcasting = false;
      }
    },
    
    // 轮询检查Agent状态
    startPolling() {
      let pollCount = 0;
      const maxPolls = 30; // 最多轮询30次
      const pollInterval = 2000; // 每2秒轮询一次
      
      const poll = () => {
        setTimeout(async () => {
          pollCount++;
          await this.$emit('refresh');
          
          // 检查是否所有Agent都不是busy状态
          const response = await api.getStatus();
          const allIdle = Object.values(response.data).every(
            status => status !== 'busy'
          );
          
          if (!allIdle && pollCount < maxPolls) {
            poll();
          }
        }, pollInterval);
      };
      
      poll();
    },
    
    clearPanel() {
      this.taskDescription = '';
      this.taskResult = '';
    }
  },
  watch: {
    selectedAgent() {
      this.clearPanel();
    }
  }
}
</script>

<style scoped>
.task-panel-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-options {
  margin: 10px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
  margin-right: 5px;
  margin-bottom: 0;
}

.task-result {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.task-result pre {
  white-space: pre-wrap;
  overflow-wrap: break-word;
  font-family: monospace;
  font-size: 0.9rem;
}
</style> 