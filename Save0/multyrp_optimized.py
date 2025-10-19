from __builtins__ import *

# 多线程迷宫寻宝 - 区域分割策略
# 32x32迷宫分为4x4的区域网格，每个区域8x8
# 16架无人机各自负责一个8x8区域的地图探索和宝藏收集

set_world_size(32)
clear()

world_size = 32
region_size = 8
maze_unlocks = max(1, num_unlocked(Unlocks.Mazes))
maze_scale = 2 ** (maze_unlocks - 1)
substance_needed = world_size * maze_scale

directions = [North, East, South, West]
offsets = {
	North: (0, 1),
	East: (1, 0),
	South: (0, -1),
	West: (-1, 0),
}
opposite = {North: South, South: North, East: West, West: East}

def move_to(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def manhattan_distance(x1, y1, x2, y2):
	dx = x1 - x2
	dy = y1 - y2
	if dx < 0:
		dx = -dx
	if dy < 0:
		dy = -dy
	return dx + dy

def explore_and_map_region(base_x, base_y):
	# 第一阶段:遍历8x8区域内所有可通行路径,建立地图
	# 使用BFS遍历,记录所有可达位置
	
	region_map = {}
	to_visit = [(base_x, base_y)]
	visited = {}
	visited[(base_x, base_y)] = True
	
	steps_taken = 0
	max_explore_steps = 1000
	
	while to_visit and steps_taken < max_explore_steps:
		target_x, target_y = to_visit[0]
		
		# 移除第一个元素(模拟队列pop)
		new_list = []
		for i in range(1, len(to_visit)):
			new_list.append(to_visit[i])
		to_visit = new_list
		
		# 检查是否超出区域范围
		if target_x < base_x or target_x >= base_x + region_size:
			continue
		if target_y < base_y or target_y >= base_y + region_size:
			continue
		
		# 移动到目标位置
		curr_x = get_pos_x()
		curr_y = get_pos_y()
		
		# 如果已经在目标位置,直接处理
		if curr_x == target_x and curr_y == target_y:
			region_map[(target_x, target_y)] = True
			
			# 探索四个方向的邻居
			for direction in directions:
				if can_move(direction):
					dx, dy = offsets[direction]
					next_x = target_x + dx
					next_y = target_y + dy
					next_pos = (next_x, next_y)
					
					if next_pos not in visited:
						if next_x >= base_x and next_x < base_x + region_size:
							if next_y >= base_y and next_y < base_y + region_size:
								visited[next_pos] = True
								to_visit.append(next_pos)
			continue
		
		# 尝试移动到target位置
		moved = False
		attempts = 0
		while attempts < 50 and (get_pos_x() != target_x or get_pos_y() != target_y):
			attempts = attempts + 1
			curr_x = get_pos_x()
			curr_y = get_pos_y()
			
			if curr_x < target_x and can_move(East):
				move(East)
				moved = True
			elif curr_x > target_x and can_move(West):
				move(West)
				moved = True
			elif curr_y < target_y and can_move(North):
				move(North)
				moved = True
			elif curr_y > target_y and can_move(South):
				move(South)
				moved = True
			else:
				break
		
		steps_taken = steps_taken + 1
		
		# 如果成功到达目标位置
		if get_pos_x() == target_x and get_pos_y() == target_y:
			region_map[(target_x, target_y)] = True
			
			# 探索四个方向的邻居
			for direction in directions:
				if can_move(direction):
					dx, dy = offsets[direction]
					next_x = target_x + dx
					next_y = target_y + dy
					next_pos = (next_x, next_y)
					
					if next_pos not in visited:
						if next_x >= base_x and next_x < base_x + region_size:
							if next_y >= base_y and next_y < base_y + region_size:
								visited[next_pos] = True
								to_visit.append(next_pos)
	
	# 探索完成,返回基地
	move_to(base_x, base_y)
	
	return region_map

def find_treasure_in_region(region_map, base_x, base_y):
	# 第二阶段:循环检测宝藏位置,如果在本区域则收集
	
	treasure_collected = 0
	max_treasures = 300
	not_in_region_count = 0
	max_not_in_region = 20
	
	while treasure_collected < max_treasures:
		# 测量宝藏位置
		treasure_pos = measure()
		
		if treasure_pos == None:
			break
		
		target_x, target_y = treasure_pos
		
		# 检查宝藏是否在本区域内
		in_my_region = True
		if target_x < base_x or target_x >= base_x + region_size:
			in_my_region = False
		if target_y < base_y or target_y >= base_y + region_size:
			in_my_region = False
		
		# 如果不在本区域,计数并等待
		if not in_my_region:
			not_in_region_count = not_in_region_count + 1
			if not_in_region_count >= max_not_in_region:
				break
			continue
		
		# 宝藏在本区域,重置计数器
		not_in_region_count = 0
		
		# 使用贪心A*算法寻找宝藏
		found = navigate_to_treasure(region_map, target_x, target_y)
		
		# 如果找到宝藏,收获并刷新迷宫
		if found and get_entity_type() == Entities.Treasure:
			while not can_harvest():
				use_item(Items.Fertilizer)
			harvest()
			treasure_collected = treasure_collected + 1
			
			if treasure_collected >= max_treasures:
				break
			
			use_item(Items.Weird_Substance, substance_needed)
		else:
			# 如果没找到宝藏,也计入not_in_region_count
			# 可能是宝藏已经被其他无人机收集了
			not_in_region_count = not_in_region_count + 1
			if not_in_region_count >= max_not_in_region:
				break
		
		# 返回基地
		move_to(base_x, base_y)

def navigate_to_treasure(region_map, target_x, target_y):
	# 在区域地图内导航到宝藏位置
	# 使用贪心算法+回溯
	
	path = []
	local_visited = {}
	current_pos = (get_pos_x(), get_pos_y())
	local_visited[current_pos] = True
	
	max_steps = 500
	steps = 0
	
	while steps < max_steps:
		steps = steps + 1
		
		# 检查是否到达宝藏
		if get_entity_type() == Entities.Treasure:
			return True
		
		# 寻找最佳移动方向(曼哈顿距离最小)
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
			
			# 跳过已访问的位置
			if next_pos in local_visited:
				continue
			
			# 跳过不在区域地图内的位置
			if next_pos not in region_map:
				continue
			
			# 计算到宝藏的距离
			dist = manhattan_distance(next_x, next_y, target_x, target_y)
			
			if dist < best_dist:
				best_dist = dist
				best_dir = direction
		
		# 如果找到最佳方向,移动
		if best_dir:
			dx, dy = offsets[best_dir]
			current_x = get_pos_x()
			current_y = get_pos_y()
			next_pos = (current_x + dx, current_y + dy)
			move(best_dir)
			path.append(best_dir)
			local_visited[next_pos] = True
		else:
			# 无路可走,回溯
			if not path:
				return False
			
			back_dir = opposite[path[len(path) - 1]]
			new_path = []
			for i in range(len(path) - 1):
				new_path.append(path[i])
			path = new_path
			move(back_dir)
	
	return False

def worker_drone_with_region(region_x, region_y):
	# 无人机工作函数:每个无人机负责一个8x8区域
	# region_x, region_y 是区域左下角坐标
	
	# 步骤1: 立即移动到指定区域
	move_to(region_x, region_y)
	
	# 步骤2: 等待迷宫生成
	# 所有无人机到达位置后,主无人机才会生成迷宫
	wait_count = 0
	maze_ready = False
	
	while wait_count < 3000:
		entity = get_entity_type()
		if entity == Entities.Hedge or entity == Entities.Treasure:
			maze_ready = True
			break
		wait_count = wait_count + 1
	
	# 如果迷宫没有生成,直接退出
	if not maze_ready:
		return
	
	# 步骤3: 迷宫已生成,开始工作流程
	# 第一阶段:探索并记忆区域地图(不管宝藏,只记录路径)
	region_map = explore_and_map_region(region_x, region_y)
	
	# 第二阶段:循环寻找并收集本区域内的宝藏
	find_treasure_in_region(region_map, region_x, region_y)

def create_worker_for_region(rx, ry):
	# 创建闭包函数,为特定区域生成worker
	def worker():
		worker_drone_with_region(rx, ry)
	return worker

def main():
	# 主流程 - 所有无人机在(0,0)生成,然后各自飞往目标区域
	
	# === 阶段1: 在(0,0)生成所有16架无人机 ===
	move_to(0, 0)
	
	drones = []
	
	# 定义16个区域的坐标(按距离从近到远排序,最远的是(24,24))
	# 索引0-15对应16个区域
	regions = [
		(0, 0),   (8, 0),   (16, 0),  (24, 0),   # 行0
		(0, 8),   (8, 8),   (16, 8),  (24, 8),   # 行1
		(0, 16),  (8, 16),  (16, 16), (24, 16),  # 行2
		(0, 24),  (8, 24),  (16, 24), (24, 24)   # 行3 (24,24)是最远的
	]
	
	# 在(0,0)位置一次性生成所有16架无人机
	# 每架无人机通过闭包知道自己要去的区域坐标
	for idx in range(16):
		region_x, region_y = regions[idx]
		worker_func = create_worker_for_region(region_x, region_y)
		drone = spawn_drone(worker_func)
		
		if drone != None:
			drones.append(drone)
	
	# 此时所有无人机已生成,它们会立即开始移动到各自区域
	# 无人机0 → (0,0)   已在位置
	# 无人机1 → (8,0)   开始移动
	# 无人机2 → (16,0)  开始移动
	# ...
	# 无人机15 → (24,24) 开始移动(最远,需要最长时间)
	
	# === 阶段2: 等待一段时间,确保所有无人机到达位置 ===
	# 最远的无人机需要移动 24+24=48 步
	# 给予足够的缓冲时间
	wait_steps = 0
	while wait_steps < 10000:
		wait_steps = wait_steps + 1
	
	# === 阶段3: 创建迷宫 ===
	# 此时所有无人机应该都已到达各自区域的左下角
	# 它们正在等待迷宫生成(循环检测 get_entity_type())
	
	move_to(0, 0)
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, substance_needed)
	
	# 迷宫创建完成!
	# 所有子无人机会检测到 Entities.Hedge,跳出等待循环
	# 然后开始执行:
	#   1. explore_and_map_region() - 探索8x8区域地图
	#   2. find_treasure_in_region() - 循环寻找并收集宝藏
	
	# === 阶段4: 等待所有无人机完成任务 ===
	for drone in drones:
		wait_for(drone)
	
	# === 阶段5: 主无人机收尾 ===
	move_to(0, 0)
	if get_entity_type() == Entities.Treasure:
		harvest()

main()
	