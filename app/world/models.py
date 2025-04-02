from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

@dataclass
class Position:
    """表示游戏世界中的位置"""
    x: int
    y: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'Position') -> int:
        """计算与另一个位置的曼哈顿距离"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def get_adjacent_positions(self) -> List['Position']:
        """获取相邻的位置"""
        return [
            Position(self.x + 1, self.y),
            Position(self.x - 1, self.y),
            Position(self.x, self.y + 1),
            Position(self.x, self.y - 1)
        ]

@dataclass
class GameObject:
    """游戏世界中的物体基类"""
    id: str
    position: Position
    description: str = ""
    
    def __str__(self) -> str:
        return f"{self.id} at {self.position}"

@dataclass
class WorldMap:
    """游戏世界地图"""
    width: int
    height: int
    objects: Dict[str, GameObject] = field(default_factory=dict)
    occupied_positions: Set[Position] = field(default_factory=set)
    
    def add_object(self, obj: GameObject) -> bool:
        """添加物体到地图，如果位置被占用则返回False"""
        if obj.position in self.occupied_positions:
            return False
        
        self.objects[obj.id] = obj
        self.occupied_positions.add(obj.position)
        return True
    
    def remove_object(self, obj_id: str) -> Optional[GameObject]:
        """从地图移除物体，返回被移除的物体或None"""
        if obj_id not in self.objects:
            return None
        
        obj = self.objects.pop(obj_id)
        self.occupied_positions.remove(obj.position)
        return obj
    
    def move_object(self, obj_id: str, new_position: Position) -> bool:
        """移动物体到新位置，如果新位置被占用则返回False"""
        if obj_id not in self.objects:
            return False
        
        if new_position in self.occupied_positions:
            return False
        
        obj = self.objects[obj_id]
        self.occupied_positions.remove(obj.position)
        obj.position = new_position
        self.occupied_positions.add(new_position)
        return True
    
    def get_object_at(self, position: Position) -> Optional[GameObject]:
        """获取指定位置的物体，如果没有则返回None"""
        for obj in self.objects.values():
            if obj.position == position:
                return obj
        return None
    
    def get_objects_in_range(self, center: Position, distance: int) -> List[GameObject]:
        """获取距离中心点指定距离内的所有物体"""
        result = []
        for obj in self.objects.values():
            if obj.position.distance_to(center) <= distance:
                result.append(obj)
        return result
    
    def is_valid_position(self, position: Position) -> bool:
        """检查位置是否在地图范围内"""
        return (0 <= position.x < self.width and 
                0 <= position.y < self.height)
    
    def is_position_occupied(self, position: Position) -> bool:
        """检查位置是否被占用"""
        return position in self.occupied_positions
    
    def get_empty_positions(self) -> List[Position]:
        """获取所有空位置"""
        empty = []
        for x in range(self.width):
            for y in range(self.height):
                pos = Position(x, y)
                if pos not in self.occupied_positions:
                    empty.append(pos)
        return empty 