<template>
  <div class="agent-actions">
    <div class="panel-header">
      <h3>智能体动作</h3>
      <button @click="fetchAgentActions" class="refresh-btn">
        <span class="refresh-icon">↻</span>
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="activeAgent && pendingActions.length > 0" class="actions-container">
      <h4>待处理动作 ({{ activeAgent }})</h4>
      <div 
        v-for="action in pendingActions" 
        :key="action.tool_call_id"
        class="action-item"
      >
        <div class="action-header">
          <div class="action-name">{{ action.function_name }}</div>
          <div class="action-id">ID: {{ action.tool_call_id.substring(0, 8) }}...</div>
        </div>
        
        <div class="action-args">
          <pre>{{ formatArgs(action.arguments) }}</pre>
        </div>
        
        <!-- 移动工具UI -->
        <div v-if="action.function_name === 'move'" class="tool-specific-ui">
          <div class="move-controls">
            <div class="direction-display">
              移动方向: <strong>{{ getDirectionFromArgs(action.arguments) }}</strong>
            </div>
            <div class="movement-buttons">
              <button
                @click="executeMove(action, true)"
                class="move-success-btn"
              >
                移动成功
              </button>
              <button
                @click="executeMove(action, false)"
                class="move-fail-btn"
              >
                移动失败
              </button>
            </div>
          </div>
        </div>
        
        <!-- 感知工具UI -->
        <div v-else-if="action.function_name === 'sense'" class="tool-specific-ui">
          <div class="sense-controls">
            <textarea 
              v-model="sensedResults[action.tool_call_id]" 
              rows="4" 
              placeholder="输入感知到的环境信息..."
              class="sense-input"
            ></textarea>
            <button
              @click="executeSense(action)"
              class="sense-btn"
              :disabled="!sensedResults[action.tool_call_id]"
            >
              提交感知结果
            </button>
          </div>
        </div>
        
        <!-- 获取位置工具UI -->
        <div v-else-if="action.function_name === 'get_position'" class="tool-specific-ui">
          <div class="position-controls">
            <div class="position-input-group">
              <div class="position-label">X:</div>
              <input 
                v-model="positionResults[action.tool_call_id].x" 
                type="number" 
                class="position-input"
              />
              <div class="position-label">Y:</div>
              <input 
                v-model="positionResults[action.tool_call_id].y" 
                type="number" 
                class="position-input"
              />
            </div>
            <button
              @click="executeGetPosition(action)"
              class="position-btn"
              :disabled="!positionResults[action.tool_call_id].x || !positionResults[action.tool_call_id].y"
            >
              提交位置
            </button>
          </div>
        </div>
        
        <!-- 其他工具的默认UI -->
        <div v-else class="action-controls">
          <input 
            v-model="actionResults[action.tool_call_id]" 
            placeholder="结果描述..." 
            class="result-input"
          />
          <button 
            @click="completeGenericAction(action)" 
            class="complete-btn"
            :disabled="!actionResults[action.tool_call_id]"
          >
            完成动作
          </button>
        </div>
      </div>
    </div>
    
    <div v-else-if="activeAgent" class="empty-state">
      <p>当前没有待处理的动作</p>
    </div>
    
    <div v-else class="empty-state">
      <p>请先选择一个智能体</p>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'AgentActions',
  
  props: {
    activeAgent: {
      type: String,
      default: ''
    }
  },
  
  data() {
    return {
      pendingActions: [],
      actionResults: {},
      sensedResults: {},
      positionResults: {},
      loading: false,
      pollingInterval: null
    };
  },
  
  watch: {
    activeAgent(newValue) {
      if (newValue) {
        this.fetchAgentActions();
        this.startPolling();
      } else {
        this.stopPolling();
        this.pendingActions = [];
      }
    }
  },
  
  methods: {
    formatArgs(argsString) {
      try {
        const args = JSON.parse(argsString);
        return JSON.stringify(args, null, 2);
      } catch (e) {
        return argsString;
      }
    },
    
    getDirectionFromArgs(argsString) {
      try {
        const args = JSON.parse(argsString);
        return args.direction || '未知';
      } catch (e) {
        return '未知';
      }
    },
    
    async fetchAgentActions() {
      if (!this.activeAgent) return;
      
      this.loading = true;
      try {
        const response = await api.getAgentPendingActions(this.activeAgent);
        this.pendingActions = response.data;
        
        // 初始化各类工具的结果输入框
        this.pendingActions.forEach(action => {
          // 常规动作结果
          if (!this.actionResults[action.tool_call_id]) {
            this.actionResults[action.tool_call_id] = '';
          }
          
          // 感知工具结果
          if (action.function_name === 'sense' && !this.sensedResults[action.tool_call_id]) {
            this.sensedResults[action.tool_call_id] = '';
          }
          
          // 位置工具结果
          if (action.function_name === 'get_position' && !this.positionResults[action.tool_call_id]) {
            this.positionResults[action.tool_call_id] = { x: '', y: '' };
          }
        });
      } catch (error) {
        console.error('获取智能体动作失败', error);
      } finally {
        this.loading = false;
      }
    },
    
    // 执行移动动作
    async executeMove(action, success) {
      let result = '';
      
      if (success) {
        const direction = this.getDirectionFromArgs(action.arguments);
        result = `成功向${direction}方向移动`;
        
        // 调用后端执行移动
        try {
          await api.executeAgentAction(this.activeAgent, {
            action_id: action.tool_call_id,
            action_name: 'move',
            action_args: JSON.parse(action.arguments),
            success: true
          });
        } catch (error) {
          console.error('执行移动失败', error);
          result = `移动操作失败: ${error.message || '未知错误'}`;
          success = false;
        }
      } else {
        result = `移动失败，遇到障碍物`;
      }
      
      await this.completeAction(action, result);
    },
    
    // 执行感知动作
    async executeSense(action) {
      const result = this.sensedResults[action.tool_call_id];
      if (!result) return;
      
      try {
        // 解析参数
        const args = JSON.parse(action.arguments);
        
        // 调用API通知后端
        await api.executeAgentAction(this.activeAgent, {
          action_id: action.tool_call_id,
          action_name: 'sense',
          action_args: args,
          success: true
        });
      } catch (error) {
        console.error('执行感知操作失败', error);
      }
      
      await this.completeAction(action, result);
      delete this.sensedResults[action.tool_call_id];
    },
    
    // 执行获取位置动作
    async executeGetPosition(action) {
      const position = this.positionResults[action.tool_call_id];
      if (!position.x || !position.y) return;
      
      const result = `当前位置: (${position.x}, ${position.y})`;
      
      try {
        // 调用API通知后端
        await api.executeAgentAction(this.activeAgent, {
          action_id: action.tool_call_id,
          action_name: 'get_position',
          action_args: {},
          success: true
        });
      } catch (error) {
        console.error('执行获取位置操作失败', error);
      }
      
      await this.completeAction(action, result);
      delete this.positionResults[action.tool_call_id];
    },
    
    // 执行通用动作
    async completeGenericAction(action) {
      const result = this.actionResults[action.tool_call_id];
      if (!result) return;
      
      await this.completeAction(action, result);
      delete this.actionResults[action.tool_call_id];
    },
    
    // 完成动作的通用方法
    async completeAction(action, result) {
      try {
        await api.completeAgentAction(this.activeAgent, {
          action_id: action.tool_call_id,
          result: result
        });
        
        // 从列表中移除已完成的动作
        this.pendingActions = this.pendingActions.filter(
          a => a.tool_call_id !== action.tool_call_id
        );
      } catch (error) {
        console.error('完成动作失败', error);
      }
    },
    
    startPolling() {
      this.stopPolling();
      this.pollingInterval = setInterval(() => {
        this.fetchAgentActions();
      }, 3000);
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    }
  },
  
  mounted() {
    if (this.activeAgent) {
      this.fetchAgentActions();
      this.startPolling();
    }
  },
  
  beforeUnmount() {
    this.stopPolling();
  }
};
</script>

<style scoped>
.agent-actions {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #1976d2;
  font-size: 18px;
}

.actions-container {
  margin-top: 10px;
}

.action-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.action-name {
  font-weight: bold;
  color: #333;
}

.action-id {
  font-size: 0.8em;
  color: #666;
}

.action-args {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 12px;
  overflow-x: auto;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.action-controls, .tool-specific-ui {
  margin-top: 12px;
}

.result-input, .sense-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
}

.complete-btn, .sense-btn, .position-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  margin-top: 8px;
}

.move-success-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  margin-right: 8px;
}

.move-fail-btn {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.complete-btn:hover, .sense-btn:hover, .position-btn:hover, .move-success-btn:hover {
  background-color: #388e3c;
}

.move-fail-btn:hover {
  background-color: #d32f2f;
}

.complete-btn:disabled, .sense-btn:disabled, .position-btn:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}

.direction-display {
  margin-bottom: 8px;
}

.movement-buttons {
  display: flex;
}

.position-input-group {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.position-label {
  margin-right: 8px;
  margin-left: 16px;
}

.position-label:first-child {
  margin-left: 0;
}

.position-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style> 