from __builtins__ import *

# 优化的迷宫导航 - 重复使用迷宫,记忆路径
# 核心思路:
# 1. 创建一个迷宫后,不断重复使用(最多300次)
# 2. 找到宝箱后,用use_item()让宝箱移动到新位置
# 3. 利用之前探索的路径信息,更快找到新宝箱位置
pet_the_piggy()
clear()

world_size = get_world_size()
maze_unlocks = max(1, num_unlocked(Unlocks.Mazes))
maze_scale = 2 ** (maze_unlocks - 1)
substance_needed = world_size * maze_scale

# 创建迷宫
plant(Entities.Bush)
use_item(Items.Weird_Substance, substance_needed)

# 全局方向定义
directions = [North, East, South, West]
offsets = {
    North: (0, 1),
    East: (1, 0),
    South: (0, -1),
    West: (-1, 0),
}
opposite = {North: South, South: North, East: West, West: East}

# 全局已访问路径 - 跨越多次寻宝保留
global_visited = {}
global_visited[(get_pos_x(), get_pos_y())] = True

def manhattan_distance(x1, y1, x2, y2):
    # """计算曼哈顿距离# """
    dx = x1 - x2
    dy = y1 - y2
    if dx < 0:
        dx = -dx
    if dy < 0:
        dy = -dy
    return dx + dy

def find_treasure():
    # """寻找宝箱 - 使用A*算法,利用global_visited的路径记忆# """
    target_x, target_y = measure()
    
    # 本次搜索的路径栈
    path = []
    
    # 本次搜索的局部visited(避免在本次搜索中重复访问)
    local_visited = {}
    current_pos = (get_pos_x(), get_pos_y())
    local_visited[current_pos] = True
    
    def get_best_direction():
        # """返回朝向目标的最佳方向(优先未全局访问过的,但也接受访问过的)# """
        best_dir = None
        best_dist = 999999
        best_dir_visited = None
        best_dist_visited = 999999
        
        current_x = get_pos_x()
        current_y = get_pos_y()
        
        for direction in directions:
            if not can_move(direction):
                continue
            
            dx, dy = offsets[direction]
            next_x = current_x + dx
            next_y = current_y + dy
            next_pos = (next_x, next_y)
            
            # 本次搜索已经访问过的不要重复
            if next_pos in local_visited:
                continue
            
            # 计算到目标的曼哈顿距离
            dist = manhattan_distance(next_x, next_y, target_x, target_y)
            
            # 如果是未全局访问的位置,优先选择
            if next_pos not in global_visited:
                if dist < best_dist:
                    best_dist = dist
                    best_dir = direction
            else:
                # 已全局访问的位置作为备选
                if dist < best_dist_visited:
                    best_dist_visited = dist
                    best_dir_visited = direction
        
        # 优先返回未访问的,如果没有就返回已访问的(利用已知路径)
        if best_dir:
            return best_dir, False  # 未访问的路径
        else:
            return best_dir_visited, True  # 已访问的路径
    
    max_steps = world_size * world_size * 10
    steps = 0
    
    while steps < max_steps:
        steps = steps + 1
        
        if get_entity_type() == Entities.Treasure:
            return True
        
        # 优先选择朝向目标的方向
        result = get_best_direction()
        if result:
            best_dir, is_revisit = result
        else:
            best_dir = None
            is_revisit = False
        
        moved = False
        if best_dir:
            dx, dy = offsets[best_dir]
            current_x = get_pos_x()
            current_y = get_pos_y()
            next_pos = (current_x + dx, current_y + dy)
            move(best_dir)
            path.append(best_dir)
            local_visited[next_pos] = True
            # 只记录新探索的路径到全局
            if not is_revisit:
                global_visited[next_pos] = True
            moved = True
        else:
            # 没有任何可行方向,尝试任意未本次访问的方向
            for direction in directions:
                if not can_move(direction):
                    continue
                dx, dy = offsets[direction]
                current_x = get_pos_x()
                current_y = get_pos_y()
                next_pos = (current_x + dx, current_y + dy)
                if next_pos in local_visited:
                    continue
                move(direction)
                path.append(direction)
                local_visited[next_pos] = True
                if next_pos not in global_visited:
                    global_visited[next_pos] = True
                moved = True
                break
        
        # 无法前进,需要回退
        if not moved:
            if not path:
                return False
            back_direction = opposite[path.pop()]
            move(back_direction)
    
    return False

# 主循环 - 重复使用迷宫最多300次
max_reuses = 300
treasure_count = 0

while treasure_count < max_reuses:
    # 获取当前宝箱位置
    treasure_pos = measure()
    if treasure_pos == None:
        break
    
    target_x, target_y = treasure_pos
    current_x = get_pos_x()
    current_y = get_pos_y()
    
    # 寻找宝箱
    found = find_treasure()
    
    if not found:
        break
    
    # 确认找到宝箱
    if get_entity_type() != Entities.Treasure:
        break
    
    treasure_count = treasure_count + 1

    # 关键:检查是否是最后一次
    if treasure_count >= max_reuses:
        harvest()
        break
    else:
        use_item(Items.Weird_Substance, substance_needed)
        # print("已探索路径数:", len(global_visited))
        # print()
