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



def main():

	n = 16
	n *= 2
	set_world_size(n)
	move_to(0, 0)
	change_hat(Hats.Dinosaur_Hat)
	while True:
		for i in range(n - 1):
			move(East)
		move(North)
		for i in range(n):
			if i % 2 == 0:
				for _ in range(n - 2):
					move(North)
			else:
				for _ in range(n - 2):
					move(South)
			move(West)
		flag = move(South)
		if not flag:
			change_hat(Hats.Wizard_Hat)
			move_to(0, 0)
			change_hat(Hats.Dinosaur_Hat)



if __name__ == "__main__":
	main()