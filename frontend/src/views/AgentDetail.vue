<template>
  <div>
    <div v-if="loading" class="loading-state">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="$router.push('/')">返回首页</button>
    </div>
    
    <div v-else>
      <div class="card agent-header">
        <div class="flex flex-between flex-center">
          <h2>{{ agent.agent_id }}</h2>
          <span class="status-badge" :class="agent.status">{{ agent.status }}</span>
        </div>
        <p>{{ agent.description || '没有描述' }}</p>
        <p class="position">当前位置: {{ agent.position }}</p>
      </div>
      
      <!-- 任务面板 -->
      <TaskPanel :selectedAgent="agent.agent_id" @refresh="loadAgent" />
      
      <!-- 智能体动作面板 -->
      <AgentActions :activeAgent="agent.agent_id" />
      
      <!-- 历史任务 -->
      <div class="card">
        <h2>历史任务</h2>
        
        <div v-if="agentTasks.length === 0" class="empty-state">
          这个Agent还没有执行过任务
        </div>
        
        <div v-for="(task, index) in agentTasks" :key="index" class="history-item">
          <div class="history-header">
            <div>
              <strong>任务:</strong> {{ task.task }}
            </div>
            <div>
              <span class="status-badge" :class="task.status">{{ task.status }}</span>
            </div>
          </div>
          
          <div v-if="task.result" class="task-result">
            <strong>结果:</strong> {{ task.result }}
          </div>
          
          <div v-if="task.error" class="task-error">
            <strong>错误:</strong> {{ task.error }}
          </div>
        </div>
      </div>
      
      <div class="actions mt-2">
        <button @click="$router.push('/')">返回首页</button>
        <button @click="removeAgent" class="danger">删除Agent</button>
      </div>
    </div>
  </div>
</template>

<script>
import TaskPanel from '@/components/TaskPanel.vue';
import AgentActions from '@/components/AgentActions.vue';
import api from '@/services/api';

export default {
  name: 'AgentDetail',
  components: {
    TaskPanel,
    AgentActions
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      agent: {},
      taskHistory: [],
      loading: true,
      error: null,
      refreshInterval: null
    };
  },
  computed: {
    // 过滤出当前Agent的任务
    agentTasks() {
      return this.taskHistory.filter(task => task.agent_id === this.id);
    }
  },
  methods: {
    async loadAgent() {
      this.loading = true;
      this.error = null;
      
      try {
        // 并行加载数据
        const [agentResponse, historyResponse] = await Promise.all([
          api.getAgent(this.id),
          api.getHistory()
        ]);
        
        this.agent = agentResponse.data;
        this.taskHistory = historyResponse.data;
        this.loading = false;
      } catch (error) {
        this.error = `加载Agent失败: ${error.response?.data?.error || error.message}`;
        this.loading = false;
      }
    },
    
    async removeAgent() {
      if (!confirm(`确定要删除Agent "${this.id}" 吗？`)) return;
      
      try {
        await api.removeAgent(this.id);
        this.$router.push('/');
      } catch (error) {
        alert(`删除失败: ${error.response?.data?.error || error.message}`);
      }
    }
  },
  created() {
    this.loadAgent();
    
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.loadAgent();
    }, 5000);
  },
  beforeUnmount() {
    // 清除定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }
};
</script>

<style scoped>
.agent-header {
  margin-bottom: 20px;
}

.position {
  color: #7f8c8d;
  font-style: italic;
  margin-top: 10px;
}

.actions {
  display: flex;
  gap: 10px;
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

.history-item {
  padding: 10px;
  margin-bottom: 10px;
  background-color: #f8f9fa;
  border-radius: 5px;
  border-left: 3px solid #3498db;
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

.loading-state,
.error-state,
.empty-state {
  padding: 30px;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 20px;
}

.error-state {
  color: #e74c3c;
}
</style> 