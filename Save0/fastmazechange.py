# Maze - Optimized Version
ALL_DIRECTIONS = [North, South, East, West]


def opposite_direction(direction):
    if direction == North:
        return South
    elif direction == East:
        return West
    elif direction == South:
        return North
    elif direction == West:
        return East


def explore_option_iterative(start_direction):
    global ALL_DIRECTIONS
    if not move(start_direction):
        return False

    path_stack = [(start_direction, 0)]
    
    # 缓存金币检查,减少调用频率
    check_counter = 0
    should_continue = True

    while path_stack and should_continue:
        if get_entity_type() == Entities.Treasure:
            harvest()
            start_maze()
            return True
        
        # 每10步才检查一次金币数量
        check_counter += 1
        if check_counter >= 10:
            should_continue = num_items(Items.Gold) < 9863168000000
            check_counter = 0

        last_move_direction, next_dir_index = path_stack[-1]

        while next_dir_index < len(ALL_DIRECTIONS):
            explore_direction = ALL_DIRECTIONS[next_dir_index]

            path_stack[-1] = (last_move_direction, next_dir_index + 1)

            if opposite_direction(explore_direction) != last_move_direction:
                if move(explore_direction):
                    path_stack.append((explore_direction, 0))
                    break

            next_dir_index += 1

        if next_dir_index == len(ALL_DIRECTIONS):
            path_stack.pop()
            move(opposite_direction(last_move_direction))

    move(opposite_direction(start_direction))
    return False


def start_maze():
    plant(Entities.Bush)
    substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)


# 预计算所有无人机的方向顺序
def get_directions_for_drone(drone_id):
    directions = [North, South, East, West]
    
    if drone_id % 2:
        directions = directions[::-1]
    if drone_id % 3:
        directions[0], directions[1] = directions[1], directions[0]
    if drone_id % 5:
        directions[1], directions[3] = directions[3], directions[1]
    
    return directions


def search():
    global drone_id
    global ALL_DIRECTIONS

    # 用 quick_print 替代 do_a_flip,如果只是为了区分无人机的话
    # 如果 do_a_flip 有其他作用,保留原逻辑
    # for _ in range(drone_id):
    #     do_a_flip()

    while True:
        for direction in ALL_DIRECTIONS:
            if explore_option_iterative(direction):
                break


# 主程序
drone_id = 0
start_maze()

max_drone_count = max_drones()

# 预计算所有无人机的方向
drone_directions = {}
for i in range(max_drone_count):
    drone_directions[i] = get_directions_for_drone(i)

# 生成无人机
for i in range(max_drone_count):
    drone_id = i
    ALL_DIRECTIONS = drone_directions[i]
    spawn_drone(search)

# 主无人机使用 ID 0 的方向
drone_id = 0
ALL_DIRECTIONS = drone_directions[0]
search()


# For the "Recycling" and "Big Gold Farmer" achievements
def generate_maze():
    plant(Entities.Bush)
    substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)


def maze():
    while True:
        if num_drones() == 25:
            if get_entity_type() == Entities.Treasure:
                harvest()
            generate_maze()


clear()
set_world_size(5)
visited_positions = {}  # 使用字典替代列表,查找更快

while num_drones() < 26:
    pos_x = get_pos_x()
    pos_y = get_pos_y()
    current = (pos_x, pos_y)
    
    if current not in visited_positions:
        visited_positions[current] = True
        spawn_drone(maze)
        move(North)
    else:
        move(East)
        