def move_to(x, y):

	n = get_world_size()

	nowx = get_pos_x()

	nowy = get_pos_y()

	diffx = x - nowx

	diffy = y - nowy

	if diffx == 0 and diffy == 0:

		return

	if diffx != 0:

		abs_diffx = abs(diffx)

		if abs_diffx > n // 2:

			if diffx >= 0:

				diffx = abs_diffx - n

			else:

				diffx = n - abs_diffx

	if diffy != 0:

		abs_diffy = abs(diffy)

		if abs_diffy > n // 2:

			if diffy >= 0:

				diffy = abs_diffy - n

			else:

				diffy = n - abs_diffy

	if diffx > 0:

		for _ in range(diffx):

			move(East)

	elif diffx < 0:

		for _ in range(-diffx):

			move(West)

	if diffy > 0:

		for _ in range(diffy):

			move(North)

	elif diffy < 0:

		for _ in range(-diffy):

			move(South)





def plant_single():

	n = get_world_size()

	for i in range(n):

		if (

			get_entity_type() != Entities.Cactus

			and get_entity_type() != None

			and get_entity_type() != Entities.Dead_Pumpkin

		):

			while not can_harvest():

				if num_items(Items.Fertilizer) > 1:

					use_item(Items.Fertilizer)

				elif num_items(Items.Water) > 1:

					use_item(Items.Water)

			harvest()

		if get_ground_type() != Grounds.Soil:

			till()

		if get_ground_type() == Grounds.Soil:

			plant(Entities.Cactus)

		if i == n - 1:

			return

		move(North)

	return





def sort_col_single():

	n = get_world_size()

	x = get_pos_x()

	for i in range(n - 1):

		swapped = False

		for j in range(n - 2, i - 1, -1):

			move_to(x, j)

			if measure(North) < measure():

				swap(North)

				swapped = True

		if not swapped:

			return

	return





def sort_row_single():

	n = get_world_size()

	y = get_pos_y()

	for i in range(n - 1):

		swapped = False

		for j in range(n - 2, i - 1, -1):

			move_to(j, y)

			if measure(East) < measure():

				swap(East)

				swapped = True

		if not swapped:

			return

	return





def main():

	n = get_world_size()

	move_to(0, 0)

	while True:

		drones = []

		for i in range(n - 1):

			drones.append(spawn_drone(plant_single))

			move(East)

		plant_single()

		move_to(0, n - 1)

		for i in drones:

			wait_for(i)

		drones = []

		for i in range(n - 1):

			move_to(i, n - 1)

			drones.append(spawn_drone(sort_col_single))

		move_to(n - 1, n - 1)

		sort_col_single()

		move_to(n - 1, 0)

		for i in drones:

			wait_for(i)

		drones = []

		for i in range(n - 1):

			move_to(n - 1, i)

			drones.append(spawn_drone(sort_row_single))

		move_to(n - 1, n - 1)

		sort_row_single()

		move_to(0, 0)

		for i in drones:

			wait_for(i)

		harvest()





if __name__ == "__main__":

	main()