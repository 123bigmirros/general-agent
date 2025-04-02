# Agent游戏系统

## 项目简介

这是一个基于LLM的Agent游戏系统，前端使用Vue，后端使用Flask。系统中的每个机器人都是一个独立运行的智能体Agent。

### 主要功能

- 多个独立运行的Agent
- 游戏世界地图可视化
- Agent移动和环境感知能力
- 任务分派和调度系统
- 全局状态监控

## 环境要求

- Python 3.8+
- Flask
- 前端依赖通过CDN加载（Vue 3, Axios）

## 安装和运行

1. 安装依赖:

```bash
pip install flask flask-cors
```

2. 运行应用:

```bash
python app.py
```

3. 访问网页:
在浏览器中打开 http://localhost:6000

## 使用方法

1. 创建Agent: 输入Agent ID和描述，点击"创建Agent"
2. 选择Agent: 在Agent列表中选择一个Agent
3. 分配任务: 输入任务描述，选择同步或异步执行，点击"分配任务"
4. 广播任务: 输入任务描述，点击"广播给所有Agent"

## 系统架构

- **世界系统**: 管理游戏世界、位置和物体
- **Agent系统**: 基于ToolCallAgent，具有移动和感知能力
- **工具系统**: 提供移动、感知和获取位置信息等能力
- **调度系统**: 管理多个Agent的任务分派和状态跟踪
- **前端界面**: 提供游戏世界可视化和Agent控制面板
