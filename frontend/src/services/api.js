import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export default {
  // Agent相关接口
  getAgents() {
    return apiClient.get('/agents');
  },
  
  getAgent(id) {
    return apiClient.get(`/agents/${id}`);
  },
  
  createAgent(agentData) {
    return apiClient.post('/agents', agentData);
  },
  
  removeAgent(id) {
    return apiClient.delete(`/agents/${id}`);
  },
  
  // 任务相关接口
  assignTask(agentId, taskData) {
    return apiClient.post(`/agents/${agentId}/tasks`, taskData);
  },
  
  broadcastTask(taskData) {
    return apiClient.post('/broadcast', taskData);
  },
  
  // 状态相关接口
  getStatus(agentId = null) {
    const params = agentId ? { agent_id: agentId } : {};
    return apiClient.get('/status', { params });
  },
  
  getHistory() {
    return apiClient.get('/history');
  },
  
  getWorldInfo() {
    return apiClient.get('/world');
  },
  
  // 代理动作相关接口
  getAgentPendingActions(agentId) {
    return apiClient.get(`/agents/${agentId}/actions`);
  },
  
  completeAgentAction(agentId, actionData) {
    return apiClient.post(`/agents/${agentId}/actions/${actionData.action_id}/complete`, actionData);
  },
  
  executeAgentAction(agentId, actionData) {
    return apiClient.post(`/agents/${agentId}/actions/${actionData.action_id}/execute`, actionData);
  }
}; 