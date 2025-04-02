import asyncio
import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

from app.world.models import WorldMap
from app.scheduler.scheduler import GameScheduler

# 创建Flask应用
app = Flask(__name__, static_folder='static', template_folder='templates')

# 配置CORS，允许所有来源的跨域请求
CORS(app)

# 创建游戏世界和调度器
world_map = WorldMap(width=10, height=10)
scheduler = GameScheduler(world_map)

# 辅助函数：将异步函数包装为Flask视图
def asyncio_handler(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__
    return wrapper

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：静态文件
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# API路由：创建Agent
@app.route('/api/agents', methods=['POST'])
def create_agent():
    data = request.json
    agent_id = data.get('agent_id')
    description = data.get('description', '')
    
    if not agent_id:
        return jsonify({'error': '缺少agent_id参数'}), 400
    
    try:
        agent = scheduler.create_agent(agent_id, description)
        return jsonify({
            'success': True,
            'agent_id': agent.name,
            'position': str(agent.position)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API路由：获取所有Agent
@app.route('/api/agents', methods=['GET'])
def get_agents():
    agents_info = {}
    for agent_id, agent in scheduler.agents.items():
        agents_info[agent_id] = {
            'position': str(agent.position),
            'description': agent.description,
            'status': scheduler.global_state["agent_status"].get(agent_id, "unknown")
        }
    
    return jsonify(agents_info)

# API路由：获取特定Agent
@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    if agent_id not in scheduler.agents:
        return jsonify({'error': f"Agent '{agent_id}' 不存在"}), 404
    
    agent = scheduler.agents[agent_id]
    return jsonify({
        'agent_id': agent.name,
        'position': str(agent.position),
        'description': agent.description,
        'status': scheduler.global_state["agent_status"].get(agent_id, "unknown")
    })

# API路由：移除Agent
@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def remove_agent(agent_id):
    success = scheduler.remove_agent(agent_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': f"Agent '{agent_id}' 不存在"}), 404

# API路由：分配任务
@app.route('/api/agents/<agent_id>/tasks', methods=['POST'])
@asyncio_handler
async def assign_task(agent_id):
    data = request.json
    task = data.get('task')
    async_mode = data.get('async', False)
    
    if not task:
        return jsonify({'error': '缺少task参数'}), 400
    
    if async_mode:
        result = await scheduler.assign_task_async(agent_id, task)
    else:
        result = await scheduler.assign_task(agent_id, task)
    
    return jsonify({'result': result})

# API路由：广播任务
@app.route('/api/broadcast', methods=['POST'])
@asyncio_handler
async def broadcast_task():
    data = request.json
    task = data.get('task')
    
    if not task:
        return jsonify({'error': '缺少task参数'}), 400
    
    results = await scheduler.broadcast_task(task)
    return jsonify(results)

# API路由：获取Agent状态
@app.route('/api/status', methods=['GET'])
def get_status():
    agent_id = request.args.get('agent_id')
    status = scheduler.get_agent_status(agent_id)
    return jsonify(status)

# API路由：获取任务历史
@app.route('/api/history', methods=['GET'])
def get_history():
    history = scheduler.get_task_history()
    return jsonify(history)

# API路由：获取世界状态
@app.route('/api/world', methods=['GET'])
def get_world():
    state = scheduler.get_world_state()
    return jsonify(state)

# API路由：获取Agent待处理动作
@app.route('/api/agents/<agent_id>/actions', methods=['GET'])
@asyncio_handler
async def get_agent_actions(agent_id):
    pending_actions = await scheduler.get_agent_pending_actions(agent_id)
    return jsonify(pending_actions)

# API路由：完成Agent动作
@app.route('/api/agents/<agent_id>/actions/<action_id>/complete', methods=['POST'])
@asyncio_handler
async def complete_agent_action(agent_id, action_id):
    data = request.json
    result = data.get('result', '')
    base64_image = data.get('base64_image')
    
    success = await scheduler.complete_agent_action(
        agent_id=agent_id,
        action_id=action_id,
        result=result,
        base64_image=base64_image
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': f"完成动作失败"}), 400

# API路由：执行前端传回的操作
@app.route('/api/agents/<agent_id>/actions/<action_id>/execute', methods=['POST'])
@asyncio_handler
async def execute_frontend_action(agent_id, action_id):
    data = request.json
    action_name = data.get('action_name')
    action_args = data.get('action_args', {})
    success = data.get('success', True)
    
    if not action_name:
        return jsonify({'error': '缺少action_name参数'}), 400
    
    result = await scheduler.execute_frontend_action(
        agent_id=agent_id,
        action_id=action_id,
        action_name=action_name,
        action_args=action_args,
        success=success
    )
    
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'error': f"执行操作失败"}), 400

if __name__ == '__main__':
    # 创建一些初始Agent用于测试
    # try:
    scheduler.create_agent("agent1", "第一个智能体")
    scheduler.create_agent("agent2", "第二个智能体")
    # except Exception as e:
    #     print(f"初始化Agent时出错: {e}")
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=6000) 