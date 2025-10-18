from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：混合种植专用 ==========
# 主要种植这4种有伴生需求的作物
# 按列分配：草、灌木、树、胡萝卜混合种植
grass_columns = [0, 1, 4, 5, 8, 9, 12, 13]
bush_columns = [2, 6, 10, 14]
tree_columns = [3, 7, 11, 15]
carrot_columns = []

# 动态填充剩余列为胡萝卜
for x in range(world_size):
	is_assigned = False
	for c in grass_columns:
		if x == c:
			is_assigned = True
			break
	if not is_assigned:
		for c in bush_columns:
			if x == c:
				is_assigned = True
				break
	if not is_assigned:
		for c in tree_columns:
			if x == c:
				is_assigned = True
				break
	if not is_assigned:
		carrot_columns.append(x)

# 用于存储每个位置的伴生需求
companion_map = {}
zone1_end = 4
zone2_end = 8
zone3_end = 12


def go_to(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)


def target_crop(x):
	# """根据列号返回该列应种植的作物"""
	for c in grass_columns:
		if x == c:
			return Entities.Grass
	for c in bush_columns:
		if x == c:
			return Entities.Bush
	for c in tree_columns:
		if x == c:
			return Entities.Tree
	for c in carrot_columns:
		if x == c:
			return Entities.Carrot
	return Entities.Carrot


def is_companion_crop(entity):
	# """检查是否是有伴生需求的作物"""
	if entity == Entities.Grass:
		return True
	if entity == Entities.Bush:
		return True
	if entity == Entities.Tree:
		return True
	if entity == Entities.Carrot:
		return True
	return False


def is_valid_pos(x, y):
	# """检查坐标是否在地图内"""
	if x < 0 or x >= world_size:
		return False
	if y < 0 or y >= world_size:
		return False
	return True


def initialize_field():
	# """初始化农田：按列配置种植作物"""
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			
			desired = target_crop(x)
			plant(desired)
			
			if get_water() < 0.5:
				use_item(Items.Water)


def scan_companions():
	# """扫描所有作物的伴生需求"""
	companion_map.clear()
	
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			entity = get_entity_type()
			
			if is_companion_crop(entity):
				companion_info = get_companion()
				if companion_info:
					companion_type, companion_pos = companion_info
					cx, cy = companion_pos
					
					if is_valid_pos(cx, cy):
						key = str(cx) + "," + str(cy)
						if key not in companion_map:
							companion_map[key] = []
						companion_map[key].append((x, y, companion_type))


def optimize_companions():
	# """根据伴生需求优化种植"""
	scan_companions()
	
	for key in companion_map:
		parts = key.split(",")
		target_x = int(parts[0])
		target_y = int(parts[1])
		
		if not is_valid_pos(target_x, target_y):
			continue
		
		requests = companion_map[key]
		
		type_counts = {}
		for req_x, req_y, req_type in requests:
			if req_type not in type_counts:
				type_counts[req_type] = 0
			type_counts[req_type] = type_counts[req_type] + 1
		
		best_type = None
		best_count = 0
		for crop_type in type_counts:
			if type_counts[crop_type] > best_count:
				best_count = type_counts[crop_type]
				best_type = crop_type
		
		if best_type:
			go_to(target_x, target_y)
			current = get_entity_type()
			
			if current != best_type:
				if current:
					if can_harvest():
						harvest()
					else:
						harvest()
				plant(best_type)
				
				if get_water() < 0.5:
					use_item(Items.Water)


def harvester_zone(start_x, end_x):
	# """收获区域内成熟作物并重新种植"""
	size = get_world_size()
	while True:
		for x in range(start_x, end_x):
			for y in range(size):
				go_to(x, y)
				entity = get_entity_type()
				desired = target_crop(x)
				
				if is_companion_crop(entity):
					if can_harvest():
						harvest()
						plant(desired)
						
						if get_water() < 0.5:
							use_item(Items.Water)
				
				elif entity == None:
					plant(desired)
					if get_water() < 0.5:
						use_item(Items.Water)
				
				elif entity != desired:
					if can_harvest():
						harvest()
					else:
						harvest()
					plant(desired)
					if get_water() < 0.5:
						use_item(Items.Water)


def prepare_zone(start_x, end_x):
	# """准备区域：确保所有位置种植正确作物"""
	for x in range(start_x, end_x):
		for y in range(world_size):
			go_to(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			desired = target_crop(x)
			entity = get_entity_type()
			
			if entity != desired:
				if entity:
					if can_harvest():
						harvest()
					else:
						harvest()
				plant(desired)
			
			if get_water() < 0.5:
				use_item(Items.Water)


def worker_1():
	change_hat(Hats.Gold_Hat)
	prepare_zone(0, zone1_end)
	harvester_zone(0, zone1_end)


def worker_2():
	change_hat(Hats.Brown_Hat)
	prepare_zone(zone1_end, zone2_end)
	harvester_zone(zone1_end, zone2_end)


def worker_3():
	change_hat(Hats.Green_Hat)
	prepare_zone(zone2_end, zone3_end)
	harvester_zone(zone2_end, zone3_end)


def worker_4():
	change_hat(Hats.Sunflower_Hat)
	
	cycle = 0
	while True:
		cycle = cycle + 1
		
		if cycle % 3 == 0:
			optimize_companions()
		
		for x in range(world_size):
			for y in range(world_size):
				go_to(x, y)
				entity = get_entity_type()
				
				if entity:
					if get_water() < 0.5:
						use_item(Items.Water)
					
					if num_items(Items.Fertilizer) > 30:
						use_item(Items.Fertilizer)


drone1 = spawn_drone(worker_1)
drone2 = spawn_drone(worker_2)
drone3 = spawn_drone(worker_3)

if drone1 and drone2 and drone3:
	worker_4()
else:
	worker_4()
	