from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：设置每种作物种在哪些列 ==========
cactus_columns = [0, 1, 2]
grass_columns = [3, 4]
tree_columns = [5, 6]
carrot_columns = [7, 8]
sunflower_columns = [9, 10, 11]
pumpkin_columns = [12, 13, 14, 15]


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
	
	for y in range(size):
		changed = True
		while changed:
			changed = False
			for x in range(start_x, end_x - 1):
				if is_cactus_column(x) and is_cactus_column(x + 1):
					go_to(x, y)
					entity = get_entity_type()
					if entity == Entities.Cactus:
						current_size = measure()
						
						go_to(x + 1, y)
						right_entity = get_entity_type()
						if right_entity == Entities.Cactus:
							right_size = measure()
							
							# 只有两个都是仙人掌时才比较
							go_to(x, y)
							if current_size > right_size:
								swap(East)
								changed = True
	
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
						
						go_to(x, y + 1)
						north_entity = get_entity_type()
						if north_entity == Entities.Cactus:
							north_size = measure()
							
							# 只有两个都是仙人掌时才比较
							go_to(x, y)
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


def harvester_zone(start_x, end_x):
	size = get_world_size()
	while True:
		ready_sunflowers = []
		
		for x in range(start_x, end_x):
			for y in range(size):
				go_to(x, y)
				entity = get_entity_type()
				desired = target_crop(x)
				
				if entity == Entities.Sunflower:
					if can_harvest():
						petals = measure()
						ready_sunflowers.append((petals, x, y))
				
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
			
			for petals, sx, sy in ready_sunflowers:
				go_to(sx, sy)
				entity = get_entity_type()
				if entity == Entities.Sunflower:
					if can_harvest():
						harvest()
						plant(target_crop(sx))


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


# 恐龙帽专用函数
def dinosaur_bone_collector():
	# """恐龙帽骨头收集专家 - 使用简单的蛇形路径，同时维护农场"""
	
	def maintain_current_position():
		# 在当前位置进行维护（跳过仙人掌区域）
		x = get_pos_x()
		if not is_cactus_column(x):
			desired = target_crop(x)
			entity = get_entity_type()
			
			# 检查并浇水
			if entity == desired or entity == Entities.Sunflower or entity == Entities.Carrot or entity == Entities.Pumpkin or entity == Entities.Tree or entity == Entities.Grass:
				if get_water() < 0.5:
					use_item(Items.Water)
			
			# 收获和种植
			if entity == Entities.Sunflower:
				if can_harvest():
					harvest()
					plant(desired)
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
				harvest()
				plant(desired)
			elif entity == None:
				plant(desired)
	while True:
		change_hat(Hats.Dinosaur_Hat)
	
		# 移动到起始位置 (0, 0) - 不使用go_to避免尾巴阻挡
		while get_pos_y() > 0:
			move(South)
		while get_pos_x() > 0:
			move(West)
		
		# 维护起始位置
		maintain_current_position()
	
		# 蛇形覆盖：逐行遍历
		tail_full = False
		for y in range(world_size):
			if y % 2 == 0:
				# 偶数行：向东移动到尽头
				while get_pos_x() < world_size - 1:
					result = move(East)
					if not result:
						# 尾巴已满，跳出所有循环
						tail_full = True
						break
					# 每移动一步就维护当前位置
					maintain_current_position()
			else:
				# 奇数行：向西移动到尽头
				while get_pos_x() > 0:
					result = move(West)
					if not result:
						# 尾巴已满，跳出所有循环
						tail_full = True
						break
					# 每移动一步就维护当前位置
					maintain_current_position()
			
			# 如果尾巴已满，停止遍历
			if tail_full:
				break
		
			# 移动到下一行（除了最后一行）
			if y < world_size - 1:
				result = move(North)
				if not result:
					# 尾巴已满，跳出循环
					tail_full = True
					break
				# 移动后维护当前位置
				maintain_current_position()
		
		# 收获恐龙尾巴（切换帽子即可收获）
		change_hat(Hats.Gold_Hat)
		# while True 会自动重新开始下一轮

# 区域划分
# Worker 1: 列0-2 (仙人掌)
# Worker 2: 列3-4 (草)
# Worker 3: 列5-6 (树)
# Worker 4: 列7-8 (胡萝卜)
# Worker 5: 恐龙帽 (全地图骨头收集+维护)
# Worker 6: 列9-12 (向日葵+部分南瓜)
# Worker 7: 列13-14 (南瓜)
# Worker 8: 列15 (南瓜) + 全地图维护

zone1_end = 3
zone2_end = 5
zone3_end = 7
zone4_end = 9
zone5_end = 13  # 扩大 Worker 6 的范围，覆盖向日葵(9-10)和南瓜(11-12)
zone6_end = 15
zone7_end = 15


def worker_1():
	change_hat(Hats.Gold_Hat)
	
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
	
	while True:
		if check_all_cactus_mature():
			sort_cactus_area(0, 3)
			harvest_cactus_chain()
			
			for x in cactus_columns:
				for y in range(world_size):
					go_to(x, y)
					entity = get_entity_type()
					if entity != Entities.Cactus:
						plant(Entities.Cactus)
					if get_water() < 0.5:
						use_item(Items.Water)
		else:
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
	dinosaur_bone_collector()


def worker_6():
	# 负责向日葵(9-10)和南瓜(11-12)
	change_hat(Hats.Purple_Hat)
	prepare_zone(zone4_end, zone5_end)
	harvester_zone(zone4_end, zone5_end)


def worker_7():
	# 负责南瓜(13-14)
	change_hat(Hats.Carrot_Hat)
	prepare_zone(zone5_end, zone6_end)
	harvester_zone(zone5_end, zone6_end)


def worker_8():
	# 负责南瓜(15) + 全地图维护
	change_hat(Hats.Sunflower_Hat)
	
	prepare_zone(zone6_end, world_size)
	
	while True:
		for x in range(zone6_end, world_size):
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


# 启动8架无人机
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
	