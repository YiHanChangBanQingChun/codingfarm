from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区 ==========
# 仙人掌：两组，每组3列
cactus_group1 = [0, 1, 2]
cactus_group2 = [3, 4, 5]
# 其他作物
grass_columns = [6, 7]
tree_columns = [8, 9]
carrot_columns = [10, 11, 12]
sunflower_columns = [13, 14, 15, 16]  # 扩大向日葵区域
pumpkin_columns = [17, 18, 19, 20, 21]

# 恐龙配置：可自定义范围
DINO_WORLD_SIZE = 22  # 恐龙在 12x12 区域收集骨头
DINO_START_X = 0
DINO_START_Y = 0
	

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
	for c in cactus_group1:
		if x == c:
			return Entities.Cactus
	for c in cactus_group2:
		if x == c:
			return Entities.Cactus
	for c in grass_columns:
		if x == c:
			return Entities.Grass
	for c in tree_columns:
		if x == c:
			return Entities.Tree
	for c in carrot_columns:
		if x == c:
			return Entities.Carrot
	for c in sunflower_columns:
		if x == c:
			return Entities.Sunflower
	for c in pumpkin_columns:
		if x == c:
			return Entities.Pumpkin
	return Entities.Pumpkin


def is_cactus_column(x):
	for c in cactus_group1:
		if x == c:
			return True
	for c in cactus_group2:
		if x == c:
			return True
	return False


def sort_cactus_area(columns):
	# """排序指定的仙人掌列# """
	if not columns:
		return
	
	size = get_world_size()
	start_x = columns[0]
	end_x = columns[-1] + 1
	
	# 横向排序
	for y in range(size):
		changed = True
		while changed:
			changed = False
			for i in range(len(columns) - 1):
				x = columns[i]
				x_next = columns[i + 1]
				go_to(x, y)
				entity = get_entity_type()
				if entity == Entities.Cactus:
					current_size = measure()
					
					go_to(x_next, y)
					right_entity = get_entity_type()
					if right_entity == Entities.Cactus:
						right_size = measure()
						
						go_to(x, y)
						if current_size > right_size:
							if x_next == x + 1:
								swap(East)
							else:
								# 不相邻的话需要手动交换
								go_to(x_next, y)
								swap(West)
								go_to(x, y)
								swap(East)
							changed = True
	
	# 纵向排序
	for x in columns:
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
						
						go_to(x, y)
						if current_size > north_size:
							swap(North)
							changed = True


def check_cactus_mature(columns):
	# """检查指定列的仙人掌是否全部成熟# """
	for x in columns:
		for y in range(world_size):
			go_to(x, y)
			entity = get_entity_type()
			if entity == Entities.Cactus:
				if not can_harvest():
					return False
	return True


def harvest_cactus_chain(columns):
	# """从最小的仙人掌开始连锁收获# """
	if not columns:
		return False
	min_x = columns[0]
	go_to(min_x, 0)
	entity = get_entity_type()
	if entity == Entities.Cactus:
		if can_harvest():
			harvest()
			return True
	return False


def snake_path_harvest(start_x, end_x, start_y, end_y):
	# """蛇形路径收获指定区域（高效遍历）# """
	
	for y in range(start_y, end_y):
		if y % 2 == 0:
			# 偶数行：从西到东
			x = start_x
			while x < end_x:
				go_to(x, y)
				process_tile(x, y, None)
				x = x + 1
		else:
			# 奇数行：从东到西
			x = end_x - 1
			while x >= start_x:
				go_to(x, y)
				process_tile(x, y, None)
				x = x - 1


def process_tile(x, y, ready_sunflowers):
	# """处理单个格子的作物# """
	entity = get_entity_type()
	desired = target_crop(x)
	
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


def prepare_zone(start_x, end_x):
	# """初始化区域# """
	for y in range(world_size):
		for x in range(start_x, end_x):
			go_to(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			desired = target_crop(x)
			entity = get_entity_type()
			
			if entity == Entities.Dead_Pumpkin:
				harvest()
				plant(desired)
			elif entity == None:
				plant(desired)
			elif entity != desired:
				if can_harvest():
					harvest()
				plant(desired)
			
			if desired != Entities.Tree:
				if get_water() < 0.5:
					use_item(Items.Water)


# ========== 仙人掌专用工人 ==========
def cactus_worker(columns, hat):
	# """仙人掌专用工人# """
	change_hat(hat)
	
	# 初始化
	for x in columns:
		for y in range(world_size):
			go_to(x, y)
			if get_ground_type() != Grounds.Soil:
				till()
			entity = get_entity_type()
			if entity != Entities.Cactus:
				if entity:
					harvest()
				plant(Entities.Cactus)
			if get_water() < 0.5:
				use_item(Items.Water)
	
	# 主循环
	while True:
		if check_cactus_mature(columns):
			sort_cactus_area(columns)
			harvest_cactus_chain(columns)
			
			# 重新种植
			for x in columns:
				for y in range(world_size):
					go_to(x, y)
					entity = get_entity_type()
					if entity != Entities.Cactus:
						plant(Entities.Cactus)
					if get_water() < 0.5:
						use_item(Items.Water)
		else:
			# 维护
			for x in columns:
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


# ========== 恐龙骨头收集工人 ==========
def dinosaur_bone_collector():
	# """恐龙帽骨头收集专家 - 可配置范围的蛇形路径# """
	
	def maintain_tile():
		x = get_pos_x()
		if not is_cactus_column(x):
			desired = target_crop(x)
			entity = get_entity_type()
			
			if entity == desired or entity == Entities.Sunflower or entity == Entities.Carrot or entity == Entities.Pumpkin or entity == Entities.Tree or entity == Entities.Grass:
				if get_water() < 0.5:
					use_item(Items.Water)
			
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
		
		# 移动到起始位置
		while get_pos_y() > DINO_START_Y:
			move(South)
		while get_pos_x() > DINO_START_X:
			move(West)
		
		maintain_tile()
		
		# 蛇形覆盖配置的范围
		tail_full = False
		end_x = DINO_START_X + DINO_WORLD_SIZE
		end_y = DINO_START_Y + DINO_WORLD_SIZE
		
		for y in range(DINO_START_Y, end_y):
			if (y - DINO_START_Y) % 2 == 0:
				# 偶数行：向东
				while get_pos_x() < end_x - 1:
					result = move(East)
					if not result:
						tail_full = True
						break
					maintain_tile()
			else:
				# 奇数行：向西
				while get_pos_x() > DINO_START_X:
					result = move(West)
					if not result:
						tail_full = True
						break
					maintain_tile()
			
			if tail_full:
				break
			
			if y < end_y - 1:
				result = move(North)
				if not result:
					tail_full = True
					break
				maintain_tile()
		
		# 收获骨头
		change_hat(Hats.Gold_Hat)


# ========== 标准收获工人（使用蛇形路径）==========
def harvester_worker(start_x, end_x, hat):
	# """标准收获工人 - 使用高效蛇形路径# """
	change_hat(hat)
	prepare_zone(start_x, end_x)
	
	while True:
		snake_path_harvest(start_x, end_x, 0, world_size)


# ========== 16架无人机的工人函数 ==========
def worker_1():
	cactus_worker(cactus_group1, Hats.Gold_Hat)

def worker_2():
	cactus_worker(cactus_group2, Hats.Brown_Hat)

def worker_3():
	harvester_worker(6, 7, Hats.Green_Hat)

def worker_4():
	harvester_worker(7, 8, Hats.Straw_Hat)

def worker_5():
	harvester_worker(8, 9, Hats.Dinosaur_Hat)

def worker_6():
	harvester_worker(9, 10, Hats.Purple_Hat)

def worker_7():
	harvester_worker(10, 11, Hats.Carrot_Hat)

def worker_8():
	harvester_worker(11, 12, Hats.Sunflower_Hat)

def worker_9():
	harvester_worker(12, 14, Hats.Gold_Hat)

def worker_10():
	harvester_worker(14, 16, Hats.Brown_Hat)

def worker_11():
	harvester_worker(16, 17, Hats.Green_Hat)

def worker_12():
	harvester_worker(17, 18, Hats.Straw_Hat)

def worker_13():
	harvester_worker(18, 19, Hats.Dinosaur_Hat)

def worker_14():
	harvester_worker(19, 20, Hats.Purple_Hat)

def worker_15():
	# 恐龙骨头收集专家
	dinosaur_bone_collector()

def worker_16():
	# """最后一个工人：负责剩余列 + 全地图维护# """
	change_hat(Hats.Carrot_Hat)
	prepare_zone(20, world_size)
	
	while True:
		# 收获自己的区域
		snake_path_harvest(20, world_size, 0, world_size)
		
		# 全地图维护（跳过仙人掌）
		for y in range(world_size):
			for x in range(world_size):
				if not is_cactus_column(x):
					go_to(x, y)
					desired = target_crop(x)
					entity = get_entity_type()
					
					if entity == desired:
						if get_water() < 0.5:
							use_item(Items.Water)
						if num_items(Items.Fertilizer) > 50:
							use_item(Items.Fertilizer)
					elif entity == None or entity == Entities.Dead_Pumpkin:
						if entity == Entities.Dead_Pumpkin:
							harvest()
						plant(desired)
						if get_water() < 0.5:
							use_item(Items.Water)


# ========== 启动16架无人机 ==========
d1 = spawn_drone(worker_1)
d2 = spawn_drone(worker_2)
d3 = spawn_drone(worker_3)
d4 = spawn_drone(worker_4)
d5 = spawn_drone(worker_5)
d6 = spawn_drone(worker_6)
d7 = spawn_drone(worker_7)
d8 = spawn_drone(worker_8)
d9 = spawn_drone(worker_9)
d10 = spawn_drone(worker_10)
d11 = spawn_drone(worker_11)
d12 = spawn_drone(worker_12)
d13 = spawn_drone(worker_13)
d14 = spawn_drone(worker_14)
d15 = spawn_drone(worker_15)

if d1 and d2 and d3 and d4 and d5 and d6 and d7 and d8 and d9 and d10 and d11 and d12 and d13 and d14 and d15:
	worker_16()
else:
	worker_16()
	