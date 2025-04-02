from typing import Dict, List, Optional, Union
from asyncio import Future

from app.agent.toolcall import ToolCallAgent
from app.tool import ToolCollection
from app.tool.movement import GetPositionTool, MoveTool, SenseTool
from app.world.models import GameObject, Position, WorldMap
from app.schema import Message
from app.schema import ToolChoice
from pydantic import Field

GAME_AGENT_SYSTEM_PROMPT = """你是游戏世界中的一个智能体，可以在游戏世界中移动并感知周围环境。
你的目标是探索世界并与其他智能体互动。
你可以使用以下工具：
- move: 向上、下、左、右移动
- sense: 感知周围环境中的物体
- get_position: 获取当前位置信息

当你被分配任务时，积极思考如何完成，并用工具来探索和行动。
"""

class GameAgent(ToolCallAgent):
    """游戏中的智能体，继承自ToolCallAgent并代理GameObject功能"""
    
    position: Position = Field(..., description="Agent在地图中的位置")
    game_description: str = Field("", description="游戏中的描述")
    
    def __init__(
        self, 
        agent_id: str, 
        position: Position, 
        world_map: WorldMap,
        description: str = "",
        system_prompt: str = GAME_AGENT_SYSTEM_PROMPT
    ):
        # 初始化ToolCallAgent，使用agent_id作为name参数
        super().__init__(
            name=agent_id,  # name字段用作智能体的唯一标识符
            description=f"游戏智能体: {description}",
            system_prompt=system_prompt,
            position=position,
            game_description=description
        )
        
        # 游戏相关属性
        self.world_map = world_map
        
        # 设置可用工具
        self._setup_tools()
        
        # 前端交互属性
        self.pending_actions: List[Dict] = []
        self.action_future: Optional[Future] = None
        
        # 将自己添加到世界地图
        game_obj = GameObject(
            id=agent_id,  # 在GameObject中使用agent_id作为id
            position=position,
            description=description
        )
        self.world_map.add_object(game_obj)
    
    def _setup_tools(self):
        """设置可用工具"""
        # 创建移动和感知工具
        move_tool = MoveTool(agent_id=self.name, world_map=self.world_map)  # 使用name而不是id
        sense_tool = SenseTool(agent_id=self.name, world_map=self.world_map)
        get_position_tool = GetPositionTool(agent_id=self.name, world_map=self.world_map)
        
        # 更新可用工具
        self.available_tools = ToolCollection(
            move_tool,
            sense_tool,
            get_position_tool
        )
    
    async def act(self) -> str:
        """覆盖父类方法，将工具调用信息发送到前端并等待执行完成"""
        if not self.tool_calls:
            if self.tool_choices == ToolChoice.REQUIRED:
                raise ValueError("Tool calls required but none provided")
            
            # 返回最后一条消息内容（如果没有工具调用）
            return self.messages[-1].content or "无内容或命令执行"
        
        # 准备工具调用信息，将发送到前端
        self.pending_actions = []
        for command in self.tool_calls:
            action_info = {
                "agent_id": self.name,
                "tool_call_id": command.id,
                "function_name": command.function.name,
                "arguments": command.function.arguments
            }
            self.pending_actions.append(action_info)
        
        # 如果没有pending_actions，返回空结果
        if not self.pending_actions:
            return "无动作需要执行"
        
        # 创建异步等待对象
        import asyncio
        self.action_future = asyncio.get_event_loop().create_future()
        
        # 返回一个特殊标记，表示有动作等待前端执行
        # 此时调度器应该获取pending_actions并传给前端
        result = "PENDING_FRONTEND_ACTIONS"
        
        # 等待前端完成所有动作
        try:
            await self.action_future
            result = "前端动作执行完成"
        except asyncio.CancelledError:
            result = "动作执行被取消"
            
        # 重置Future
        self.action_future = None
        
        return result
    
    async def complete_frontend_action(self, action_id: str, result: str, base64_image: Optional[str] = None) -> None:
        """前端完成动作后调用此方法，继续agent的执行流程"""
        # 查找对应的工具调用
        matching_tool_call = None
        for tool_call in self.tool_calls:
            if tool_call.id == action_id:
                matching_tool_call = tool_call
                break
        
        if not matching_tool_call:
            return
        
        # 添加工具响应到记忆中
        tool_msg = Message.tool_message(
            content=result,
            tool_call_id=action_id,
            name=matching_tool_call.function.name,
            base64_image=base64_image
        )
        self.memory.add_message(tool_msg)
        
        # 从pending_actions中移除已完成的动作
        self.pending_actions = [a for a in self.pending_actions if a["tool_call_id"] != action_id]
        
        # 如果所有动作都已完成，可以继续执行
        if not self.pending_actions and self.action_future and not self.action_future.done():
            self.action_future.set_result(True)
    
    def get_pending_actions(self) -> List[Dict]:
        """获取等待前端执行的动作列表"""
        return self.pending_actions
    
    async def assign_task(self, task_description: str) -> str:
        """分配任务给智能体"""
        # 添加任务到智能体的记忆中
        self.update_memory("user", task_description)
        
        # 运行智能体处理任务
        result = await self.run()
        
        return result 