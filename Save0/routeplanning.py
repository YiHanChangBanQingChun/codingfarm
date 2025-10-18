from __builtins__ import *

# 优化的迷宫导航 - 使用 A* 算法直奔宝藏
for _ in range(1000):
	print("Maze run", _ + 1)
	clear()

	# world = 10
	# set_world_size(world)
	# world_size = world

	world_size = get_world_size()
	maze_unlocks = max(1, num_unlocked(Unlocks.Mazes))
	maze_scale = 2 ** (maze_unlocks - 1)
	substance_needed = world_size * maze_scale

	plant(Entities.Bush)
	use_item(Items.Weird_Substance, substance_needed)

	directions = [North, East, South, West]
	offsets = {
		North: (0, 1),
		East: (1, 0),
		South: (0, -1),
		West: (-1, 0),
	}
	opposite = {North: South, South: North, East: West, West: East}

	def manhattan_distance(x1, y1, x2, y2):
		dx = x1 - x2
		dy = y1 - y2
		if dx < 0:
			dx = -dx
		if dy < 0:
			dy = -dy
		return dx + dy

	def a_star_search():
		# """A* 寻路：DFS + 启发式"""
		target_x, target_y = measure()
		
		start = (get_pos_x(), get_pos_y())
		visited = {start: True}
		path = []
		
		def get_best_direction():
			# 返回朝向目标的最佳方向
			best_dir = None
			best_dist = 999999
			current_x = get_pos_x()
			current_y = get_pos_y()
			
			for direction in directions:
				if not can_move(direction):
					continue
				
				dx, dy = offsets[direction]
				next_x = current_x + dx
				next_y = current_y + dy
				next_pos = (next_x, next_y)
				
				if next_pos in visited:
					continue
				
				# 计算到目标的曼哈顿距离
				dist = manhattan_distance(next_x, next_y, target_x, target_y)
				if dist < best_dist:
					best_dist = dist
					best_dir = direction
			
			return best_dir
		
		while True:
			if get_entity_type() == Entities.Treasure:
				return True
			
			# 优先选择朝向目标的方向
			best_dir = get_best_direction()
			
			moved = False
			if best_dir:
				dx, dy = offsets[best_dir]
				next_pos = (get_pos_x() + dx, get_pos_y() + dy)
				move(best_dir)
				path.append(best_dir)
				visited[next_pos] = True
				moved = True
			else:
				# 没有朝向目标的未访问路径，尝试任意未访问的方向
				for direction in directions:
					if not can_move(direction):
						continue
					dx, dy = offsets[direction]
					next_pos = (get_pos_x() + dx, get_pos_y() + dy)
					if next_pos in visited:
						continue
					move(direction)
					path.append(direction)
					visited[next_pos] = True
					moved = True
					break
			
			# 无法前进，需要回退
			if not moved:
				if not path:
					return False
				back_direction = opposite[path.pop()]
				move(back_direction)
		
		return False

	def greedy_measure_walk():
		# """贪心策略：直接朝 measure() 方向前进"""
		max_attempts = world_size * world_size * 4
		attempts = 0
		stuck_counter = {}
		
		while attempts < max_attempts:
			if get_entity_type() == Entities.Treasure:
				return True
			
			target_x, target_y = measure()
			current_x = get_pos_x()
			current_y = get_pos_y()
			
			# 检查是否卡住
			pos = (current_x, current_y)
			if pos in stuck_counter:
				stuck_counter[pos] = stuck_counter[pos] + 1
			else:
				stuck_counter[pos] = 1
			
			# 卡住超过 5 次，使用 DFS 回退
			if stuck_counter[pos] > 5:
				return False
			
			moved = False
			
			# 计算目标方向的优先级
			dx = target_x - current_x
			dy = target_y - current_y
			
			# 根据距离确定主要方向和次要方向
			if dx < 0:
				dx = -dx
			if dy < 0:
				dy = -dy
			
			# 优先走距离更远的方向
			if dx > dy:
				# X 方向优先
				if current_x < target_x:
					if can_move(East):
						move(East)
						moved = True
				elif current_x > target_x:
					if can_move(West):
						move(West)
						moved = True
				
				if not moved:
					if current_y < target_y:
						if can_move(North):
							move(North)
							moved = True
					elif current_y > target_y:
						if can_move(South):
							move(South)
							moved = True
			else:
				# Y 方向优先
				if current_y < target_y:
					if can_move(North):
						move(North)
						moved = True
				elif current_y > target_y:
					if can_move(South):
						move(South)
						moved = True
				
				if not moved:
					if current_x < target_x:
						if can_move(East):
							move(East)
							moved = True
					elif current_x > target_x:
						if can_move(West):
							move(West)
							moved = True
			
			# 如果主方向都走不通，尝试任意可行方向
			if not moved:
				for direction in directions:
					if can_move(direction):
						move(direction)
						moved = True
						break
			
			if moved:
				attempts = attempts + 1
			else:
				# 完全卡死，无路可走
				return False
		
		return False

	# 优先使用贪心策略（最快），失败则用 A*
	reached = greedy_measure_walk()
	if not reached:
		reached = a_star_search()
	
	if reached and get_entity_type() == Entities.Treasure:
		harvest()