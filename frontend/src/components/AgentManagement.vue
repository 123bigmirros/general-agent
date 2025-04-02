<template>
  <div class="agent-management card">
    <h2>Agent管理</h2>
    
    <!-- 创建Agent表单 -->
    <div class="create-agent">
      <input v-model="newAgentId" placeholder="Agent ID" />
      <input v-model="newAgentDescription" placeholder="描述（可选）" />
      <button @click="createAgent" :disabled="!newAgentId">创建Agent</button>
    </div>
    
    <!-- Agent列表 -->
    <div class="agent-list mt-2">
      <h3>Agent列表</h3>
      
      <div v-if="Object.keys(agents).length === 0" class="empty-state">
        还没有Agent，创建一个吧！
      </div>
      
      <div v-for="(agent, id) in agents" :key="id" class="agent-item">
        <div class="agent-info">
          <div class="agent-title">
            <strong>{{ id }}</strong>
            <span class="agent-status" :class="agent.status">{{ agent.status }}</span>
          </div>
          <div>{{ agent.description }}</div>
          <div class="agent-position">位置: {{ agent.position }}</div>
        </div>
        <div class="agent-actions">
          <button @click="$emit('select-agent', id)" class="mr-1">选择</button>
          <button @click="removeAgent(id)" class="danger">移除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'AgentManagement',
  props: {
    agents: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      newAgentId: '',
      newAgentDescription: ''
    }
  },
  methods: {
    async createAgent() {
      if (!this.newAgentId) return;
      
      try {
        await api.createAgent({
          agent_id: this.newAgentId,
          description: this.newAgentDescription
        });
        
        this.$emit('refresh');
        
        // 清空表单
        this.newAgentId = '';
        this.newAgentDescription = '';
      } catch (error) {
        alert(`创建Agent失败: ${error.response?.data?.error || error.message}`);
      }
    },
    
    async removeAgent(agentId) {
      if (!confirm(`确定要移除Agent "${agentId}"吗？`)) return;
      
      try {
        await api.removeAgent(agentId);
        this.$emit('refresh');
      } catch (error) {
        alert(`移除Agent失败: ${error.response?.data?.error || error.message}`);
      }
    }
  }
}
</script>

<style scoped>
.agent-item {
  background-color: #f8f9fa;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.agent-title {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.agent-status {
  font-size: 0.8rem;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
  background-color: #95a5a6;
  color: white;
}

.agent-status.idle {
  background-color: #27ae60;
}

.agent-status.busy {
  background-color: #f39c12;
}

.agent-status.error {
  background-color: #e74c3c;
}

.agent-position {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.agent-actions {
  display: flex;
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: #7f8c8d;
  background-color: #f8f9fa;
  border-radius: 5px;
}
</style> 