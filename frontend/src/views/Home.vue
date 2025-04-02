<template>
  <div>
    <!-- 游戏世界 -->
    <GameWorld :agents="agents" :worldInfo="worldInfo" />
    
    <!-- 控制区域 -->
    <div class="grid grid-2 mt-2">
      <!-- 左侧：Agent管理和任务分派 -->
      <div>
        <!-- Agent管理 -->
        <AgentManagement 
          :agents="agents" 
          @refresh="loadData" 
          @select-agent="handleSelectAgent" 
        />
        
        <!-- 任务面板 -->
        <TaskPanel 
          :selectedAgent="selectedAgentId" 
          @refresh="loadData" 
        />
      </div>
      
      <!-- 右侧：信息面板 -->
      <InfoPanel 
        :agentStatus="agentStatus" 
        :taskHistory="taskHistory" 
      />
    </div>
  </div>
</template>

<script>
import GameWorld from '@/components/GameWorld.vue';
import AgentManagement from '@/components/AgentManagement.vue';
import TaskPanel from '@/components/TaskPanel.vue';
import InfoPanel from '@/components/InfoPanel.vue';
import api from '@/services/api';

export default {
  name: 'Home',
  components: {
    GameWorld,
    AgentManagement,
    TaskPanel,
    InfoPanel
  },
  data() {
    return {
      agents: {},
      worldInfo: { world_size: '10x10' },
      agentStatus: {},
      taskHistory: [],
      selectedAgentId: '',
      refreshInterval: null
    };
  },
  methods: {
    // 加载数据
    async loadData() {
      try {
        // 并行加载数据
        const [
          agentsResponse,
          statusResponse,
          historyResponse,
          worldResponse
        ] = await Promise.all([
          api.getAgents(),
          api.getStatus(),
          api.getHistory(),
          api.getWorldInfo()
        ]);
        
        this.agents = agentsResponse.data;
        this.agentStatus = statusResponse.data;
        this.taskHistory = historyResponse.data;
        this.worldInfo = worldResponse.data;
        
        // 如果当前选中的Agent已被删除，清除选择
        if (this.selectedAgentId && !this.agents[this.selectedAgentId]) {
          this.selectedAgentId = '';
        }
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    },
    
    // 选择Agent
    handleSelectAgent(agentId) {
      this.selectedAgentId = agentId;
    }
  },
  created() {
    // 初始加载数据
    this.loadData();
    
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.loadData();
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