from __builtins__ import *

# ========== 初始化 ==========
clear()

# 检测世界大小
move(North)
world_size = 1
while move(North):
	world_size += 1

# 回到起点
while move(South):
	pass

# 配置：最左边1列种胡萝卜，其余全种南瓜
CARROT_COLS = 1
PUMPKIN_START = CARROT_COLS

# ========== 辅助函数 ==========

def go_to(x, y):
	"""移动到指定坐标"""
	while get_pos_x() < x:
		move(East)
	while get_pos_x() > x:
		move(West)
	while get_pos_y() < y:
		move(North)
	while get_pos_y() > y:
		move(South)

def till_all():
	"""耕耘整个农场"""
	for x in range(world_size):
		for y in range(world_size):
			go_to(x, y)
			till()

def harvest_and_plant_carrots():
	"""收获并重新种植胡萝卜区域"""
	for x in range(CARROT_COLS):
		for y in range(world_size):
			go_to(x, y)
			entity = get_entity_type()
			
			# 如果可以收获就收获
			if can_harvest():
				harvest()
				entity = None
			
			# 如果没有胡萝卜就种植
			if entity != Entities.Carrot:
				plant(Entities.Carrot)

def manage_pumpkin_field():
	"""管理南瓜区域 - 一次完整遍历"""
	for x in range(PUMPKIN_START, world_size):
		for y in range(world_size):
			go_to(x, y)
			entity = get_entity_type()
			
			# 处理空地或枯死的南瓜
			if entity == None or entity == Entities.Dead_Pumpkin:
				# 确保有胡萝卜才种植
				if num_items(Items.Carrot) > 0:
					plant(Entities.Pumpkin)
				continue
			
			# 收获成熟的南瓜
			if can_harvest():
				harvest()
				# 立即重新种植
				if num_items(Items.Carrot) > 0:
					plant(Entities.Pumpkin)
				continue
			
			# 对于正在生长的南瓜进行维护
			if entity == Entities.Pumpkin:
				# 保持水分充足
				if get_water() < 0.75:
					use_item(Items.Water)
				
				# 使用肥料加速生长
				if num_items(Items.Fertilizer) > 0:
					use_item(Items.Fertilizer)

def smart_cure_infections():
	"""智能治疗感染 - 只在必要时使用奇异物质"""
	# 如果没有奇异物质就不处理
	if num_items(Items.Weird_Substance) <= 0:
		return
	
	# 遍历南瓜区域,治疗感染的南瓜
	# 注意:使用奇异物质会影响相邻植物的感染状态
	# 策略:从边缘开始治疗,避免交叉感染
	for x in range(PUMPKIN_START, world_size):
		for y in range(world_size):
			go_to(x, y)
			
			# 只对南瓜使用奇异物质
			if get_entity_type() == Entities.Pumpkin:
				# 如果有奇异物质就使用(会切换感染状态)
				if num_items(Items.Weird_Substance) > 0:
					use_item(Items.Weird_Substance)

# ========== 主程序 ==========

# 初始化:耕耘所有土地
till_all()

# 种植初始胡萝卜
for x in range(CARROT_COLS):
	for y in range(world_size):
		go_to(x, y)
		plant(Entities.Carrot)

# 主循环
cycle = 0
while True:
	cycle += 1
	
	# 1. 收获并重新种植胡萝卜(持续生产)
	harvest_and_plant_carrots()
	
	# 2. 检查胡萝卜库存,如果太少就再收获一轮
	if num_items(Items.Carrot) < 5:
		harvest_and_plant_carrots()
	
	# 3. 管理南瓜区域(种植、收获、浇水、施肥)
	manage_pumpkin_field()
	
	# 4. 每3个周期治疗一次感染
	if cycle % 3 == 0:
		smart_cure_infections()