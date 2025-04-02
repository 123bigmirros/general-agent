<template>
  <div class="game-world card">
    <h2>游戏世界 ({{ worldSize }})</h2>
    <div class="world-grid" 
      :style="{ 
        'grid-template-columns': `repeat(${worldWidth}, 1fr)`,
        'grid-template-rows': `repeat(${worldHeight}, 1fr)`
      }"
    >
      <div 
        v-for="cell in worldCells" 
        :key="cell.id" 
        class="grid-cell"
        :class="{ 'has-agent': cell.hasAgent }"
      >
        <span v-if="cell.agentId" 
              class="agent-marker" 
              :title="cell.agentId"
              :style="{ backgroundColor: getAgentColor(cell.agentId) }"
        >
          {{ cell.agentId.substring(0, 2) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameWorld',
  props: {
    agents: {
      type: Object,
      required: true
    },
    worldInfo: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      worldWidth: 10,
      worldHeight: 10,
      agentColors: {}
    };
  },
  computed: {
    worldSize() {
      return this.worldInfo.world_size || '10x10';
    },
    worldCells() {
      const cells = [];
      
      // 解析地图尺寸
      const sizeMatch = this.worldSize.match(/(\d+)x(\d+)/);
      if (sizeMatch) {
        this.worldWidth = parseInt(sizeMatch[1]);
        this.worldHeight = parseInt(sizeMatch[2]);
      }
      
      // 生成所有格子
      for (let y = 0; y < this.worldHeight; y++) {
        for (let x = 0; x < this.worldWidth; x++) {
          // 查找该位置是否有Agent
          let agentId = null;
          let hasAgent = false;
          
          for (const [id, agent] of Object.entries(this.agents)) {
            // 解析位置字符串，格式为 "(x, y)"
            const posMatch = agent.position.match(/\((\d+),\s*(\d+)\)/);
            if (posMatch) {
              const agentX = parseInt(posMatch[1]);
              const agentY = parseInt(posMatch[2]);
              
              if (agentX === x && agentY === y) {
                agentId = id;
                hasAgent = true;
                
                // 确保每个Agent有唯一颜色
                if (!this.agentColors[id]) {
                  this.agentColors[id] = this.generateColor(id);
                }
                
                break;
              }
            }
          }
          
          cells.push({
            id: `cell-${x}-${y}`,
            x,
            y,
            hasAgent,
            agentId
          });
        }
      }
      
      return cells;
    }
  },
  methods: {
    // 根据Agent ID生成一个唯一的颜色
    generateColor(id) {
      // 简单的字符串哈希函数
      let hash = 0;
      for (let i = 0; i < id.length; i++) {
        hash = id.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      // 转为HSL色值，饱和度和亮度保持不变
      const h = hash % 360;
      return `hsl(${h}, 70%, 60%)`;
    },
    
    getAgentColor(id) {
      return this.agentColors[id] || '#3498db';
    }
  }
};
</script>

<style scoped>
.game-world {
  margin-bottom: 20px;
}

.world-grid {
  display: grid;
  gap: 2px;
  background-color: #ecf0f1;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  height: 400px;
}

.grid-cell {
  background-color: #dfe6e9;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
}

.grid-cell.has-agent {
  background-color: #d4e6f1;
}

.agent-marker {
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.8rem;
}
</style> 