from __builtins__ import *

# 清空农场，为自动化做准备
clear()

# --- 配置区域 ---
# 使用列表定义农场每一列的布局，可以轻松修改
# 草(grass), 胡萝卜(Carrot), 南瓜(Pumpkin), 树(Tree)
farm_layout = [
	Entities.Carrot,
	Entities.Pumpkin,
	Entities.Carrot,
	Entities.grass,
	Entities.Tree,
	Entities.Tree
]

world_size = get_world_size()

# --- 函数定义 ---

def needs_tilling(plant_type):
	# """检查作物是否需要耕地"""
	return plant_type == Entities.Carrot or plant_type == Entities.Pumpkin

def handle_tile(plant_type):
	# """处理单个地块：收获、浇水、种植"""
	if can_harvest():
		harvest()
	
	# 如果是需要耕地的作物，确保地块是耕地
	if needs_tilling(plant_type) and get_ground_type() != Grounds.Soil:
		till()

	plant(plant_type)
	
	# 如果土壤湿度低，则浇水
	if get_water() < 0.5:
		use_item(Items.Water)

def process_column(plant_type, direction):
	# """沿指定方向处理一整列"""
	for _ in range(world_size):
		handle_tile(plant_type)
		move(direction)

# --- 主逻辑 ---

# 初始耕地阶段：根据布局预先耕好需要的地块
for x in range(world_size):
	plant_type = farm_layout[x]
	if needs_tilling(plant_type):
		for y in range(world_size):
			if get_ground_type() != Grounds.Soil:
				till()
			move(North)
	# 移动到下一列的起点
	if x < world_size - 1:
		move(East)
		for _ in range(world_size):
			move(South)

# 无限循环，持续耕作
while True:
	for x in range(world_size):
		plant_type = farm_layout[x]
		
		# 根据列的奇偶性决定向上还是向下移动
		if x % 2 == 0: # 偶数序列 (0, 2, 4...)
			process_column(plant_type, North)
		else: # 奇数序列 (1, 3, 5...)
			process_column(plant_type, South)
		
		# 移动到下一列
		if x < world_size - 1:
			move(East)