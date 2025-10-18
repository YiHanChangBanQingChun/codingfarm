from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：设置每种作物种在哪些列 ==========
carrot_columns = [0]
sunflower_columns = [1, 4]
tree_columns = [3]
grass_columns = [2]
pumpkin_columns = [5, 6, 7]


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
	
	for c in carrot_columns:
		if col == c:
			return Entities.Carrot
	
	for c in sunflower_columns:
		if col == c:
			return Entities.Sunflower
	
	for c in tree_columns:
		if col == c:
			return Entities.Tree
	
	for c in grass_columns:
		if col == c:
			return Entities.Grass
	
	for c in pumpkin_columns:
		if col == c:
			return Entities.Pumpkin
	
	return Entities.Pumpkin


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
quarter_1 = world_size / 4
quarter_3 = quarter_1 + half

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
	prepare_zone(0, quarter_1)
	harvester_zone(0, quarter_1)

def worker_2():
	prepare_zone(quarter_1, half)
	harvester_zone(quarter_1, half)

def worker_3():
	prepare_zone(half, quarter_3)
	planter_zone(half, quarter_3)

def worker_4():
	prepare_zone(quarter_3, world_size)
	planter_zone(quarter_3, world_size)

drone1 = spawn_drone(worker_1)
drone2 = spawn_drone(worker_2)
drone3 = spawn_drone(worker_3)

if drone1 and drone2 and drone3:
	worker_4()
else:
	worker_4()
