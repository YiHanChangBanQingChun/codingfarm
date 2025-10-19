from __builtins__ import *

# 多无人机迷宫寻宝 - 从同一起点快速分散探索
# 核心策略：每个无人机有不同的初始扩散方向，快速占领不同区域

def move_to(x, y):
	n = get_world_size()
	nowx = get_pos_x()
	nowy = get_pos_y()
	
	diffx = x - nowx
	abs_diffx = abs(diffx)
	if abs_diffx > n // 2:
		if diffx >= 0:
			diffx = abs_diffx - n
		else:
			diffx = n - abs_diffx
	
	diffy = y - nowy
	abs_diffy = abs(diffy)
	if abs_diffy > n // 2:
		if diffy >= 0:
			diffy = abs_diffy - n
		else:
			diffy = n - abs_diffy
	
	if diffx >= 0:
		for _ in range(diffx):
			move(East)
	else:
		for _ in range(-diffx):
			move(West)
	
	if diffy >= 0:
		for _ in range(diffy):
			move(North)
	else:
		for _ in range(-diffy):
			move(South)

def drone_search():
	# """每架无人机执行的搜索任务 - 随机扩散 + 混合算法# """
	
	# 记录起始位置，生成无人机ID
	start_x = get_pos_x()
	start_y = get_pos_y()
	drone_id = start_x * 100 + start_y
	
	# 第一阶段：随机扩散50步，避开死胡同
	expansion_steps = 50
	visited_expansion = {}
	
	for step in range(expansion_steps):
		entity = get_entity_type()
		if entity == Entities.Treasure:
			harvest()
			return True
		if entity != Entities.Hedge and entity != Entities.Treasure:
			return False
		
		# 记录当前位置
		current_pos = (get_pos_x(), get_pos_y())
		if current_pos not in visited_expansion:
			visited_expansion[current_pos] = 0
		visited_expansion[current_pos] = visited_expansion[current_pos] + 1
		
		# 如果在同一位置停留太久，说明可能在死胡同，强制换方向
		if visited_expansion[current_pos] > 3:
			visited_expansion = {}  # 清空记录，重新开始
		
		# 根据无人机ID选择不同的方向偏好
		base_dirs = [North, East, South, West]
		dir_offset = (drone_id + step) % 4
		
		# 尝试移动，优先选择没访问过或访问少的方向
		best_direction = None
		min_visits = 999
		
		for i in range(4):
			direction = base_dirs[(i + dir_offset) % 4]
			if can_move(direction):
				# 计算这个方向的下一个位置
				next_x = get_pos_x()
				next_y = get_pos_y()
				
				if direction == North:
					next_y = next_y + 1
				elif direction == South:
					next_y = next_y - 1
				elif direction == East:
					next_x = next_x + 1
				elif direction == West:
					next_x = next_x - 1
				
				next_pos = (next_x, next_y)
				if next_pos in visited_expansion:
					visits = visited_expansion[next_pos]
				else:
					visits = 0
				
				# 优先选择访问次数最少的方向
				if visits < min_visits:
					min_visits = visits
					best_direction = direction
		
		if best_direction:
			move(best_direction)
	
	# 第二阶段：根据ID选择算法
	# 偶数ID用贪心+A*，奇数ID用BFS
	use_bfs = (drone_id % 2) == 1
	
	if use_bfs:
		return bfs_search(drone_id)
	else:
		return greedy_and_astar_search(drone_id)

def greedy_and_astar_search(drone_id):
	# """贪心算法 + A*算法# """
	
	# 贪心阶段：直接朝measure()方向走
	max_greedy_steps = 100
	stuck_count = 0
	last_pos = (get_pos_x(), get_pos_y())
	
	for step in range(max_greedy_steps):
		entity = get_entity_type()
		if entity == Entities.Treasure:
			harvest()
			return True
		if entity != Entities.Hedge and entity != Entities.Treasure:
			return False
		
		# 检测卡住
		current_pos = (get_pos_x(), get_pos_y())
		if current_pos == last_pos:
			stuck_count = stuck_count + 1
			if stuck_count > 5:
				break  # 卡住了，切换到A*
		else:
			stuck_count = 0
		last_pos = current_pos
		
		# 使用measure()获取宝藏位置
		target_x, target_y = measure()
		current_x = get_pos_x()
		current_y = get_pos_y()
		
		dx = target_x - current_x
		dy = target_y - current_y
		
		# 优先走距离更远的轴
		moved = False
		if abs(dx) > abs(dy):
			# X轴优先
			if dx > 0 and can_move(East):
				move(East)
				moved = True
			elif dx < 0 and can_move(West):
				move(West)
				moved = True
			if not moved:
				if dy > 0 and can_move(North):
					move(North)
					moved = True
				elif dy < 0 and can_move(South):
					move(South)
					moved = True
		else:
			# Y轴优先
			if dy > 0 and can_move(North):
				move(North)
				moved = True
			elif dy < 0 and can_move(South):
				move(South)
				moved = True
			if not moved:
				if dx > 0 and can_move(East):
					move(East)
					moved = True
				elif dx < 0 and can_move(West):
					move(West)
					moved = True
		
		# 都走不通，随机尝试
		if not moved:
			for direction in [North, East, South, West]:
				if can_move(direction):
					move(direction)
					break
	
	# A*阶段：DFS + 启发式
	return astar_search(drone_id)

def astar_search(drone_id):
	# """A*算法：DFS + 距离启发式# """
	
	visited = {}
	path = []
	start_pos = (get_pos_x(), get_pos_y())
	visited[start_pos] = True
	
	base_directions = [North, East, South, West]
	direction_offset = drone_id % 4
	directions = []
	for i in range(4):
		directions.append(base_directions[(i + direction_offset) % 4])
	
	opposite = {North: South, South: North, East: West, West: East}
	
	max_steps = get_world_size() * get_world_size() * 8
	steps = 0
	
	while steps < max_steps:
		steps = steps + 1
		
		entity = get_entity_type()
		if entity != Entities.Hedge and entity != Entities.Treasure:
			return False
		if entity == Entities.Treasure:
			harvest()
			return True
		
		# 每隔一段时间用measure()调整方向
		if steps % 30 == 0:
			target_x, target_y = measure()
			current_x = get_pos_x()
			current_y = get_pos_y()
			dx = target_x - current_x
			dy = target_y - current_y
			
			# 尝试朝目标走3步
			for _ in range(3):
				if abs(dx) > abs(dy):
					if dx > 0 and can_move(East):
						move(East)
						break
					elif dx < 0 and can_move(West):
						move(West)
						break
				else:
					if dy > 0 and can_move(North):
						move(North)
						break
					elif dy < 0 and can_move(South):
						move(South)
						break
		
		# DFS搜索
		moved = False
		for direction in directions:
			if can_move(direction):
				next_x = get_pos_x()
				next_y = get_pos_y()
				
				if direction == North:
					next_y = next_y + 1
				elif direction == South:
					next_y = next_y - 1
				elif direction == East:
					next_x = next_x + 1
				elif direction == West:
					next_x = next_x - 1
				
				next_pos = (next_x, next_y)
				
				if next_pos not in visited:
					move(direction)
					visited[next_pos] = True
					path.append(direction)
					moved = True
					break
		
		if not moved:
			if len(path) == 0:
				return False
			back_direction = opposite[path.pop()]
			move(back_direction)
	
	return False

def bfs_search(drone_id):
	# """BFS广度优先搜索# """
	
	visited = {}
	queue = []  # 使用列表模拟队列
	start_pos = (get_pos_x(), get_pos_y())
	visited[start_pos] = True
	
	base_directions = [North, East, South, West]
	direction_offset = drone_id % 4
	directions = []
	for i in range(4):
		directions.append(base_directions[(i + direction_offset) % 4])
	
	opposite = {North: South, South: North, East: West, West: East}
	
	max_steps = get_world_size() * get_world_size() * 8
	steps = 0
	path = []
	
	while steps < max_steps:
		steps = steps + 1
		
		entity = get_entity_type()
		if entity != Entities.Hedge and entity != Entities.Treasure:
			return False
		if entity == Entities.Treasure:
			harvest()
			return True
		
		# BFS：尝试所有方向，记录可行的路径
		current_pos = (get_pos_x(), get_pos_y())
		available_directions = []
		
		for direction in directions:
			if can_move(direction):
				next_x = get_pos_x()
				next_y = get_pos_y()
				
				if direction == North:
					next_y = next_y + 1
				elif direction == South:
					next_y = next_y - 1
				elif direction == East:
					next_x = next_x + 1
				elif direction == West:
					next_x = next_x - 1
				
				next_pos = (next_x, next_y)
				
				if next_pos not in visited:
					available_directions.append((direction, next_pos))
		
		# 如果有未访问的方向，选择第一个
		if len(available_directions) > 0:
			direction, next_pos = available_directions[0]
			move(direction)
			visited[next_pos] = True
			path.append(direction)
			
			# 把其他可行方向加入队列（模拟BFS的层级遍历）
			for i in range(1, len(available_directions)):
				queue.append(available_directions[i])
		else:
			# 没有未访问的方向，回溯或从队列中取
			if len(path) > 0:
				back_direction = opposite[path.pop()]
				move(back_direction)
			elif len(queue) > 0:
				# 清空path，从队列中选择新路径
				path = []
				visited = {}
			else:
				return False
	
	return False

def spawn_drones_at_start():
	# """在迷宫入口生成所有无人机# """
	world_size = get_world_size()
	
	# 移动到迷宫入口 (0, 0)
	move_to(0, 0)
	
	# 确认在迷宫中
	entity = get_entity_type()
	if entity != Entities.Hedge and entity != Entities.Treasure:
		print("Not in maze!")
		return False
	
	# 生成32架无人机，它们会自动分散
	drone_count = 0
	max_drones = 32
	
	for i in range(max_drones):
		# 每生成一个无人机，主无人机稍微移动一下位置
		# 这样可以避免生成在完全相同的位置
		if i > 0:
			# 尝试移动一小步
			for direction in [North, East, South, West]:
				if can_move(direction):
					move(direction)
					break
		
		# 尝试生成无人机
		drone = spawn_drone(drone_search)
		if drone:
			drone_count = drone_count + 1
		else:
			# 无法生成更多无人机，主无人机自己搜索
			print("Cannot spawn more drones. Main drone searching...")
			result = drone_search()
			if result:
				print("Main drone found treasure!")
				return True
			break
	
	print("Spawned", drone_count, "drones from entrance")
	
	# 主无人机也参与搜索
	# 选择一个独特的扩散方向（与其他无人机不同）
	main_directions = [East, South, West, North]
	expansion_count = 0
	
	while expansion_count < 20:
		entity = get_entity_type()
		
		if entity == Entities.Treasure:
			harvest()
			print("Main drone found treasure!")
			return True
		elif entity != Entities.Hedge:
			print("Treasure found! Maze disappeared.")
			return True
		
		# 主无人机走一个特殊的螺旋路径
		direction = main_directions[expansion_count % 4]
		if can_move(direction):
			move(direction)
		expansion_count = expansion_count + 1
	
	# 然后进行DFS搜索
	visited = {}
	path = []
	current_pos = (get_pos_x(), get_pos_y())
	visited[current_pos] = True
	
	directions = [South, West, North, East]  # 主无人机的优先级
	opposite = {North: South, South: North, East: West, West: East}
	
	max_steps = world_size * world_size * 10
	steps = 0
	
	while steps < max_steps:
		steps = steps + 1
		
		entity = get_entity_type()
		
		if entity != Entities.Hedge and entity != Entities.Treasure:
			print("Treasure found by a drone!")
			return True
		
		if entity == Entities.Treasure:
			harvest()
			print("Main drone found treasure!")
			return True
		
		moved = False
		for direction in directions:
			if can_move(direction):
				next_x = get_pos_x()
				next_y = get_pos_y()
				
				if direction == North:
					next_y = next_y + 1
				elif direction == South:
					next_y = next_y - 1
				elif direction == East:
					next_x = next_x + 1
				elif direction == West:
					next_x = next_x - 1
				
				next_pos = (next_x, next_y)
				
				if next_pos not in visited:
					move(direction)
					visited[next_pos] = True
					path.append(direction)
					moved = True
					break
		
		if not moved:
			if len(path) == 0:
				return True
			back_direction = opposite[path.pop()]
			move(back_direction)
	
	return True

def main():
	# """主循环：不断创建新迷宫并搜索# """
	
	for maze_run in range(1000):
		print("=== Maze Run", maze_run + 1, "===")
		
		# 清理场地
		clear()
		
		# 设置世界大小为 32x32
		set_world_size(32)
		world_size = 32
		
		# 计算所需的 Weird_Substance
		maze_unlocks = max(1, num_unlocked(Unlocks.Mazes))
		maze_scale = 2 ** (maze_unlocks - 1)
		substance_needed = world_size * maze_scale
		
		print("Creating", world_size, "x", world_size, "maze")
		print("Substance needed:", substance_needed)
		
		# 在 (0, 0) 位置生成迷宫
		move_to(0, 0)
		plant(Entities.Bush)
		use_item(Items.Weird_Substance, substance_needed)
		
		print("Maze created! Spawning drones...")
		
		# 在迷宫入口生成所有无人机，它们会自动分散探索
		maze_completed = spawn_drones_at_start()
		
		if maze_completed:
			print("Maze completed! Moving to next...")
		
		# print()

# 执行主程序
if __name__ == "__main__":
	main()
	