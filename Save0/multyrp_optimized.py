from __builtins__ import *

# 多无人机迷宫寻宝 - 超高效策略
# 参考别人优化代码的核心思路:
# 1. 在5x5网格上部署25个无人机,守在固定位置等待宝箱
# 2. 无人机发现当前位置是宝箱时,直接在宝箱上创建新迷宫(不收割!)
# 3. 主无人机只负责检测measure()==None,然后创建新迷宫

# 全局配置
substance = 5 * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
target = 512000  # 目标Gold数量

def handle():
	# """无人机处理函数 - 守在固定位置等待宝箱# """
	while True:
		# 检查是否达到目标
		if num_items(Items.Gold) >= target:
			return
		
		# 检查当前位置是否是宝箱
		if get_entity_type() == Entities.Treasure:
			# 关键:在宝箱上直接创建新迷宫,不收割!
			use_item(Items.Weird_Substance, substance)
			
			# 重复多次确保迷宫生成成功(防止宝箱移动)
			for i in range(6):
				if get_entity_type() == Entities.Treasure:
					use_item(Items.Weird_Substance, substance)
					if i == 5:
						# 第6次还是宝箱,收割它
						harvest()
				else:
					# 已经不是宝箱了,说明迷宫生成成功
					break

def main():
	# """主函数# """
	print("=== 高效迷宫寻宝开始 ===")
	print("目标Gold数量:", target)
	
	# 设置世界大小为5x5(小世界,无人机覆盖更密集)
	set_world_size(5)
	
	print("每个迷宫需要Weird_Substance:", substance)
	
	# 初始化:在5x5网格上部署25个无人机
	print("部署25个无人机到5x5网格...")
	for _ in range(5):
		for j in range(5):
			spawn_drone(handle)
			move(East)
		move(North)
	
	print("无人机部署完成!")
	
	# 主无人机负责创建迷宫
	print("开始迷宫循环...")
	maze_count = 0
	
	while num_items(Items.Gold) < target:
		# 关键优化:使用measure()==None判断宝箱是否被找到
		# 如果measure()返回None,说明当前没有宝箱(被无人机找到并覆盖了)
		if measure() == None:
			# 创建新迷宫
			plant(Entities.Bush)
			use_item(Items.Weird_Substance, substance)
			maze_count = maze_count + 1
			
			if maze_count % 10 == 0:
				current_gold = num_items(Items.Gold)
				print("已创建", maze_count, "个迷宫, 当前Gold:", current_gold)
	
	print("=== 完成! ===")
	print("总共创建了", maze_count, "个迷宫")
	print("最终Gold数量:", num_items(Items.Gold))

# 执行主程序
if __name__ == "__main__":
	main()
	