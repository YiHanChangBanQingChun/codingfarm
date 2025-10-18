from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：设置每种作物种在哪些列 ==========
grass_columns = [3]
cactus_columns = [0, 1, 2]
tree_columns = [4]
carrot_columns = [5, 6]
sunflower_columns = [7, 8]
pumpkin_columns = [9, 10, 11]


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
						right_size = measure(East)
						
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
						north_size = measure(North)
						
						if current_size > north_size:
							swap(North)
							changed = True


def prepare_field():
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
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
						
				elif entity == Entities.Carrot:
					if can_harvest():
						harvest()
				
				elif entity == Entities.Grass:
					if can_harvest():
						harvest()
						
				elif entity == Entities.Pumpkin:
					if can_harvest():
						harvest()
						
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
third_1 = world_size / 3
third_2 = third_1 * 2

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
	prepare_zone(0, third_1)
	harvester_zone(0, third_1)

def worker_2():
	prepare_zone(third_1, third_2)
	harvester_zone(third_1, third_2)

def worker_3():
	prepare_zone(third_2, world_size)
	harvester_zone(third_2, world_size)

def worker_4():
	while True:
		for x in range(world_size):
			for y in range(world_size):
				go_to(x, y)
				desired = target_crop(x)
				entity = get_entity_type()
				
				if entity == desired:
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
	