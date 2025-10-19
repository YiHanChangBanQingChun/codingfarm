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

region_map = {}
treasure_found_count = 0
max_treasure_reuses = 300

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

def explore_region():
	# 第一阶段：遍历并映射8x8区域内所有可通行路径
	global region_map
	
	base_x = get_pos_x()
	base_y = get_pos_y()
	
	local_map = {}
	to_visit = [(base_x, base_y)]
	visited = {}
	visited[(base_x, base_y)] = True
	
	while to_visit:
		current_x, current_y = to_visit[0]
		to_visit_new = []
		for i in range(1, len(to_visit)):
			to_visit_new.append(to_visit[i])
		to_visit = to_visit_new
		
		if current_x < base_x or current_x >= base_x + region_size:
			continue
		if current_y < base_y or current_y >= base_y + region_size:
			continue
		
		curr_pos_x = get_pos_x()
		curr_pos_y = get_pos_y()
		
		while curr_pos_x < current_x:
			if can_move(East):
				move(East)
				curr_pos_x = get_pos_x()
			else:
				break
		
		while curr_pos_x > current_x:
			if can_move(West):
				move(West)
				curr_pos_x = get_pos_x()
			else:
				break
		
		while curr_pos_y < current_y:
			if can_move(North):
				move(North)
				curr_pos_y = get_pos_y()
			else:
				break
		
		while curr_pos_y > current_y:
			if can_move(South):
				move(South)
				curr_pos_y = get_pos_y()
			else:
				break
		
		if get_pos_x() != current_x or get_pos_y() != current_y:
			continue
		
		local_map[(current_x, current_y)] = True
		
		for direction in directions:
			if can_move(direction):
				dx, dy = offsets[direction]
				next_x = current_x + dx
				next_y = current_y + dy
				next_pos = (next_x, next_y)
				
				if next_pos not in visited:
					if next_x >= base_x and next_x < base_x + region_size:
						if next_y >= base_y and next_y < base_y + region_size:
							visited[next_pos] = True
							to_visit.append(next_pos)
	
	region_map = local_map
	
	while get_pos_x() != base_x or get_pos_y() != base_y:
		if get_pos_x() > base_x and can_move(West):
			move(West)
		elif get_pos_x() < base_x and can_move(East):
			move(East)
		elif get_pos_y() > base_y and can_move(South):
			move(South)
		elif get_pos_y() < base_y and can_move(North):
			move(North)
		else:
			break

def find_treasure_in_region():
	# 第二阶段：在本区域内寻找宝藏
	# 如果宝藏在本区域，则收集；否则等待其他区域处理
	global region_map, treasure_found_count
	
	base_x = get_pos_x()
	base_y = get_pos_y()
	
	consecutive_not_in_region = 0
	max_consecutive = 5
	
	while treasure_found_count < max_treasure_reuses:
		treasure_pos = measure()
		
		if treasure_pos == None:
			break
		
		target_x, target_y = treasure_pos
		
		if target_x < base_x or target_x >= base_x + region_size:
			consecutive_not_in_region = consecutive_not_in_region + 1
			if consecutive_not_in_region >= max_consecutive:
				break
			continue
		
		if target_y < base_y or target_y >= base_y + region_size:
			consecutive_not_in_region = consecutive_not_in_region + 1
			if consecutive_not_in_region >= max_consecutive:
				break
			continue
		
		consecutive_not_in_region = 0
		
		path = []
		local_visited = {}
		current_pos = (get_pos_x(), get_pos_y())
		local_visited[current_pos] = True
		
		found = False
		max_steps = 300
		steps = 0
		
		while steps < max_steps:
			steps = steps + 1
			
			if get_entity_type() == Entities.Treasure:
				found = True
				break
			
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
				
				if next_pos in local_visited:
					continue
				
				if next_pos not in region_map:
					continue
				
				dist = manhattan_distance(next_x, next_y, target_x, target_y)
				
				if dist < best_dist:
					best_dist = dist
					best_dir = direction
			
			if best_dir:
				dx, dy = offsets[best_dir]
				current_x = get_pos_x()
				current_y = get_pos_y()
				next_pos = (current_x + dx, current_y + dy)
				move(best_dir)
				path.append(best_dir)
				local_visited[next_pos] = True
			else:
				if not path:
					break
				back_direction = opposite[path[len(path) - 1]]
				path_new = []
				for i in range(len(path) - 1):
					path_new.append(path[i])
				path = path_new
				move(back_direction)
		
		if found and get_entity_type() == Entities.Treasure:
			while not can_harvest():
				use_item(Items.Fertilizer)
			harvest()
			treasure_found_count = treasure_found_count + 1
			
			if treasure_found_count >= max_treasure_reuses:
				break
			
			use_item(Items.Weird_Substance, substance_needed)
		
		while get_pos_x() != base_x or get_pos_y() != base_y:
			if get_pos_x() > base_x and can_move(West):
				move(West)
			elif get_pos_x() < base_x and can_move(East):
				move(East)
			elif get_pos_y() > base_y and can_move(South):
				move(South)
			elif get_pos_y() < base_y and can_move(North):
				move(North)
			else:
				break

def worker_drone():
	# 无人机工作流程：先探索区域地图，再寻找宝藏
	explore_region()
	find_treasure_in_region()

def main():
	# 移动到迷宫入口并创建迷宫
	move_to(0, 0)
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, substance_needed)
	
	# 生成16架无人机，分配到4x4区域网格
	drones = []
	for i in range(4):
		for j in range(4):
			x = i * region_size
			y = j * region_size
			
			while get_pos_x() < x:
				move(East)
			while get_pos_x() > x:
				move(West)
			while get_pos_y() < y:
				move(North)
			while get_pos_y() > y:
				move(South)
			
			drone = spawn_drone(worker_drone)
			if drone != None:
				drones.append(drone)
	
	# 等待所有无人机完成任务
	for drone in drones:
		wait_for(drone)
	
	# 主无人机回到原点收尾
	move_to(0, 0)
	if get_entity_type() == Entities.Treasure:
		harvest()

main()
	