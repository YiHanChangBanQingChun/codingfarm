from __builtins__ import *

# Build a full-field maze and navigate it elegantly.
for _ in range(1000):
	print("Attempting maze run...", _ + 1)
	clear()

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


	def walk_wall_right(max_steps):
		# """Follow the right wall; bail out if we start looping."""
		dir_idx = 0
		visited_states = {}
		steps = 0

		def try_step(current_idx, delta):
			target_idx = (current_idx + delta) % 4
			move_dir = directions[target_idx]
			if can_move(move_dir):
				move(move_dir)
				return True, target_idx
			return False, current_idx

		while steps < max_steps:
			if get_entity_type() == Entities.Treasure:
				return True

			state = (get_pos_x(), get_pos_y(), dir_idx)
			if state in visited_states:
				break
			visited_states[state] = True

			success, dir_idx = try_step(dir_idx, 1)
			if success:
				steps += 1
				continue
			success, dir_idx = try_step(dir_idx, 0)
			if success:
				steps += 1
				continue
			success, dir_idx = try_step(dir_idx, -1)
			if success:
				steps += 1
				continue
			success, dir_idx = try_step(dir_idx, 2)
			if success:
				steps += 1
				continue

		return False


	def depth_first_search():
		# """Deterministic DFS that copes with loops."""
		start = (get_pos_x(), get_pos_y())
		visited = {start: True}
		path = []

		while True:
			if get_entity_type() == Entities.Treasure:
				return True

			moved = False
			for direction in directions:
				if not can_move(direction):
					continue
				dx, dy = offsets[direction]
				next_pos = (get_pos_x() + dx, get_pos_y() + dy)
				if next_pos in visited:
					continue
				move(direction)
				path.append(direction)
				visited[next_pos] = True
				moved = True
				break

			if moved:
				continue

			if not path:
				return False
			back_direction = opposite[path.pop()]
			move(back_direction)


	estimated_steps = world_size * world_size * 8
	reached_treasure = walk_wall_right(estimated_steps)
	if not reached_treasure:
		reached_treasure = depth_first_search()

	if reached_treasure and get_entity_type() == Entities.Treasure:
		harvest()