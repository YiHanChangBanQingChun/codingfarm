from __builtins__ import *

# ========== 初始化 ==========
clear()

world_size = get_world_size()

# ========== 辅助函数 ==========

def go_to(x, y):
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def is_tree_position(x, y):
	# 树使用棋盘格模式种植（间隔种植，避免生长减速）
	# 只在偶数行偶数列种树
	return (x % 2 == 0) and (y % 2 == 0)

# ========== 主程序 ==========

# 阶段2：耕耘所有土地
for x in range(world_size):
	for y in range(world_size):
		go_to(x, y)
		if get_ground_type() != Grounds.Soil:
			till()

# 阶段1：收集初始木材（收获灌木）
while num_items(Items.Wood) < 15000:
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			if get_water() < 0.4:
					use_item(Items.Water)
			if get_entity_type() == Entities.Tree:
				if can_harvest():
					harvest()
					plant(Entities.Tree)
			else:
				plant(Entities.Tree)

# 阶段2：收集初始草地
while num_items(Items.Hay) < 15000:
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			if get_water() < 0.4:
					use_item(Items.Water)
			if get_entity_type() == Entities.Tree:
				harvest()
			if get_entity_type() == Entities.Grass:
				if can_harvest():
					harvest()
					plant(Entities.Grass)
			else:
				plant(Entities.Grass)


# 阶段3：收集初始胡萝卜
while num_items(Items.Carrot) < 15000:
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			if get_water() < 0.4:
					use_item(Items.Water)
			if get_entity_type() == Entities.Grass:
				harvest()
			if get_entity_type() == Entities.Carrot:
				if can_harvest():
					harvest()
					plant(Entities.Carrot)
			else:
				plant(Entities.Carrot)

# 主循环：智能种植管理
while True:
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			
			# 获取当前实体
			entity = get_entity_type()
			
			# 1. 收获成熟植物
			if can_harvest():
				harvest()
				entity = None
			
			# 2. 决定种什么
			# 优先级：树（棋盘格） > 胡萝卜（有木材时） > 南瓜（有胡萝卜时）
			if entity == None or entity == Entities.Dead_Pumpkin:
				# 树：棋盘格模式种植
				if is_tree_position(x, y):
					if entity != Entities.Tree and num_items(Items.Wood) > 0:
						plant(Entities.Tree)
						entity = Entities.Tree
				# 胡萝卜：如果木材充足且胡萝卜不足
				elif num_items(Items.Wood) > 5000 and num_items(Items.Carrot) < 5000:
					plant(Entities.Carrot)
					entity = Entities.Carrot
				# 南瓜：如果有胡萝卜
				elif num_items(Items.Carrot) > 5000:
					plant(Entities.Pumpkin)
					entity = Entities.Pumpkin
			
			# 3. 浇水（除了树）
			if entity == Entities.Carrot or entity == Entities.Pumpkin:
				if get_water() < 0.4:
					use_item(Items.Water)
			
			# 4. 随机施肥（70%概率）
			if entity == Entities.Carrot or entity == Entities.Pumpkin or entity == Entities.Tree:
				if num_items(Items.Fertilizer) > 0:
					if random() > 0.7:
						use_item(Items.Fertilizer)
			
			# 5. 治疗感染
			if entity:
				if num_items(Items.Weird_Substance) > 0:
					use_item(Items.Weird_Substance)