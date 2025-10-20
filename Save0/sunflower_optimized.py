from __builtins__ import *

def move_to(x, y):
    while get_pos_x() < x:
        move(East)
    while get_pos_x() > x:
        move(West)
    while get_pos_y() < y:
        move(North)
    while get_pos_y() > y:
        move(South)

def scan_column():
    x = get_pos_x()
    move_to(x, 0)
    
    # Initial planting phase
    for y in range(32):
        move_to(x, y)
        if get_ground_type() != Grounds.Soil:
            till()
        if get_entity_type() != Entities.Sunflower:
            plant(Entities.Sunflower)
    
    while True:
        max_petal = 0
        max_positions = []
        
        for y in range(32):
            move_to(x, y)
            entity = get_entity_type()
            if entity == Entities.Sunflower:
                petals = measure()
                if petals != None:
                    if petals > max_petal:
                        max_petal = petals
                        max_positions = [(x, y)]
                    elif petals == max_petal:
                        max_positions.append((x, y))
        
        if max_petal == 0:
            break
        
        for pos_x, pos_y in max_positions:
            move_to(pos_x, pos_y)
            while not can_harvest():
                use_item(Items.Fertilizer)
            harvest()
        
        if max_petal <= 7:
            break
    
    for y in range(32):
        move_to(x, y)
        if get_entity_type() != Entities.Sunflower:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Sunflower)

def main():
    clear()
    set_world_size(32)
    
    max_d = max_drones()
    
    # First run: spawn all drones for initial planting
    drones = []
    for x in range(max_d):
        move_to(x, 0)
        drone = spawn_drone(scan_column)
        if drone != None:
            drones.append(drone)
        # Give the drone a moment to read its position
        if x < max_d - 1:
            move(East)
    
    # Wait for all drones to complete initial planting
    for drone in drones:
        wait_for(drone)
    
    # Continuous harvesting loop
    while True:
        drones = []
        
        for x in range(max_d):
            move_to(x, 0)
            drone = spawn_drone(scan_column)
            if drone != None:
                drones.append(drone)
            if x < max_d - 1:
                move(East)
        
        for drone in drones:
            wait_for(drone)

main()
