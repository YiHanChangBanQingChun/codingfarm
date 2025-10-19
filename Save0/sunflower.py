def raxis(i, n=get_world_size()):

    return i // n, i % n





def move_to(x, y):

    n = get_world_size()

    nowx = get_pos_x()

    nowy = get_pos_y()

    diffx = x - nowx

    abs_diffx = abs(diffx)

    if abs_diffx > n // 2:

        if diffx >= 0:

            diffx = abs_diffx - n

        else:

            diffx = n - abs_diffx

    diffy = y - nowy

    abs_diffy = abs(diffy)

    if abs_diffy > n // 2:

        if diffy >= 0:

            diffy = abs_diffy - n

        else:

            diffy = n - abs_diffy

    if diffx >= 0:

        for _ in range(diffx):

            move(East)

    else:

        for _ in range(-diffx):

            move(West)

    if diffy >= 0:

        for _ in range(diffy):

            move(North)

    else:

        for _ in range(-diffy):

            move(South)





axis = []





def water_square():

    n = 16

    dx = get_pos_x() % 2

    dy = get_pos_y() % 2

    while True:

        for i in range(n**2 - 1, -1, -1):

            x, y = raxis(i, n)

            if x % 2 == 1:

                y = n - y - 1

            x += n * dx

            y += n * dy

            move_to(x, y)

            if x % 8 > 3 and get_water() < 0.7:

                use_item(Items.Water)

            elif get_water() < 0.2:

                use_item(Items.Water)





def plant_square():

    n = 8

    dx = get_pos_x() % 4

    dy = get_pos_y() % 4

    flower_num_t = {

        7: [],

        8: [],

        9: [],

        10: [],

        11: [],

        12: [],

        13: [],

        14: [],

        15: [],

    }

    for i in range(n**2):

        x, y = raxis(i, n)

        if x % 2 == 1:

            y = n - y - 1

        x += n * dx

        y += n * dy

        move_to(x, y)

        if get_entity_type() != Entities.Sunflower and get_entity_type() != None:

            while not can_harvest():

                use_item(Items.Fertilizer)

            harvest()

        if get_ground_type() != Grounds.Soil:

            till()

        if get_ground_type() == Grounds.Soil:

            plant(Entities.Sunflower)

        t = get_pos_x(), get_pos_y()

        flower_num_t[measure()].append(t)

    return flower_num_t





def harvest_square():

    global axis

    axis_t = axis

    for x, y in axis_t:

        move_to(x, y)

        while not can_harvest():

            use_item(Items.Fertilizer)

        harvest()

    return





def main():

    global axis

    for i in range(2):

        for j in range(2):

            move_to(1 - i, 1 - j)

            spawn_drone(water_square)

    while True:

        flower_num = []

        drones = []

        for i in range(4):

            for j in range(4):

                move_to(3 - i, 3 - j)

                drones.append(spawn_drone(plant_square))

        for i in drones:

            flower_num.append(wait_for(i))

        drones = []

        for i in range(15, 6, -1):

            for j in flower_num:

                axis = j[i]

                drones.append(spawn_drone(harvest_square))

            for j in drones:

                wait_for(j)

            drones = []





if __name__ == "__main__":
    clear()
    main()