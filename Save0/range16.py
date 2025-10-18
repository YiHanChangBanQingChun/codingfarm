from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：设置每种作物种在哪些列 ==========
cactus_columns = [0, 1, 2]
grass_columns = [3, 4]
tree_columns = [5, 6]
carrot_columns = [7, 8]
sunflower_columns = [9, 10]
pumpkin_columns = [11, 12, 13, 14, 15]


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
	col = x
	
	for c in grass_columns:
		if col == c:
			return Entities.Grass
	
	for c in cactus_columns:
		if col == c:
			return Entities.Cactus
	
	for c in tree_columns:
		if col == c:
			return Entities.Tree
	
	for c in carrot_columns:
		if col == c:
			return Entities.Carrot
	
	for c in sunflower_columns:
		if col == c:
			return Entities.Sunflower
	
	for c in pumpkin_columns:
		if col == c:
			return Entities.Pumpkin
	
	return Entities.Pumpkin


def is_cactus_column(x):
	for c in cactus_columns:
		if x == c:
			return True
	return False


def sort_cactus_area(start_x, end_x):
	size = get_world_size()
	
	# 横向排序：每一行从西到东递增
	for y in range(size):
		changed = True
		while changed:
			changed = False
			# 只在仙人掌列之间进行排序
			for x in range(start_x, end_x - 1):
				if is_cactus_column(x) and is_cactus_column(x + 1):
					go_to(x, y)
					entity = get_entity_type()
					if entity == Entities.Cactus:
						current_size = measure()
						right_size = measure(East)
						
						if current_size > right_size:
							swap(East)
							changed = True
	
	# 纵向排序：每一列从南到北递增
	for x in range(start_x, end_x):
		if is_cactus_column(x):
			changed = True
			while changed:
				changed = False
				for y in range(size - 1):
					go_to(x, y)
					entity = get_entity_type()
					if entity == Entities.Cactus:
						current_size = measure()
						north_size = measure(North)
						
						if current_size > north_size:
							swap(North)
							changed = True


def check_all_cactus_mature():
	for x in cactus_columns:
		for y in range(world_size):
			go_to(x, y)
			entity = get_entity_type()
			if entity == Entities.Cactus:
				if not can_harvest():
					return False
	return True


def harvest_cactus_chain():
	min_x = cactus_columns[0]
	go_to(min_x, 0)
	entity = get_entity_type()
	if entity == Entities.Cactus:
		if can_harvest():
			harvest()
			return True
	return False


def prepare_field():
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			if can_harvest():
				harvest()
			if get_ground_type() != Grounds.Soil:
				till()
			desired = target_crop(x)
			entity = get_entity_type()
			if entity == Entities.Dead_Pumpkin:
				harvest()
				entity = None
			if entity != desired:
				if entity:
					if can_harvest():
						harvest()
					else:
						harvest()
				plant(desired)
				entity = desired
			if desired != Entities.Tree:
				if get_water() < 0.5:
					use_item(Items.Water)


def harvester_zone(start_x, end_x):
	size = get_world_size()
	while True:
		ready_sunflowers = []
		sunflower_count = 0
		
		has_cactus = False
		for x in range(start_x, end_x):
			if is_cactus_column(x):
				has_cactus = True
				break
		
		if has_cactus:
			all_mature = True
			for x in range(start_x, end_x):
				if is_cactus_column(x):
					for y in range(size):
						go_to(x, y)
						entity = get_entity_type()
						if entity == Entities.Cactus:
							if not can_harvest():
								all_mature = False
								break
				if not all_mature:
					break
			
			if all_mature:
				sort_cactus_area(start_x, end_x)
				
				for x in range(start_x, end_x):
					if is_cactus_column(x):
						go_to(x, 0)
						entity = get_entity_type()
						if entity == Entities.Cactus:
							if can_harvest():
								harvest()
								break
		
		for x in range(start_x, end_x):
			for y in range(size):
				go_to(x, y)
				entity = get_entity_type()
				desired = target_crop(x)
				
				if entity == Entities.Sunflower:
					sunflower_count = sunflower_count + 1
					if can_harvest():
						petals = measure()
						ready_sunflowers.append((petals, x, y))
				
				elif entity == Entities.Cactus:
					pass
						
				elif entity == Entities.Tree:
					if can_harvest():
						harvest()
						plant(desired)
						
				elif entity == Entities.Carrot:
					if can_harvest():
						harvest()
						plant(desired)
				
				elif entity == Entities.Grass:
					if can_harvest():
						harvest()
						plant(desired)
						
				elif entity == Entities.Pumpkin:
					if can_harvest():
						harvest()
						plant(desired)
						
				elif entity == Entities.Dead_Pumpkin:
					plant(desired)
					
				elif entity == None:
					plant(desired)
		
		if ready_sunflowers:
			best_petals = 0
			for petals, sx, sy in ready_sunflowers:
				if petals > best_petals:
					best_petals = petals
					if can_harvest():
						harvest()
						plant(target_crop(sx))
			
			for petals, sx, sy in ready_sunflowers:
				go_to(sx, sy)
				entity = get_entity_type()
				if entity == Entities.Sunflower:
					if can_harvest():
						harvest()
						plant(target_crop(sx))


def planter_zone(start_x, end_x):
	size = get_world_size()
	while True:
		for x in range(start_x, end_x):
			for y in range(size):
				go_to(x, y)
				desired = target_crop(x)
				entity = get_entity_type()
				
				if entity == Entities.Dead_Pumpkin:
					if can_harvest():
						harvest()
					plant(desired)
					
				elif entity == None:
					if can_harvest():
						harvest()
					plant(desired)
					
				elif entity != desired:
					if can_harvest():
						harvest()
						plant(desired)
					else:
						harvest()
						plant(desired)
						
				elif entity == desired:
					if can_harvest():
						harvest()
					plant(desired)
					if desired == Entities.Tree:
						if get_water() < 0.75:
							use_item(Items.Water)
					else:
						if get_water() < 0.75:
							use_item(Items.Water)
							
						if num_items(Items.Fertilizer) > 20:
							use_item(Items.Fertilizer)


half = world_size / 2

# 8无人机优化：Worker 1专门负责仙人掌，其他均分剩余列
zone1_end = 3   # Worker 1: 列 0-2 (仙人掌专用)
zone2_end = 5   # Worker 2: 列 3-4 (草)
zone3_end = 7   # Worker 3: 列 5-6 (树)
zone4_end = 9   # Worker 4: 列 7-8 (胡萝卜)
zone5_end = 11  # Worker 5: 列 9-10 (向日葵)
zone6_end = 13  # Worker 6: 列 11-12 (南瓜)
zone7_end = 15  # Worker 7: 列 13-14 (南瓜)
# Worker 8: 列 15 (南瓜) + 全地图维护

def prepare_zone(start_x, end_x):
	for x in range(start_x, end_x):
		for y in range(world_size):
			go_to(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			desired = target_crop(x)
			entity = get_entity_type()
			
			if entity == Entities.Dead_Pumpkin:
				if can_harvest():
					harvest()
				plant(desired)
			elif entity == None:
				if can_harvest():
					harvest()
				plant(desired)
			elif entity != desired:
				if can_harvest():
					harvest()
				else:
					if can_harvest():
						harvest()
				plant(desired)
				
			if desired != Entities.Tree:
				if get_water() < 0.5:
					use_item(Items.Water)

def worker_1():
	change_hat(Hats.Gold_Hat)
	
	# 初始化仙人掌区域
	for x in cactus_columns:
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
	
	# 主循环：等待成熟 → 排序 → 收获 → 重新种植
	while True:
		# 检查是否所有仙人掌都成熟
		if check_all_cactus_mature():
			# 全部成熟，进行排序
			sort_cactus_area(0, 3)
			
			# 触发连锁收获
			harvest_cactus_chain()
			
			# 重新种植所有仙人掌
			for x in cactus_columns:
				for y in range(world_size):
					go_to(x, y)
					entity = get_entity_type()
					if entity != Entities.Cactus:
						plant(Entities.Cactus)
					if get_water() < 0.5:
						use_item(Items.Water)
		else:
			# 维护：浇水、补种
			for x in cactus_columns:
				for y in range(world_size):
					go_to(x, y)
					entity = get_entity_type()
					
					if entity == Entities.Cactus:
						if get_water() < 0.5:
							use_item(Items.Water)
					elif entity == None:
						plant(Entities.Cactus)
						if get_water() < 0.5:
							use_item(Items.Water)

def worker_2():
	change_hat(Hats.Brown_Hat)
	prepare_zone(zone1_end, zone2_end)
	harvester_zone(zone1_end, zone2_end)

def worker_3():
	change_hat(Hats.Green_Hat)
	prepare_zone(zone2_end, zone3_end)
	harvester_zone(zone2_end, zone3_end)

def worker_4():
	change_hat(Hats.Straw_Hat)
	prepare_zone(zone3_end, zone4_end)
	harvester_zone(zone3_end, zone4_end)

def worker_5():
	change_hat(Hats.Dinosaur_Hat)
	prepare_zone(zone4_end, zone5_end)
	harvester_zone(zone4_end, zone5_end)

def worker_6():
	change_hat(Hats.Purple_Hat)
	prepare_zone(zone5_end, zone6_end)
	harvester_zone(zone5_end, zone6_end)

def worker_7():
	change_hat(Hats.Carrot_Hat)
	prepare_zone(zone6_end, zone7_end)
	harvester_zone(zone6_end, zone7_end)

def worker_8():
	change_hat(Hats.Sunflower_Hat)
	
	# 先准备自己的区域
	prepare_zone(zone7_end, world_size)
	
	# 然后进入混合模式：收获自己的区域 + 全地图维护
	while True:
		# 收获自己的区域 (列 15)
		for x in range(zone7_end, world_size):
			for y in range(world_size):
				go_to(x, y)
				entity = get_entity_type()
				desired = target_crop(x)
				
				if entity == Entities.Pumpkin:
					if can_harvest():
						harvest()
						plant(desired)
				elif entity == Entities.Dead_Pumpkin:
					plant(desired)
				elif entity == None:
					plant(desired)
		
		# 全地图浇水施肥维护（跳过仙人掌列，由Worker 1专门处理）
		for x in range(world_size):
			if not is_cactus_column(x):
				for y in range(world_size):
					go_to(x, y)
					desired = target_crop(x)
					entity = get_entity_type()
					
					if entity == desired:
						if get_water() < 0.5:
							use_item(Items.Water)
						if num_items(Items.Fertilizer) > 30:
							use_item(Items.Fertilizer)
						if can_harvest():
							harvest()
							plant(desired)
							if get_water() < 0.5:
								use_item(Items.Water)
					
					elif entity == None or entity == Entities.Dead_Pumpkin:
						if entity == Entities.Dead_Pumpkin:
							harvest()
						plant(desired)
						if get_water() < 0.5:
							use_item(Items.Water)


drone1 = spawn_drone(worker_1)
drone2 = spawn_drone(worker_2)
drone3 = spawn_drone(worker_3)
drone4 = spawn_drone(worker_4)
drone5 = spawn_drone(worker_5)
drone6 = spawn_drone(worker_6)
drone7 = spawn_drone(worker_7)

if drone1 and drone2 and drone3 and drone4 and drone5 and drone6 and drone7:
	worker_8()
else:
	worker_8()
	