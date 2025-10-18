from __builtins__ import *

clear()

world_size = get_world_size()

# ========== 配置区：设置每种作物种在哪些列 ==========
carrot_columns = [0]
sunflower_columns = [1, 2]
tree_columns = [3]
pumpkin_columns = [4, 5, 6, 7]


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
				clear()
				entity = None
			if entity != desired:
				if entity and can_harvest():
					harvest()
					entity = None
				elif entity:
					clear()
					entity = None
				plant(desired)
				entity = desired
			if desired != Entities.Tree and get_water() < 0.5:
				use_item(Items.Water)


def harvester_drone():
	size = get_world_size()
	while True:
		ready_sunflowers = []
		sunflower_count = 0
		
		for x in range(size):
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
						
				elif entity == Entities.Pumpkin:
					if can_harvest():
						harvest()
						
				elif entity == Entities.Dead_Pumpkin:
					harvest()
					entity = None
				
				if entity == None:
					plant(desired)
		
		if ready_sunflowers:
			best_petals = 0
			for petals, sx, sy in ready_sunflowers:
				if petals > best_petals:
					best_petals = petals
			
			for petals, sx, sy in ready_sunflowers:
				go_to(sx, sy)
				if can_harvest():
					harvest()
					
		size = get_world_size()


def planter_loop():
	while True:
		for x in range(world_size):
			for y in range(world_size):
				go_to(x, y)
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
					
				if desired == Entities.Tree:
					if get_water() < 0.75:
						use_item(Items.Water)
				else:
					if get_water() < 0.75:
						use_item(Items.Water)
						
					if num_items(Items.Fertilizer) > 10:
						use_item(Items.Fertilizer)


prepare_field()

drone = spawn_drone(harvester_drone)
if drone == None:
	harvester_drone()

planter_loop()