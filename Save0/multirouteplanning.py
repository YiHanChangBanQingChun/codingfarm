from __builtins__ import *

def run_maze_treasure_hunt():
    single_drone_mode = False

    if single_drone_mode:
        target_gold = 616448
        set_world_size(8)
    else:
        target_gold = 9863168
        set_world_size(32)

    clear()

    initial_gold = num_items(Items.Gold)

    # set_world_size(8)
    world_size = get_world_size()
    maze_unlocks = max(1, num_unlocked(Unlocks.Mazes))
    maze_scale = 2 ** (maze_unlocks - 1)
    substance_needed = world_size * maze_scale

    plant(Entities.Bush)
    use_item(Items.Weird_Substance, substance_needed)

    directions = [North, East, South, West]
    offsets = {
        North: (0, 1),
        East: (1, 0),
        South: (0, -1),
        West: (-1, 0),
    }
    opposite = {North: South, South: North, East: West, West: East}

    global_visited = {}
    global_visited[(get_pos_x(), get_pos_y())] = True

    def manhattan_distance(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    def to_int(value):
        return value // 1

    def find_treasure():
        target_x, target_y = measure()
        
        path = []
        
        local_visited = {}
        current_pos = (get_pos_x(), get_pos_y())
        local_visited[current_pos] = True
        
        base_greedy = 50
        openness_factor = min(treasure_count / 30, 5.0)
        greedy_attempts = to_int(base_greedy * (1 + openness_factor))
        
        def get_best_direction(allow_revisit_for_greedy):
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
                
                if next_pos in local_visited:
                    continue
                
                dist = manhattan_distance(next_x, next_y, target_x, target_y)
                
                if allow_revisit_for_greedy:
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = direction
                else:
                    if next_pos not in global_visited:
                        if dist < best_dist:
                            best_dist = dist
                            best_dir = direction
                    else:
                        if dist < best_dist_visited:
                            best_dist_visited = dist
                            best_dir_visited = direction
            
            if best_dir:
                return best_dir, False
            else:
                return best_dir_visited, True
        
        max_steps = world_size * world_size * 10
        steps = 0
        last_distance = 999999
        greedy_stuck_count = 0
        greedy_extended = False
        
        while steps < max_steps:
            steps = steps + 1
            
            if get_entity_type() == Entities.Treasure:
                return True
            
            current_distance = manhattan_distance(get_pos_x(), get_pos_y(), target_x, target_y)
            
            if steps <= greedy_attempts:
                if current_distance < last_distance:
                    greedy_stuck_count = 0
                else:
                    greedy_stuck_count = greedy_stuck_count + 1
                
                if greedy_stuck_count > 5 and not greedy_extended:
                    greedy_extended = True
                
                last_distance = current_distance
            
            if greedy_extended and current_distance > 3:
                use_greedy = True
            elif steps <= greedy_attempts:
                use_greedy = True
            else:
                use_greedy = False
            
            result = get_best_direction(use_greedy)
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
                if not is_revisit:
                    global_visited[next_pos] = True
                moved = True
            else:
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
            
            if not moved:
                if not path:
                    return False
                back_direction = opposite[path.pop()]
                move(back_direction)
        
        return False
    
    max_reuses = 300
    treasure_count = 0
    base_refresh_interval = 15
    consecutive_immediate_finds = 0

    while treasure_count < max_reuses:
        treasure_count = treasure_count + 1
        if treasure_count < 80:
            refresh_interval = base_refresh_interval
        elif treasure_count < 160:
            refresh_interval = base_refresh_interval * 2
        else:
            refresh_interval = base_refresh_interval * 3
        
        if treasure_count > 0 and treasure_count % refresh_interval == 0:
            old_count = len(global_visited)
            current_pos = (get_pos_x(), get_pos_y())
            new_visited = {current_pos: True}
            count = 0
            for pos in global_visited:
                if count % 2 == 0:
                    new_visited[pos] = True
                count = count + 1
            global_visited = {}
            for pos in new_visited:
                global_visited[pos] = True
        
        treasure_pos = measure()
        if treasure_pos == None:
            break
        
        target_x, target_y = treasure_pos
        current_x = get_pos_x()
        current_y = get_pos_y()
        
        drone_pos_before = (get_pos_x(), get_pos_y())
        found = find_treasure()
        

        print(treasure_count)
        if treasure_count > 299:
            # print("Early exit to avoid overharvest")
            harvest()
            break
        

        
        if get_entity_type() != Entities.Treasure:
            break
        
        drone_pos_after = (get_pos_x(), get_pos_y())
        if drone_pos_before == drone_pos_after:
            consecutive_immediate_finds = consecutive_immediate_finds + 1
        else:
            consecutive_immediate_finds = 0
        
        if consecutive_immediate_finds >= 3:
            harvest()
            break

        use_item(Items.Weird_Substance, substance_needed)