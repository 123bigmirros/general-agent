from typing import List, Optional

from app.tool.base import BaseTool, ToolResult
from app.world.models import Position, WorldMap, GameObject
from pydantic import Field

class MoveTool(BaseTool):
    """允许Agent在世界地图上移动的工具"""
    
    name: str = "move"
    description: str = "移动到相邻的位置"
    parameters: dict = {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["up", "down", "left", "right"],
                "description": "移动方向"
            }
        },
        "required": ["direction"]
    }
    
    # 添加为模型字段
    agent_id: str = Field(..., description="Agent的ID")  
    world_map: WorldMap = Field(..., description="游戏世界地图")
    
    def __init__(self, agent_id: str, world_map: WorldMap):
        # 使用硬编码值初始化基类
        super().__init__(
            name="move", 
            description="移动到相邻的位置", 
            parameters={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "移动方向"
                    }
                },
                "required": ["direction"]
            },
            # 通过构造函数参数传递这些值
            agent_id=agent_id,
            world_map=world_map
        )
    
    async def execute(self, direction: str, **kwargs) -> ToolResult:
        """准备移动操作的参数，实际移动由前端执行"""
        try:
            # 获取Agent当前位置
            agent = self.world_map.objects.get(self.agent_id)
            if not agent:
                return ToolResult(error=f"Agent {self.agent_id} 不存在")
            
            current_pos = agent.position
            
            # 根据方向确定新位置
            new_pos = None
            if direction == "up":
                new_pos = Position(current_pos.x, current_pos.y - 1)
            elif direction == "down":
                new_pos = Position(current_pos.x, current_pos.y + 1)
            elif direction == "left":
                new_pos = Position(current_pos.x - 1, current_pos.y)
            elif direction == "right":
                new_pos = Position(current_pos.x + 1, current_pos.y)
            else:
                return ToolResult(error=f"无效的方向: {direction}")
            
            # 检查新位置是否有效，但不执行实际移动
            if not self.world_map.is_valid_position(new_pos):
                return ToolResult(error=f"位置 {new_pos} 超出地图范围")
            
            # 检查是否有障碍物（但不执行移动）
            blocking_obj = self.world_map.get_object_at(new_pos)
            if blocking_obj:
                return ToolResult(error=f"目标位置 {new_pos} 被 {blocking_obj.id} 占据")
                
            # 返回移动参数，由前端来完成实际移动
            return ToolResult(output=f"准备移动到 {new_pos}，方向: {direction}")
                
        except Exception as e:
            return ToolResult(error=f"准备移动操作时发生错误: {str(e)}")

class SenseTool(BaseTool):
    """允许Agent感知周围环境的工具"""
    
    name: str = "sense"
    description: str = "感知周围环境"
    parameters: dict = {
        "type": "object",
        "properties": {
            "range": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "default": 2,
                "description": "感知范围（曼哈顿距离）"
            }
        }
    }
    
    # 添加为模型字段
    agent_id: str = Field(..., description="Agent的ID")  
    world_map: WorldMap = Field(..., description="游戏世界地图")
    
    def __init__(self, agent_id: str, world_map: WorldMap):
        # 使用硬编码值初始化基类
        super().__init__(
            name="sense", 
            description="感知周围环境", 
            parameters={
                "type": "object",
                "properties": {
                    "range": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 2,
                        "description": "感知范围（曼哈顿距离）"
                    }
                }
            },
            # 通过构造函数参数传递这些值
            agent_id=agent_id,
            world_map=world_map
        )
    
    async def execute(self, range: int = 2, **kwargs) -> ToolResult:
        """准备感知操作参数，实际感知由前端执行"""
        try:
            # 获取Agent当前位置
            agent = self.world_map.objects.get(self.agent_id)
            if not agent:
                return ToolResult(error=f"Agent {self.agent_id} 不存在")
            
            # 不执行实际感知，只返回请求参数
            return ToolResult(output=f"准备以 {range} 的范围感知周围环境，中心位置: {agent.position}")
                
        except Exception as e:
            return ToolResult(error=f"准备感知操作时发生错误: {str(e)}")

class GetPositionTool(BaseTool):
    """获取Agent当前位置的工具"""
    
    name: str = "get_position"
    description: str = "获取当前位置信息"
    parameters: dict = {
        "type": "object",
        "properties": {}
    }
    
    # 添加为模型字段
    agent_id: str = Field(..., description="Agent的ID")  
    world_map: WorldMap = Field(..., description="游戏世界地图")
    
    def __init__(self, agent_id: str, world_map: WorldMap):
        # 使用硬编码值初始化基类
        super().__init__(
            name="get_position", 
            description="获取当前位置信息", 
            parameters={
                "type": "object",
                "properties": {}
            },
            # 通过构造函数参数传递这些值
            agent_id=agent_id,
            world_map=world_map
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """准备获取位置信息，实际操作由前端执行"""
        try:
            # 获取Agent当前位置
            agent = self.world_map.objects.get(self.agent_id)
            if not agent:
                return ToolResult(error=f"Agent {self.agent_id} 不存在")
            
            # 不执行实际获取操作，只返回请求
            return ToolResult(output=f"准备获取位置信息，Agent ID: {self.agent_id}")
                
        except Exception as e:
            return ToolResult(error=f"准备获取位置操作时发生错误: {str(e)}") 