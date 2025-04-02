import asyncio
import random
import json
from typing import Dict, List, Optional, Set

from app.logger import logger
from app.agent.game_agent import GameAgent
from app.world.models import Position, WorldMap

class GameScheduler:
    """游戏调度器，负责管理多个Agent和分派任务"""
    
    def __init__(self, world_map: WorldMap):
        self.world_map = world_map
        self.agents: Dict[str, GameAgent] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.global_state: Dict[str, any] = {
            "task_history": [],  # 任务历史记录
            "agent_status": {},  # 智能体状态
            "pending_actions": {}  # 每个智能体的待处理操作
        }
    
    def create_agent(self, agent_id: str, description: str = "") -> GameAgent:
        """创建新的Agent并添加到调度器"""
        if agent_id in self.agents:
            raise ValueError(f"Agent ID '{agent_id}' 已存在")
        
        # 获取可用位置
        empty_positions = self.world_map.get_empty_positions()
        if not empty_positions:
            raise ValueError("世界地图已满，无法创建新的Agent")
        
        # 随机选择一个位置
        position = random.choice(empty_positions)
        
        # 创建Agent
        agent = GameAgent(
            agent_id=agent_id,
            position=position,
            world_map=self.world_map,
            description=description
        )
        # 添加到调度器
        self.agents[agent_id] = agent
        self.global_state["agent_status"][agent_id] = "idle"
        
        logger.info(f"创建Agent '{agent_id}' 在位置 {position}")
        
        return agent
    
    def remove_agent(self, agent_id: str) -> bool:
        """从调度器和世界地图中移除Agent"""
        if agent_id not in self.agents:
            return False
        
        # 取消正在运行的任务
        if agent_id in self.running_tasks and not self.running_tasks[agent_id].done():
            self.running_tasks[agent_id].cancel()
            del self.running_tasks[agent_id]
        
        # 从世界地图中移除
        self.world_map.remove_object(agent_id)
        
        # 从调度器中移除
        del self.agents[agent_id]
        if agent_id in self.global_state["agent_status"]:
            del self.global_state["agent_status"][agent_id]
        
        logger.info(f"移除Agent '{agent_id}'")
        
        return True
    
    async def assign_task(self, agent_id: str, task: str) -> str:
        """分配任务给指定的Agent"""
        if agent_id not in self.agents:
            return f"错误: Agent '{agent_id}' 不存在"
        
        agent = self.agents[agent_id]
        
        # 记录任务
        task_record = {
            "agent_id": agent_id,
            "task": task,
            "status": "assigned"
        }
        self.global_state["task_history"].append(task_record)
        self.global_state["agent_status"][agent_id] = "busy"
        
        # 启动任务
        try:
            result = await agent.assign_task(task)
            
            # 更新任务状态
            task_record["status"] = "completed"
            task_record["result"] = result
            self.global_state["agent_status"][agent_id] = "idle"
            
            return f"任务完成: {result}"
            
        except Exception as e:
            # 更新任务状态
            task_record["status"] = "failed"
            task_record["error"] = str(e)
            self.global_state["agent_status"][agent_id] = "error"
            
            logger.error(f"Agent '{agent_id}' 执行任务时发生错误: {str(e)}")
            return f"任务失败: {str(e)}"
    
    async def assign_task_async(self, agent_id: str, task: str) -> str:
        """异步分配任务给指定的Agent"""
        if agent_id not in self.agents:
            return f"错误: Agent '{agent_id}' 不存在"
        
        # 如果已有任务在运行，取消它
        if agent_id in self.running_tasks and not self.running_tasks[agent_id].done():
            self.running_tasks[agent_id].cancel()
        
        # 创建新任务
        self.running_tasks[agent_id] = asyncio.create_task(
            self.assign_task(agent_id, task)
        )
        
        return f"任务已异步分配给Agent '{agent_id}'"
    
    async def broadcast_task(self, task: str) -> Dict[str, str]:
        """向所有Agent广播任务"""
        results = {}
        tasks = []
        
        for agent_id in self.agents:
            # 创建任务
            tasks.append(self.assign_task(agent_id, task))
        
        # 等待所有任务完成
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, agent_id in enumerate(self.agents):
            result = task_results[i]
            if isinstance(result, Exception):
                results[agent_id] = f"错误: {str(result)}"
            else:
                results[agent_id] = result
        
        return results
    
    async def get_agent_pending_actions(self, agent_id: str) -> List[Dict]:
        """获取指定Agent的待处理操作"""
        if agent_id not in self.agents:
            return []
        
        agent = self.agents[agent_id]
        pending_actions = agent.get_pending_actions()
        
        # 更新全局状态中的待处理操作
        self.global_state["pending_actions"][agent_id] = pending_actions
        
        return pending_actions
    
    async def complete_agent_action(self, agent_id: str, action_id: str, result: str, base64_image: Optional[str] = None) -> bool:
        """前端完成Agent的操作后调用此方法"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # 通知Agent动作已完成
        await agent.complete_frontend_action(action_id, result, base64_image)
        
        # 更新全局状态中的待处理操作
        pending_actions = agent.get_pending_actions()
        self.global_state["pending_actions"][agent_id] = pending_actions
        
        return True
    
    async def execute_frontend_action(self, agent_id: str, action_id: str, action_name: str, action_args: Dict, success: bool = True) -> bool:
        """执行前端传回的动作，更新游戏世界状态"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # 根据动作类型执行相应操作
        if action_name == "move" and success:
            # 解析移动参数
            try:
                # 确保action_args是字典类型
                direction = None
                if isinstance(action_args, str):
                    args_dict = json.loads(action_args)
                    direction = args_dict.get("direction")
                elif isinstance(action_args, dict):
                    direction = action_args.get("direction")
                else:
                    return False
                
                if not direction:
                    return False
                
                # 获取当前位置
                current_pos = agent.position
                
                # 根据方向计算新位置
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
                    return False
                
                # 执行移动
                if new_pos and self.world_map.is_valid_position(new_pos):
                    # 检查目标位置是否有其他物体
                    blocking_obj = self.world_map.get_object_at(new_pos)
                    if blocking_obj is None:
                        # 执行移动
                        if self.world_map.move_object(agent_id, new_pos):
                            # 移动成功，更新Agent的位置属性
                            agent.position = new_pos
                            logger.info(f"Agent '{agent_id}' 移动到位置 {new_pos}")
                            return True
                        else:
                            logger.info(f"Agent '{agent_id}' 移动失败：无法移动到 {new_pos}")
                            return False
                    else:
                        logger.info(f"Agent '{agent_id}' 无法移动到位置 {new_pos}，被 {blocking_obj.id} 阻挡")
                        return False
                else:
                    logger.info(f"Agent '{agent_id}' 移动失败：位置 {new_pos} 无效")
                    return False
            except Exception as e:
                logger.error(f"执行移动操作时出错: {str(e)}")
                return False
        elif action_name == "sense" and success:
            # 感知工具不改变世界状态，但可以记录日志
            try:
                range_value = 2  # 默认范围
                if isinstance(action_args, dict) and "range" in action_args:
                    range_value = action_args["range"]
                elif isinstance(action_args, str):
                    args_dict = json.loads(action_args)
                    if "range" in args_dict:
                        range_value = args_dict["range"]
                
                logger.info(f"Agent '{agent_id}' 执行感知操作，范围：{range_value}")
                return True
            except Exception as e:
                logger.error(f"执行感知操作时出错: {str(e)}")
                return False
        elif action_name == "get_position" and success:
            # 获取位置工具不改变世界状态，但可以记录日志
            logger.info(f"Agent '{agent_id}' 获取位置信息: {agent.position}")
            return True
        
        # 其他操作类型或失败情况
        return success
    
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, str]:
        """获取Agent状态"""
        if agent_id:
            if agent_id not in self.global_state["agent_status"]:
                return {"error": f"Agent '{agent_id}' 不存在"}
            return {agent_id: self.global_state["agent_status"][agent_id]}
        
        return self.global_state["agent_status"]
    
    def get_task_history(self) -> List[Dict]:
        """获取任务历史记录"""
        return self.global_state["task_history"]
    
    def get_world_state(self) -> Dict:
        """获取世界状态"""
        agents_info = {}
        for agent_id, agent in self.agents.items():
            agents_info[agent_id] = {
                "position": str(agent.position),
                "description": agent.description,
                "status": self.global_state["agent_status"].get(agent_id, "unknown")
            }
        
        return {
            "world_size": f"{self.world_map.width}x{self.world_map.height}",
            "agent_count": len(self.agents),
            "agents": agents_info
        } 